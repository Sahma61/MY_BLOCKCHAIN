import socket
import json
import hashlib
import copy
import gen_keys
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
MAX_BYTES = 65535

class Node:
    
    def __init__(self):
        with open('config.json', 'r') as infile: config = json.load(infile)
        self.config = copy.deepcopy(config)
        self.config["txpool"] = {}
        self.config["UTXO"] = {}
        self.config["peerpool"] = {}
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.2', 8085))
        sock.settimeout(None)
        
        while True:
            print("Recieving at '127.0.0.1/8085")
            data, address = sock.recvfrom(MAX_BYTES)
            if address not in self.config["peerpool"].values(): continue
            text = json.loads(data.decode('ascii'))
            print('The client at {} says {!r}' .format(address, text))
            if text[0] == 1:
                self.add_blocks(text[1])
            self.print_attr()