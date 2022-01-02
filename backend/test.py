print("this is a test.py file and has been executed correctly")
print("sync file called")
import requests
import json
from tqdm import tqdm
import time
from models import *
from pokt import Pokt
import datetime
import dateutil
from dateutil.parser import *
headers = {"Content-Type": "application/json", "Accept": "Accept: application/json"}
node = Pokt('pocket:8081')
print("after POKT node init")
print("in sync file")
def ex(cmd):
        c.execute(cmd)

def blockInfo(block):
        # time.sleep(5)

        relays, height, time, txs, proposer = node.block(block)
        apps = node.app_count(block)
        nodes = node.node_count(block)
        if txs == 0:
                return False

        # ex(f'UPDATE pulse SET nodes={nodes}, apps={apps}')
        pulse = Pulse.get(id=0)
        pulse.nodes = nodes
        pulse.apps = apps
        pulse.save()

        Blocks.create(height=block, producer=proposer, relays=relays, txs=txs)
        # ex(f"INSERT INTO blocks VALUES ({block},'{blockProducer}',{relays},{txs})")

        return True


def syncBlock(block):
#       print("syncblock:",block)
        if block == 30024:
                return False
        block_time = node.block_time(block)

        start = time.time()

        while blockInfo(block)==False:
                print("node has not processed block", e)
                time.sleep(10)
        print(block)
        txs = node.block_txs(block)

        print("block txs", time.time()-start)
        block = time.time()
        slim_txs = []

        for tx in txs:
                x = node.strip_tx(tx)
                if x != None:
                        hash, receiver, sender, value, type, fee, height, index, code, memo, chain = node.strip_tx(tx)
                        slim_txs.append({"hash":hash, "receiver": receiver, "sender": sender, "value": value, "type": type, "fee": fee, "height": height, "index": index, "code": code, "memo": memo, "chain":chain, "timestamp": parse(block_time)})

        print("computation: ", time.time()-block)
        computation = time.time()

        if len(txs)>0:
                Transaction.insert_many(slim_txs).execute()
        print("insertion, ", time.time()-computation)
        print("total: ", time.time()-start)

print('live sync')

def syncMempool():
        query = Transaction.delete().where(Transaction.height==-1)

        raw_txs = node.mempool(100000)
        print("mempool: ", len(raw_txs))
        slim_txs = []

        for tx in raw_txs:
                hash, receiver, sender, value, type, fee, height, index, code, memo, chain = node.strip_raw_tx(tx)
                slim_txs.append({"hash":hash, "receiver": receiver, "sender": sender, "value": value, "type": type, "fee": fee, "height": height, "index": index, "code": code, "memo": memo, "chain":chain, "timestamp": datetime.datetime.now()})

        if len(raw_txs)>0:
                # print(slim_txs)
                query.execute()
                Transaction.insert_many(slim_txs).execute()

for i in range(100):
	print("while true loop")
	time.sleep(0.5)

print("exited")
