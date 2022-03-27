import socket, errno
import json
import hashlib
import copy, getpass
import os
import gen_keys
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from txs import *
from bks import *
MAX_BYTES = 65535

def add_UTXO(UTXO, txpool, listoftxids):
    for x in listoftxids:
        tx = txpool[x]
        UTXO[x] = tx["vout"]
    
    for x in listoftxids:
        tx = txpool[x]
        vin = tx["vin"]
        for y in vin:
            if UTXO.get(y[0]) != None and UTXO.get(y[0]).get(y[1]) != None:
                UTXO.get(y[0]).pop(y[1])
                
            if not list(UTXO[y[0]].keys()):
                UTXO.pop(y[0])
                
    for x in listoftxids:
        txpool.pop(x)
                 
    return UTXO, txpool

class Node:
    
    def __init__(self):
        
        self.config = {}
        self.config["txpool"] = {}
        self.config["UTXO"] = {}
        self.config["peerpool"] = []
        self.config["blockpool"] = {}
        self.config["orphantxpool"] = {}
        self.config["orphanblockpool"] = {}
        self.config["pubkey"] = ""
        self.config["bitcoin_address"] = ""
        self.config["bits"] = "0x1e03a30c"
        
        try:
            file_in = open("encrypted.bin", "rb")
        except FileNotFoundError:
            gen_keys.get_keys()
            file_in = open("encrypted.bin", "rb")
            
        password = getpass.getpass(prompt="Enter the password:")
        for i in range(16 - len(password) % 16): password = password + "0"
        key = password.encode()
        nonce, tag, ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        self.keys = json.loads(data.decode())
        self.config["pubkey"] = self.keys["public_key"]
        self.config["bitcoin_address"] = self.keys["bitcoin_address"]
        
        try:
            with open('config.json', 'r') as infile: config = json.load(infile)
            self.config = copy.deepcopy(config)
        except FileNotFoundError:
            file_out = open("config.json", "wb"); file_out.write(json.dumps(self.config, sort_keys = True).encode()); file_out.close()
            
        with open('UTXO.json', 'r') as infile: UTXO = json.load(infile)
        self.config["UTXO"] = copy.deepcopy(UTXO)
        
        try:
            with open('txpool.json', 'r') as infile: txpool = json.load(infile)
            self.config["txpool"] = copy.deepcopy(txpool)
        except FileNotFoundError:
            file_out = open("txpool.json", "wb"); file_out.write(json.dumps(self.config["txpool"], sort_keys = True).encode()); file_out.close()
            
        try:    
            with open('bkpool.json', 'r') as infile: bkpool = json.load(infile)
            self.config["blockpool"] = copy.deepcopy(bkpool)
        except FileNotFoundError:
            file_out = open("bkpool.json", "wb"); file_out.write(json.dumps(self.config["blockpool"], sort_keys = True).encode()); file_out.close()
            
        try:    
            with open('peerpool.json', 'r') as infile: peerpool = json.load(infile)
            self.config["peerpool"] = copy.deepcopy(peerpool)
        except FileNotFoundError:
            file_out = open("peerpool.json", "wb"); file_out.write(json.dumps(self.config["peerpool"], sort_keys = True).encode()); file_out.close()   
            
    def print_attr(self):
        print(self.config)
        
    def add_peers(self, address, loc_address):
        peers = self.config["peerpool"]
        if peers[address] == None:
            peers[address] = loc_address
    
    def add_txs(self, tx):
        txs = self.config["txpool"]
        hash = hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
        if txs.get(hash) == None:
            txs[hash] = tx

    def add_coinbase_tx(self):
        coinbase_tx = transaction(tx_in = [], tx_out = {self.config["bitcoin_address"]: 100}, is_coinbase = True)
        self.add_txs(coinbase_tx.tx)
        coinbase_tx_id = hashlib.sha256(json.dumps(coinbase_tx.tx, sort_keys=True).encode()).hexdigest()
        data = json.dumps((2, coinbase_tx.tx)).encode()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i in range(8000, 9000):
            try: sock.bind(("127.0.0.1", i))
            except socket.error as e: continue
            address, port = sock.getsockname()
            if port >= 8000 and port <= 9000: break

        sock.settimeout(0.0)
        with open('peerpool.json', 'r') as infile: peers = json.load(infile)
        for x in peers:
            sock.sendto(data, (x[0], x[1]))
        return coinbase_tx, coinbase_tx_id
    
    def check_orphan_bks(self, bk):
        bks = self.config["blockpool"]
        hash = hashlib.sha256(json.dumps(bk, sort_keys=True).encode()).hexdigest()
        if bks.get(bk.block["previousblockhash"]) == None:
            return False
        return True
    
    def add_blocks(self, bk):
        bks = self.config["blockpool"]
        #orphan_bks = self.config["orphanblockpool"] 
        hash = hashlib.sha256(json.dumps(bk, sort_keys=True).encode()).hexdigest()
        #if check_orphan_bks(self, bk):
        #if orphan_bks[hash] == None: orphan_bks[hash] = bk
        #else:
        if bks.get(hash) == None: bks[hash] = bk
           
    def receive_thread(self):
        for i in range(8000, 9000):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try: sock.bind(("127.0.0.1", i))
            except socket.error as e: continue
            address, port = sock.getsockname()
            if port >= 8000 and port <= 9000: break
            print("Recieving at %s:%d" %(address, port))
        
        sock.settimeout(0.0)
        data = json.dumps((1, (address, port))).encode()
        for i in range(8000, 9000):
            sock.sendto(data, ('127.0.0.1', i))
        
        sock.settimeout(None)    
        while True:
            print("Recieving at %s:%d" %(address, port))
            data, recv_address = sock.recvfrom(MAX_BYTES)
            text = json.loads(data.decode('ascii'))
            if len(data) != 0 and recv_address not in self.config["peerpool"] and text[0] == 1:
                self.config["peerpool"].append((text[1][0], text[1][1]))
                sock.sendto(json.dumps((1, (address, port))).encode(), recv_address)
                with open("peerpool.json", "wb") as file_out:
                    file_out.write(json.dumps(self.config["peerpool"]).encode())
            if text[0] == 2:
                if verify_tx(text[1], self.config["UTXO"]):
                    print("Transaction verified successfully")
                    self.config["txpool"][hashlib.sha256(json.dumps(text[1], sort_keys=True).encode()).hexdigest()] = text[1]
                    with open("txpool.json", "wb") as file_out:
                    	file_out.write(json.dumps(self.config["txpool"], sort_keys = True).encode())
            if text[0] == 3:
                if verify_bk(text[1], self.config["txpool"]):
                    print("Block verified successfully")
                    if text[1]["blocknum"] <= len(list(os.listdir('BKS'))):
                        self.config["blockpool"][hashlib.sha256(json.dumps(text[1], sort_keys=True).encode()).hexdigest()] = text[1]
                        with open('bkpool.json', "wb") as file_out:
                        	file_out.write(json.dumps(self.config["blockpool"]).encode())
                        continue
                    val = len(os.listdir('BKS'))+1
                    with open(f'BKS/bk{val}.json', "wb") as file_out:
                    	file_out.write(json.dumps(text[1]).encode())
                    output = add_UTXO(self.config["UTXO"], self.config["txpool"], text[1]["txs"])
                    self.config["UTXO"] = output[0]
                    self.config["txpool"] = output[1]
                    file_out = open('UTXO.json', "wb"); file_out.write(json.dumps(self.config["UTXO"]).encode()); file_out.close()
                    file_out = open('txpool.json', "wb"); file_out.write(json.dumps(self.config["txpool"]).encode()); file_out.close()
                    
            print('The client at {} says {!r}' .format(recv_address, text))
