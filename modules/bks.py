import hashlib, json
import sys, os, time
from utils import *
class block:
    def __init__(self):
      
        self.block = {}
        self.block["blocknum"] = 0
        self.block["time"] = 0
        self.block["size"] = 0
        self.block["version"] = None
        self.block["previousblockhash"] = None
        self.block["merkelroot"] = None
        self.block["time"] = 0
        self.block["difficulty"] = 0.0
        self.block["difficulty_1"] = "0x00000000FFFF0000000000000000000000000000000000000000000000000000"
        self.block["nonce"] = None
        self.block["txs"] = []
        
        try:
            file_in = open("config.json", "rb")
            config = json.load(file_in)
            self.block["bits"] = config["bits"]
            
        except FileNotFoundError:
            self.block["bits"] = "0x1e03a30c"

    def insert_tx(self, listoftxs):
        for txs in listoftxs:
            self.block["txs"].append(txs)
        return
    
    def adjust_dif(self):
        
        if not os.listdir('BKS'):
            return
        
        Interval = 4
        TargetTimespan = 2400
        
        if len(list(os.listdir("BKS"))) % Interval == 0:
            adjustment_needed = True
            level = len(list(os.listdir("BKS"))) // Interval
            
            value1 = sorted(list(os.listdir("BKS")))[-1]
            with open(f'BKS/{value1}', 'r') as infile: previousblock = json.load(infile)
            
            value2 = sorted(list(os.listdir("BKS")))[(level-1)*Interval]
            with open(f'BKS/{value2}', 'r') as infile: ppreviousblock = json.load(infile)
    
    
            ActualTimespan = previousblock["time"] - ppreviousblock["time"]
           
            if ActualTimespan < TargetTimespan/4:
                ActualTimespan = TargetTimespan/4
        
            if ActualTimespan > TargetTimespan*4:
                ActualTimespan = TargetTimespan*4
                
            #Retarget
            bnPowLimit = 2**256 - 1
            bnNew = int(previousblock["bits"][4:], 16)*2**(8*(int(previousblock["bits"][2:4], 16) - 3))
            bnOld = bnNew
            bnNew *= ActualTimespan
            bnNew /= TargetTimespan
            
            if bnNew > bnPowLimit:
                bnNew = bnPowLimit
                
            print("Ratio: ", bnNew/bnOld)
            time.sleep(10.0)
                
            target = target_to_bits(target=bnNew)
            
            target0 = target[0]
            target1 = target[1]
            
            if len(target0) != 4: target0 = "0x0" + target0[-1]
            
            self.block["bits"] = target0 + target1[2:]
            
            with open('config.json', 'r') as infile: config = json.load(infile)
            config["bits"] = self.block["bits"]
            file_out = open("config.json", "wb")
            file_out.write(json.dumps(config, sort_keys = True).encode())
            file_out.close()
            
        return
        
        
    def mine_block(self):
        self.adjust_dif()
        self.block["blocknum"] = len(list(os.listdir('BKS'))) + 1
        target = int(self.block["bits"][4:], 16)*2**(8*(int(self.block["bits"][2:4], 16) - 3))
        self.block["difficulty"] = int(self.block["difficulty_1"], 16) / target
        self.block["time"] = int(time.clock_gettime(time.CLOCK_REALTIME))
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
    #valid &= block["bits"] == "0x1e03a30c"
    valid &= block["previousblockhash"] == hashlib.sha256(json.dumps(previousblock, sort_keys=True).encode()).hexdigest()
    valid &= block["merkelroot"] == merkle_root
    #valid &= block["time"] == 0
    #valid &= block["difficulty"] == 0.0
    
    target = int(block["bits"][4:], 16)*2**(8*(int(block["bits"][2:4], 16) - 3))
    val = hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
    if target > int(val, 16): valid = True
    else: valid = False
    for x in block["txs"]:
        if x not in txpool.keys(): valid = False; break
            
    return valid

def add_new_bk(bk_pool, bk):
    verify_bk(bk)
    bk_pool[hashlib.sha256(json.dumps(bk, sort_keys=True).encode()).hexdigest()] = bk
    
def target_to_bits(target):
    exponent = 0
    coefficient = 0
    for exp in range(0x04, 0xFF):
        if target > 2**(8 * (exp - 3)) and target % 2**(8 * (exp - 3)) == 0:
            exponent = exp
            coefficient = target // 2**(8 * (exp - 3))
    return hex(exponent), hex(int(coefficient))
