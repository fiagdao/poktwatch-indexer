import requests
import json
import os

class Pokt:
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
                        self.url.nodes = self.ip+"/v1/query/nodes"
                        self.url.apps = self.ip+"/v1/query/apps"
                        self.url.mempool  = "http://45.76.59.153:26657/unconfirmed_txs"

                def node_count(self, height):
                        while True:
                                try:
                                        params = {"opts":{"page":1,"per_page":1000000},"height":height}
                                        nodes = requests.post(self.url.nodes, data=json.dumps(params), headers=self.headers).json()["result"]
                                        if nodes == None:
                                                return 0
                                        return len(nodes)
                                except Exception as e:
                                        print(e, flush=True)
                                        pass


                def app_count(self, height):
                        while True:
                                try:
                                        params = {"opts":{"page":1,"per_page":1000000},"height":height}
                                        apps = requests.post(self.url.apps, data=json.dumps(params), headers=self.headers).json()["result"]
                                        if apps == None:
                                                return 0
                                        return len(apps)
                                except Exception as e:
                                        print(e,flush=True)
                                        pass


                def relay_count(self, height):
                        proofs =0
                        txs = self.block_txs(height)

                        # print(len(txs))
                        for tx in txs:
                                type = tx["tx_result"]["message_type"]

                                if type=="claim":
                                        txproofs = tx["stdTx"]["msg"]["value"]["total_proofs"]
                                        proofs += int(txproofs)
                        return proofs

                def block(self, height):
                        block = requests.post(url=self.url.block, data=json.dumps({"height": height}), headers=self.headers).json()
                        if "code" in block and block["code"]!=200:
                                return True

                        relays = self.relay_count(height)

                        height = block["block"]["header"]["height"]
                        time = block["block"]["header"]["time"]
                        txs = block["block"]["header"]["num_txs"]
                        proposer = block["block"]["header"]["proposer_address"].lower()

                        return relays, height, time, txs, proposer

                def block_time(self, height):
                        block = requests.post(url=self.url.block, data=json.dumps({"height": height}), headers=self.headers).json()
                        if "code" in block and block["code"]!=200:
                                return True

                        time = block["block"]["header"]["time"]

                        return time

                def block_txs(self, height):
                        ret = requests.post(self.url.blocktxs, data=json.dumps({"height":height, "per_page":99999999}), headers=self.headers)
                        data= ret.json()
                        txs = data["txs"]
                        return txs

                def height(self):
                                height = requests.post(self.url.height,data=json.dumps({}),headers=self.headers).json()["height"]
                                return height

                def address(self, address):
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

                def node(self, address, price):
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

                def mempool(self, limit):
                        raw_txs = requests.get(self.url.mempool+"?limit="+str(limit)).json()["result"]["txs"]
                        # txs =[]
                        # for i in raw_txs:
                        #       tx = os.popen(f"pocket util decode-tx {i} False true").read()
                        #       txs.append(tx)
                        # print(raw_txs)
                        return raw_txs

                def strip_raw_tx(self, tx):
                        # print(tx)
                        output = os.popen(f'pocket util decode-tx {tx} false true').read()
                       # print(output)
                        tx = json.loads(output, strict=False)

                        hash=tx["hash"].upper()
                        receiver=tx["receiver"].lower()
                        sender=tx["signer"].lower()
                        type=tx["type"]
                        fee=int(tx["fee"][:-5])
                        height=-1
                        index=-1
                        code=-1
                        memo=tx["memo"]

                        if type=="send":
                                value=tx["msg"]["amount"]
                                proofs=0
                                chain = None
                        elif type=="claim":
                                proofs = tx["msg"]["total_proofs"]
                                value=int(proofs)*8900
                                chain = tx["msg"]["header"]["chain"]
                        else:
                                value=0
                                proofs=0
                                chain = None

                        if len(receiver)<41:
                                return hash, receiver, sender, value, type, fee, height, index, code, memo, chain
                        else:
                                print(hash)
                                return None


                def strip_tx(self, tx):
                        hash = tx["hash"]
                        receiver=tx["tx_result"]["recipient"].lower()
                        sender = tx["tx_result"]["signer"].lower()
                        type = tx["tx_result"]["message_type"]
                        fee=tx["stdTx"]["fee"][0]["amount"]
                        height=tx["height"]
                        index=tx["index"]
                        code=tx["tx_result"]["code"]
                        memo=tx["stdTx"]["memo"]
                        # print("json: ", time.time()-jsonT)

                        if type=="send":
                                value=tx["stdTx"]["msg"]["value"]["amount"]
                                proofs=0
                                chain = None
                        elif type=="claim":
                                proofs = tx["stdTx"]["msg"]["value"]["total_proofs"]
                                value=int(proofs)*8900
                                chain = tx["stdTx"]["msg"]["value"]["header"]["chain"]
                        else:
                                value=0
                                proofs=0
                                chain = None

                        if len(receiver)<41:
                                return hash, receiver, sender, value, type, fee, height, index, code, memo, chain
                        else:
                                print(hash)
                                return None
