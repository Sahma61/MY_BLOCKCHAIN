import hashlib, json
import sys, os
from utils import *
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
            self.block["txs"].append(txs)
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

def verify_bk(block, txpool):
    if not os.listdir('BKS'):
        with open('config.json', 'r') as infile: previousblock = json.load(infile)
    else:
        value = list(os.listdir('BKS'))[-1] 
        with open(f'BKS/{value}', 'r') as infile: previousblock = json.load(infile)
    
    listoftransactions = []
    listofids = []
    for x in block["txs"]:
        listoftransactions.append(txpool[x])
    merkle_root = create_tree(listoftransactions)
    
    valid = True
    valid &= block["size"] == 0
    valid &= block["version"] == None
    valid &= block["bits"] == "0x1e03a30c"
    valid &= block["previousblockhash"] == hashlib.sha256(json.dumps(previousblock, sort_keys=True).encode()).hexdigest()
    valid &= block["merkelroot"] == merkle_root
    valid &= block["time"] == 0
    valid &= block["difficulty"] == 0.0
    
    target = int(block["bits"][-6:], 16)*2**(8*(int(block["bits"][2:4], 16) - 3))
    val = hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
    if target > int(val, 16): valid = True
    else: valid = False
    for x in block["txs"]:
        if x not in txpool.keys(): valid = False; break
            
    return valid

def add_new_bk(bk_pool, bk):
    verify_bk(bk)
    bk_pool[hashlib.sha256(json.dumps(bk, sort_keys=True).encode()).hexdigest()] = bk
