from pokt import PoktRPCDataProvider
from threading import Thread
import json
import datetime
import os
import logging
import time
import random

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


def get_block_txs(height: int, pokt_rpc: PoktRPCDataProvider, retries: int = 20, per_page: int = 500):
    """ get all transaction of a block ordered by index (native)

    height - the height to query blocktxs for
    retries - the number of times to retry if there is an RPC error
    per_page - the per_page query of the RPC request, smaller for thinner machines
    pokt_rpc - the PoktRPCDataProvider object to query

    """
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
            time.sleep(random.randint(3, 7))
            logging.error("Failed to gather block-txs, {}".format(e))
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


def flatten_tx(tx, RelaysToTokensMultiplier: int, timestamp):
    """ flatten a tx to the json requirements according to models.py

    tx - the Transaction to flatten
    RelaysToTokensMultiplier - the RelaysToTokensMultiplier at that current block, this is used for calculating the value of a claim
    timestamp - the block timestamp of the height of the tx

    """
    message_type = tx.tx_result.message_type
    if len(tx.tx_result.signer) > 40:
        tx.tx_result.signer = "invalid_signer"

    if len(tx.tx_result.recipient) > 40:
        tx.tx_result.recipient = "invalid_recipient"

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
    """ flatten a raw tx string to the json requirements according to models.py

    raw_tx - the raw transaction string to flatten
    RelaysToTokensMultiplier - the RelaysToTokensMultiplier at that current block, this is used for calculating the value of a claim

    """

    res = os.popen('pocket util decode-tx {} false true'.format(raw_tx)).read()

    try:
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
    except Exception as e:
        logging.error("Raw_tx decoding error {}. Tx result {}".format(e, res))

        quit()
