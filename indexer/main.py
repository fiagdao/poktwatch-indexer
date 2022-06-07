from pokt import PoktRPCDataProvider
from utils import *
from dateutil.parser import parse
from models import *
from threading import Thread
import sys
import signal
import threading
import time
import random
import os
import requests
import json
import datetime
import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[
                        logging.FileHandler("poktwatch.log"),
                        logging.StreamHandler()
                    ],
                    level=logging.INFO)

rpc_url = "http://pocket:8081"
pokt_rpc = PoktRPCDataProvider(rpc_url)

quit_event = threading.Event()
signal.signal(signal.SIGTERM, lambda *_args: quit_event.set())


def update_mempool(retries: int):
    """ get all transactions in the mempool and add them to the database

    retries - the number of times to allow for a failed request

    """
    while retries > 0:
        try:
            unconfirmed_txs = requests.get(
                "http://pocket:26657/unconfirmed_txs?limit=10000").json()
            RelaysToTokensMultiplier = pokt_rpc.get_param(
                "RelaysToTokensMultiplier", height=0)
            flat_txs = [flatten_pending_tx(
                raw_tx, RelaysToTokensMultiplier) for raw_tx in unconfirmed_txs["result"]["txs"]]
            Transaction.delete().where(Transaction.height == -1).execute()
            Transaction.insert_many(flat_txs).execute()
            return True
        except Exception as e:
            logging.warning(
                "Mempool failure. Error: {}. Retry-{}".format(e, retries))
            retries -= 1
    return False


def update_pulse(height: int, retries: int):
    """ update the Pulse section according to models.py

    height - the height to update pulse at
    retries - the allowance for an RPC request failure

    """
    while retries > 0:
        try:
            nodes = pokt_rpc.get_nodes(height=height, per_page=1).total_pages
            apps = pokt_rpc.get_apps(height=height, per_page=1).total_pages

            pulse = Pulse[1]
            pulse.nodes = nodes
            pulse.apps = apps
            pulse.save()

            return True
        except Exception as e:
            print(e)
            retries -= 1

    return False


def sync_block(height: int, retries: int):
    """ add all Transactions of a block and the Block to the database

    height - height to add
    retries - the number of times to retry an RPC request failure

    """

    while retries > 0:
        try:
            block_txs = get_block_txs(height, pokt_rpc)
            relays = 0
            for tx in block_txs:
                if tx.tx_result.message_type == "claim":
                    relays += tx.stdTx.msg.value.total_proofs

            RelaysToTokensMultiplier = pokt_rpc.get_param(
                "RelaysToTokensMultiplier", height=height)

            block_header = pokt_rpc.get_block(height).block.header
            timestamp = block_header.time
            proposer = block_header.proposer_address

            flat_txs = [flatten_tx(tx, RelaysToTokensMultiplier, timestamp)
                        for tx in block_txs]

            Transaction.insert_many(flat_txs).execute()
            Block.create(height=height, proposer=proposer, relays=relays,
                         txs=len(flat_txs), timestamp=timestamp)

            return True
        except Exception as e:
            time.sleep(random.randint(5, 10))
            print(block, e)
            retries -= 1

    return False


batch_size = int(sys.argv[1])
state_height = State[1].height
pokt_height = pokt_rpc.get_height()
batch_height = pokt_height - (pokt_height % batch_size)
for batch in range(state_height, batch_height, batch_size):
    """ for syncing early blocks on beefy machines, there is batching/threading functionality, which is a arg in the entrypoint.sh file. It is currently set to 1 for stability.


    """
    logging.info("Current height {}".format(State[1].height))

    if quit_event.is_set():
        logging.info("Safely shutting down")
        quit()
    with db.atomic() as transaction:  # Opens new transaction.
        try:
            threads = []
            for block in range(batch, batch + batch_size):
                logging.info("Starting block: {}".format(block))
                x = Request(target=sync_block, args=(block, 10,))
                x.start()
                threads.append(x)

            for thread in threads:
                if thread.join() == False:
                    logging.error("Thread failed, quitting")
                    transaction.rollback()
                    quit()

        except:
            transaction.rollback()
            quit()

        state = State[1]
        state.height = batch + batch_size
        state.save()

        transaction.commit()

while True:
    time.sleep(5)
    state_height = State[1].height
    pokt_height = pokt_rpc.get_height()
    if state_height - 1 == pokt_height:
        with db.atomic() as transaction:
            try:
                logging.info("Updating mempool")
                update_mempool(20)
                logging.info("Mempool has been successfully updated")
            except Exception as e:
                logging.error("Mempool update has failed {}".format(e))
                transaction.rollback()
                quit()

            transaction.commit()

    for block in range(state_height, pokt_height + 1):
        logging.info("Syncing block: {}".format(block))
        if quit_event.is_set():
            logging.info("Safely shutting down")
            quit()
        with db.atomic() as transaction:  # Opens new transaction.
            try:
                sync_block(block, 20)
                update_pulse(block, 20)
                update_mempool(20)
            except Exception as e:
                logging.error("Failure to sync block: {}".format(e))
                transaction.rollback()
                quit()

            logging.info("Successfully synced block {}".format(block))

            transaction.commit()

        state = State[1]
        state.height = block + 1
        state.save()
