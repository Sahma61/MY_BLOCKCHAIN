import hashlib, json
import sys
class block:
    def __init__(self):
        self.block = {}
        self.block["size"] = 0
        self.block["version"] = None
        self.block["bits"] = "0x1e03a30c"
        self.block["previousblockhash"] = None
        self.block["merkelroot"] = None
        self.block["time"] = 0
        self.block["difficulty"] = 0.0
        self.block["nonce"] = None
        self.block["txs"] = []

    def insert_tx(self, listoftxs):
        for txs in listoftxs:
            self.block["txs"].append(hashlib.sha256(json.dumps(txs, sort_keys=True).encode()).hexdigest())
        return

    def mine_block(self):
        target = int(self.block["bits"][-6:], 16)*2**(8*(int(self.block["bits"][2:4], 16) - 3))
        print(hex(target))
        for nonce in range(sys.maxsize):
            self.block["nonce"] = hex(nonce)
            val = hashlib.sha256(json.dumps(self.block, sort_keys=True).encode()).hexdigest()
            print(val)
            if target > int(val, 16):
                break
        return val

    def verify_block(): pass

def verify_bk(bk):
    return

def add_new_bk(bk_pool, bk):
    verify_bk(bk)
    bk_pool[hashlib.sha256(json.dumps(bk, sort_keys=True).encode()).hexdigest()] = bk
