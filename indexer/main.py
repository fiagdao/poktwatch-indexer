from pokt import PoktRPCDataProvider
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

rpc_url = "http://pocket:8081"
pokt_rpc = PoktRPCDataProvider(rpc_url)

quit_event = threading.Event()
signal.signal(signal.SIGTERM, lambda *_args: quit_event.set())

# allows threading functions to have return values
class Request(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def get_block_txs(height: int, retries: int = 20, per_page: int = 500):
    page = 1
    txs = []
    while retries > 0:
        try:
            block_txs = pokt_rpc.get_block_transactions(
                page=page, per_page=per_page, height=height)
            if (block_txs.txs == []):
                return txs
            else:
                txs.extend(block_txs.txs)
                page += 1

        except Exception as e:
            time.sleep(random.randint(3,7))
            print("block-txs failed", e)
            if retries < 0:
                raise (
                    "Out of retries getting block {} transactions page {}".format(
                        height, page
                    )
                )

    raise (
        "get_block_txs failed"
    )
    quit()

def upper(string: str):
    return string.upper()

def flatten_tx(tx: Transaction, RelaysToTokensMultiplier: int, timestamp):
    message_type = tx.tx_result.message_type
    if len(tx.tx_result.signer)>40:
        tx.tx_result.signer="invalid_signer"

    if len(tx.tx_result.recipient)>40:
        tx.tx_result.recipient="invalid_recipient"

    if message_type == "send":
        value = tx.stdTx.msg.value.amount
    elif message_type == "claim":
        value = tx.stdTx.msg.value.total_proofs * RelaysToTokensMultiplier
    else:
        value = 0
   
    # few edge cases with 0 fee transaction
    if len(tx.stdTx.fee) == 0:
        fee = 0
    else:
        fee = tx.stdTx.fee[0].amount

    return {
        "height": tx.height,
        "hash": tx.hash_,
        "index": tx.index,
        "result_code": tx.tx_result.code,
        "signer": tx.tx_result.signer,
        "recipient": tx.tx_result.recipient,
        "msg_type": tx.tx_result.message_type,
        "fee": fee,
        "memo": tx.stdTx.memo,
        "value": value,
        "timestamp": timestamp
    }

def flatten_pending_tx(raw_tx: str, RelaysToTokensMultiplier: int):
    res = os.popen('pocket util decode-tx {} false true'.format(raw_tx)).read()

    tx = json.loads(res, strict=False)

    if tx["type"] == "send":
        value = tx["msg"]["amount"]
    elif tx["type"] == "claim":
        value = tx["msg"]["total_proofs"] * RelaysToTokensMultiplier
    else:
        value = 0

    return {
        "height": -1,
        "hash": tx["hash"].upper(),
        "index": -1,
        "result_code": -1,
        "signer": tx["signer"].upper(),
        "recipient": tx["receiver"].upper(),
        "msg_type": tx["type"],
        "fee": int(tx["fee"][:5]),
        "memo": tx["memo"],
        "value": value,
        "timestamp": datetime.datetime.now()
    }

def update_mempool(retries: int):
    while retries > 0:
        try:
            unconfirmed_txs = requests.get("http://pocket:26657/unconfirmed_txs?limit=10000").json()
            print("got mempool", unconfirmed_txs)
            RelaysToTokensMultiplier = pokt_rpc.get_param(
                "RelaysToTokensMultiplier", height=0)
            print("got relays to tokens")
            flat_txs = [flatten_pending_tx(raw_tx, RelaysToTokensMultiplier) for raw_tx in unconfirmed_txs["result"]["txs"]]
            print("got flat_txs", flat_txs)
            Transaction.delete().where(Transaction.height == -1).execute()
            Transaction.insert_many(flat_txs).execute()
            print("inserted")
            return True
        except Exception as e:
            print("mempool failure", e)
            retries-=1
    return False


def update_pulse(height:int, retries:int):
    while retries>0:
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
            retries-=1

    return False

def sync_block(height: int, retries: int):
    while retries>0:
        try:
            block_txs = get_block_txs(height)
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
            print("created transactions, and block", height)
            Block.create(height=height, proposer=proposer, relays=relays,
                         txs=len(flat_txs), timestamp=timestamp)

            return True
        except Exception as e:
            time.sleep(random.randint(5,10))
            print(block, e)
            retries-=1

    return False


batch_size = int(sys.argv[1])
state_height = State[1].height
pokt_height = pokt_rpc.get_height()
batch_height = pokt_height - (pokt_height % batch_size)

for batch in range(state_height, batch_height, batch_size):
    print(State[1].height)

    if quit_event.is_set():
            print("safely shutting down")
            quit()
    with db.atomic() as transaction:  # Opens new transaction.
        try:
            threads = []
            for block in range(batch, batch + batch_size):
                print("starting block:", block)
                x = Request(target=sync_block, args=(block,10,))
                x.start()
                threads.append(x)

            for thread in threads:
                if thread.join() == False:
                    print("thread failed")
                    transaction.rollback()
                    raise ("thread failed")

        except:
            transaction.rollback()
            quit()

        print("increased state")
        state = State[1]
        state.height = batch + batch_size
        state.save()

        transaction.commit()

while True:
    print("main loop")
    time.sleep(5)
    state_height = State[1].height
    pokt_height = pokt_rpc.get_height()
    if state_height-1 == pokt_height:
        with db.atomic() as transaction:
            try:
                print("updating mempool")
                update_mempool(20)
                print("mempool has been updated")
            except Exception as e:
                print("failure", e)
                transaction.rollback()
                quit()

            transaction.commit()

    for block in range(state_height, pokt_height + 1):
        print(State[1].height)
        if quit_event.is_set():
            print("safely shutting down")
            quit()
        with db.atomic() as transaction:  # Opens new transaction.
            try:
                sync_block(block, 20)
                update_pulse(block, 20)
                print("finished pulse and block, updating mempool")
                update_mempool(20)
            except Exception as e:
                print(e)
                transaction.rollback()
                quit()

            print("increased state")

            transaction.commit()

        state = State[1]
        state.height = block+1
        state.save()


