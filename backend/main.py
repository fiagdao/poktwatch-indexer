from pypocket.pokt import PoktRPCDataProvider
from dateutil.parser import parse
from models import *
from threading import Thread
import sys
import signal
import threading
import time
import random

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

    return {
        "height": tx.height,
        "hash": tx.hash_,
        "index": tx.index,
        "result_code": tx.tx_result.code,
        "signer": tx.tx_result.signer,
        "recipient": tx.tx_result.recipient,
        "msg_type": tx.tx_result.message_type,
        "fee": tx.stdTx.fee[0].amount,
        "memo": tx.stdTx.memo,
        "value": value,
        "timestamp": timestamp
    }

def update_pulse(height:int, retries:int):
    while retries>0:
        try:
            nodes = pokt_rpc.get_nodes(height=height, per_page=1).total_pages
            apps = pokt_rpc.get_apps(height=height, per_page=1).total_pages

            Pulse[1].nodes = nodes
            Pulse[1].apps = apps
            Pulse[1].save()

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

            state = State[1]
            state.height = batch + batch_size
            state.save()
        except:
            transaction.rollback()
            quit()
        transaction.commit()

while True:
    state_height = State[1].height
    pokt_height = pokt_rpc.get_height()

    for block in range(state_height, pokt_height + 1):
        if quit_event.is_set():
            print("safely shutting down")
            quit()
        with db.atomic() as transaction:  # Opens new transaction.
            try:
                sync_block(block, 20)
                update_pulse(block, 20)
            except:
                transaction.rollback()
                quit()
