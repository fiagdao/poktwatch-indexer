from django.shortcuts import redirect
from django.shortcuts import render
from django.core import serializers
from .models import Transactions, Pulse, Blocks
import requests
import json
import time
import math
import psycopg2
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


headers= {"Content-Type": "application/json", "Accept": "Accept: application/json"}

class poktNode:
		class url:
				pass
		def __init__(self, ip):
				self.headers= {"Content-Type": "application/json", "Accept": "Accept: application/json"}

				self.ip = "http://"+ip
				self.url.height=self.ip+"/v1/query/height"
				self.url.block=self.ip+"/v1/query/block"
				self.url.blocktxs=self.ip+"/v1/query/blocktxs"
				self.url.account=self.ip+"/v1/query/account"
				self.url.node=self.ip+"/v1/query/node"

		def getRelays(self,block):
			proofs =0
			txs = node.block_txs(block)

			# print(len(txs))
			for tx in txs:
				type = tx["tx_result"]["message_type"]

				if type=="claim":
					txproofs = tx["stdTx"]["msg"]["value"]["total_proofs"]
					proofs += int(txproofs)
			return proofs

		def block(self, blocknum):
			block = requests.post(url=self.url.block, data=json.dumps({"height": blocknum}), headers=headers).json()
			if "code" in block and block["code"]!=200:
				return True

			relays = self.getRelays(blocknum)
			print("got relays, rendering")

			height = block["block"]["header"]["height"]
			time = block["block"]["header"]["time"]
			txs = block["block"]["header"]["num_txs"]
			proposer = block["block"]["header"]["proposer_address"].lower()

			return relays, height, time, txs, proposer

		def block_txs(self, block):
			ret = requests.post(self.url.blocktxs, data=json.dumps({"height":block, "per_page":99999999}), headers=headers)
			data= ret.json()
			txs = data["txs"]
			return txs

		def height(self):
				height = requests.post(self.url.height,data=json.dumps({}),headers=self.headers).json()["height"]
				return height

		def addressbal(self, address):
			print("test")
			response = requests.post(url=self.url.account, data=json.dumps({"address": address}), headers=self.headers).json()
			if response == None:
				print("none")
				return 0
			elif "code" in response and response["code"]!=200:
				print("asdf")
				print(response)
				return None
			elif "coins" in response and len(response["coins"])>0:
				balance = round(int(response["coins"][0]["amount"])/1000000,3)
				print("returned balance")
				print(balance)
				return balance
			else:
				return 0

		def node_info(self, address, price):
			response = requests.post(url=self.url.node, data=json.dumps({"address": address}), headers=self.headers).json()

			if "message" in response:
				nodeBal=0
				jailed=""
				public_key=""
				nodeVal=0
			elif price != "N/A":
				nodeBal=round(int(response["tokens"])/1000000,3)
				jailed = response["jailed"]
				public_key = response["public_key"]
				nodeVal = round(nodeBal*price,2)
			else:
				nodeBal=round(int(response["tokens"])/1000000,3)
				jailed = response["jailed"]
				public_key = response["public_key"]
				nodeVal = "N/A"

			return nodeBal, jailed, public_key, nodeVal
node = poktNode(ip='pocket:8081')

def get_price():
	try:
		price= round(float(requests.get('https://api.coingecko.com/api/v3/simple/price?ids=pocket-network&vs_currencies=usd').json()["pocket-network"]["usd"]),2)
	except:
		price = "N/A"
	return price

# Create your views here.
def index(request):
	print('started')
	# print("price")
	price = get_price()
	print("price")
	height = node.height()
	print("height")

	txs = Transactions.objects.all().order_by('-height')[:10]
	print("txs")

	blocks = Blocks.objects.all().order_by('-id')[:10]
	print("blocks")

	# pulse = Pulse.objects.get(height=height)
	pulse = Pulse.objects.all()[0]

	print('got txs, rendering')
	# print(txs)
	return render(request,"index.html", {
	"txs": txs,
	"price": price,
	"height": height,
	"numOfBlocks": [0,1,2,3,4,5,6,7,8,9],
	"nodes":pulse.nodes,
	"apps": pulse.apps,
	"blocks":blocks
	})

def tx(request, hash):
	hash = hash.upper()
	price = get_price()

	start = time.time()
	print('starting')
	print(f"SELECT * FROM Transactions WHERE hash='{hash}' LIMIT 1")
	try:
		tx= Transactions.objects.raw(f"SELECT * FROM Transactions WHERE hash='{hash}' LIMIT 1")
		_ = tx[0]
	except Exception as e:
		print(e)
		return render(request,"failedQuery.html")


	print('got tx, RENDERING',time.time()-start)

	print(tx[0].sender)

	return render(request,"tx.html", {
	"hash": tx[0].hash,
	"receiver": tx[0].receiver,
	"sender": tx[0].sender,
	"value": tx[0].value,
	"type": tx[0].type,
	"fee": tx[0].fee,
	"height": tx[0].height,
	"index": tx[0].index,
	"code": tx[0].code,
	"memo": tx[0].memo,
	"price":price
	})

def account(request, address):
	address=address.lower()
	price = get_price()
	balance = node.addressbal(address)
	if price == "N/A":
		value = "N/A"
	else:
		value = round(balance*price,2)

	if balance == None:
		print("balance failed")
		return render(request,"failedQuery.html")
	start = time.time()
	print("request querying SQL")

	start = time.time()
	txs = serializers.serialize("json",Transactions.objects.raw(f"SELECT * FROM Transactions WHERE receiver='{address}' OR sender='{address}' ORDER BY id DESC LIMIT 25"))
	print(f"SELECT * FROM Transactions WHERE receiver='{address}' OR sender='{address}' ORDER BY id DESC LIMIT 25")
	transfers = serializers.serialize("json",Transactions.objects.raw(f"SELECT * FROM transactions where type='send' AND (receiver='{address}' OR sender='{address}') ORDER BY id DESC LIMIT 10"))

	print('querying node NOW time since start: ', time.time()-start)

	nodeBal, jailed, public_key, nodeVal = node.node_info(address, price)

	# print(txs)

	return render(request,"address.html", {
	"address": address,
	"txs":txs,
	"balance": balance,
	"price":price,
	"value":value,
	"nodeBal":nodeBal,
	"jailed": jailed,
	"public_key":public_key,
	"nodeVal":nodeVal,
	"transfers":transfers,
	"price":price,
	})


def search(request):
	search = request.GET["q"]
	print(search, "searching")

	if len(search)==40:
		return redirect('/address/'+search, permanent=True)
	elif len(search)==64:
		return redirect('/tx/'+search, permanent=True)
	elif len(search)<16 and search.isnumeric():
		return redirect('/block/'+search,permanent=True)
	else:
		return render(request,"failedQuery.html")

def block(request, blocknum):
	price = get_price()

	block = node.block(blocknum)

	if block == True:
		return render(request,"failedQuery.html")
	else:
		relays, height, time, txs, proposer = block

	return render(request, 'block.html', {
	"height": height,
	"time":time,
	"txs": txs,
	"proposer": proposer,
	"relays": relays,
	"price":price
	})

def txs(request):
	price = get_price()

	if 'p' in request.GET:
		page = int(request.GET["p"])
	else:
		page=1
	# totalPages =


	if 'a' in request.GET:
		print("start count")
		for i in Transactions.objects.raw(f"SELECT 1 id, count(*) FROM transactions WHERE sender='{request.GET['a']}' OR receiver='{request.GET['a']}'"):
			count=i.count
		print("count finished")
		transactions = Transactions.objects.raw(f"SELECT * FROM transactions WHERE sender='{request.GET['a']}' OR receiver='{request.GET['a']}' ORDER BY id DESC LIMIT 50 OFFSET {(page-1)*50}")
		print("transations done, rendering.")
	elif 'b' in request.GET:
		transactions = Transactions.objects.raw(f"SELECT * FROM transactions WHERE height={request.GET['b']} ORDER BY id DESC LIMIT 50 OFFSET {(page-1)*50}")
	else:
		transactions = Transactions.objects.raw(f"SELECT * FROM transactions ORDER BY id DESC LIMIT 50 OFFSET {(page-1)*50}")

	transactions = serializers.serialize("json", transactions)

	return render(request, 'txs.html', {
	"txs": transactions,
	"price": price,
	"count": count,
	"address": request.GET['a'],
	"page": page,
	"totalPages": math.ceil(count/50)
	})

def handler500(request):
	return render(request, "500.html")

def test(request):
	return render(request, "test.html")


def rewards(request, address):
	transactions = Transactions.objects.raw(f"SELECT * FROM transactions WHERE type='claim' AND sender='{address}'")
	height = node.height()
	two_day = 0
	week = 0
	month = 0
	for tx in txs:
		if tx.height > height-192:
			two_day+=tx.amount
		if tx.height > height-672:
			week +=tx.amount
		if tx.height > height-43200:
			month +=tx.amount


	return render(request, 'rewards.html', {
	"2d": two_day,
	"week": week,
	"month": month,
	"txs": transactions
	})


# connection = psycopg2.connect(user='postgres', database='poktwatch', password='ok', host='localhost')
# c = connection.cursor()
@csrf_exempt
def api(request):
	if request.method=='POST':
		try:
			print(request.body)
			postdict = json.loads(request.body.decode('utf-8'))
			accounts = postdict["accounts"]

			dict ={"accounts": {}}

			for account in accounts:
				accountTxs = []
				c = Transactions.objects.raw(f"SELECT height, value, timestamp, chain, id FROM transactions where type='claim' and sender='{account}' and code=0")
				print(account)
				for tx in c:
					print(tx)
					accountTxs.append({"block":tx.height,"reward": tx.value, "time": tx.timestamp, "chain":tx.chain})

				dict["accounts"][account]= accountTxs
		except Exception as e:
			return JsonResponse({"code":500, "error":str(e)})

		return JsonResponse(dict)
	return JsonResponse({"code":400})

@csrf_exempt
def apiAccountHash(request):
        if request.method=='POST':
                try:
                        print(request.body)
                        postdict = json.loads(request.body.decode('utf-8'))
                        accounts = postdict["accounts"]

                        dict ={"accounts": {}}

                        for account in accounts:
                                accountTxs = []
                                c = Transactions.objects.raw(f"SELECT height, hash, value, id FROM transactions where sender='{account}' or receiver='{account}'")
                                print(account)
                                for tx in c:
                                        print(tx)
                                        accountTxs.append({"block":tx.height,"hash": tx.hash, "amount": tx.value})

                                dict["accounts"][account]= accountTxs
                except Exception as e:
                        return JsonResponse({"code":500, "error":str(e)})

                return JsonResponse(dict)
        return JsonResponse({"code":400})
