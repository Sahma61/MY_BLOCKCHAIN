import socket, errno
import json
import hashlib
import copy
import gen_keys
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
MAX_BYTES = 65535

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
        
        try:
            file_in = open("encrypted.bin", "rb")
        except FileNotFoundError:
            gen_keys.get_keys()
            file_in = open("encrypted.bin", "rb")
            
        password = input("Enter the password:")
        for i in range(16 - len(password) % 16): password = password + "0"
        key = password.encode()
        nonce, tag, ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        self.keys = json.loads(data.decode())
        self.config["pubkey"] = self.keys["public_key"]
        self.config["bitcoin_address"] = self.keys["bitcoin_address"]
        
        try:
            file_in = open("config.json", "rb")
        except FileNotFoundError:
            file_out = open("config.json", "wb")
            file_out.write(json.dumps(self.config, sort_keys = True).encode())
            file_out.close()
            
        with open('config.json', 'r') as infile: config = json.load(infile)
        self.config = copy.deepcopy(config)
        
        with open('UTXO.json', 'r') as infile: UTXO = json.load(infile)
        self.config["UTXO"] = copy.deepcopy(UTXO)
        
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
            if len(data) != 0 and recv_address not in self.config["peerpool"] and text[0] == 1: self.config["peerpool"].append((text[1][0], text[1][1])); sock.sendto(json.dumps((1, (address, port))).encode(), recv_address); file_out = open("peerpool.json", "wb"); file_out.write(json.dumps(self.config["peerpool"]).encode()); file_out.close()
            if text[0] == 2: self.config["txpool"][json.dumps(text[1], sort_keys=True)] = text[1]; file_out = open("txpool.json", "wb"); file_out.write(json.dumps(self.config["txpool"]).encode()); file_out.close()
            print('The client at {} says {!r}' .format(recv_address, text))
