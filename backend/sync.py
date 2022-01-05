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
print("in sync file")
# heightURL = 'http://localhost:8081/v1/query/height'
# tx = 'http://localhost:8081/v1/query/tx'
# blocktxs= 'http://localhost:8081/v1/query/blocktxs'
# nodesURL = 'http://localhost:8081/v1/query/nodes'
# appsURL = 'http://localhost:8081/v1/query/apps'
# blockURL = 'http://localhost:8081/v1/query/block'
#
# host='ec2-35-170-124-67.compute-1.amazonaws.com'
# database='dfj22uqqfkqbam'
# user='u8ubp48c0q5bhm'
# port=5432
# password='pdfa73ca4ff5e08f37c37d656332e303aa4e5f150734fb8b2c0b3fa344590f4e8'
#
# # connection = psycopg2.connect(user="ibclhcjiwsbxnn",host="ec2-3-221-100-217.compute-1.amazonaws.com",database="dbjcte3ojl6ska",password="be5454e4edab439fdc807a97252fffea1fe3917a76aabfbccd823b6239c6295f",port="5432")
# # connection = psycopg2.connect(user="ufo4f7au3ibjir",host="ec2-35-174-58-77.compute-1.amazonaws.com",database="dfj22uqqfkqbam",password="pb77af04be9db1ee75fca22da05007c7b4ce35d282059837afd8735c49b0a42c3",port="5432")
# connection = psycopg2.connect(user="u8ubp48c0q5bhm", database="dfj22uqqfkqbam", host="ec2-35-170-124-67.compute-1.amazonaws.com", password="pdfa73ca4ff5e08f37c37d656332e303aa4e5f150734fb8b2c0b3fa344590f4e8", port="5432")
#
# # connection =psycopg2.connect(database='Transaction')
# c = connection.cursor()
time.sleep(30)
node = Pokt('pocket:8081')
print(node.block_txs(1000),flush=True)
print("after POKT node init",flush=True)
def ex(cmd):
	c.execute(cmd)

def blockInfo(block):
	# time.sleep(5)
	print("blockInfostart", flush=True)
	relays, height, time, txs, proposer = node.block(block)
	print("app and node count", flush=True)
	apps = node.app_count(block)
	print("node count", flush=True)
	nodes = node.node_count(block)

	# ex(f'UPDATE pulse SET nodes={nodes}, apps={apps}')
	print("pulse shit", flush=True)
	pulse = Pulse.get(id=1)
	pulse.nodes = nodes
	pulse.apps = apps
	pulse.save()
	print("creating block", flush=True)
	Blocks.create(height=block, producer=proposer, relays=relays, txs=txs)
	# ex(f"INSERT INTO blocks VALUES ({block},'{blockProducer}',{relays},{txs})")

	return True


def syncBlock(block):
	print("syncblock:",block,flush=True)
	if block == 30024:
		return False
	print("attempting blocktime", flush=True)
	block_time = node.block_time(block)

	start = time.time()
	print("attempting blockinformation", flush=True)
	while blockInfo(block)==False:
	 	print("node has not processed block", flush=True)
	 	time.sleep(10)
	print(block,flush=True)
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


print('testing')
while True:
	print("while true",flush=True)
	currHeight = State[1].height
	tarHeight= node.height()
	print(currHeight,tarHeight,flush=True)
	if tarHeight > currHeight:
		if tarHeight-1==currHeight:
			syncMempool()
			time.sleep(20)
		else:
			pass
		print('about to sync block',flush=True)
		syncBlock(currHeight+1)
		print(f"{time.time()}      Success! Synced block: {currHeight+1}",flush=True)
		# time.sleep(0.01)
		# ex(f'UPDATE STATE SET height={currHeight+1}')
		state = State[1]
		state.height = currHeight+1
		state.save()
		# connection.commit(
			# time.sleep(30)
	else:
		# print(tarHeight, currHeight)
		#syncMempool()

		time.sleep(10)


