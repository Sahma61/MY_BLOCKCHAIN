import argparse
import json
import copy
from node import Node
from txs import *
import socket
from bks import block
from utils import *
import os

def Send(args):
    UTXO = node.config["UTXO"]
    tx_in = []
    balance = 0
    for x in UTXO.keys():
        if UTXO[x].get(node.config["bitcoin_address"]) == None: continue
        if UTXO[x][node.config["bitcoin_address"]] >= (args.value + args.fee): tx_in.append(x); balance = UTXO[x][node.config["bitcoin_address"]]; break
        else: tx_in.append(x); balance += UTXO[x][node.config["bitcoin_address"]]
        if balance >= (args.value + args.fee): break
    if balance >= (args.value + args.fee):
        tx = transaction(tx_in, {args.address: args.value, node.config["bitcoin_address"]: balance - args.value - args.fee})
    else:
        print("Not enough balance!")
        exit()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(8000, 9000):
        try: sock.bind(("127.0.0.1", i))
        except socket.error as e: continue
        address, port = sock.getsockname()
        if port >= 8000 and port <= 9000: break
    
    data = json.dumps((2, tx.tx)).encode()
    sock.settimeout(0.0)
    with open('peerpool.json', 'r') as infile: peers = json.load(infile)
    for x in peers:
        sock.sendto(data, (x[0], x[1]))
    
def Receive(args):
    node.receive_thread()
    
def Mine(args):
    if not os.listdir('BKS'):
        with open('config.json', 'r') as infile: previousblock = json.load(infile)
    else:
        with open(f'BKS/{os.listdir[-1]}', 'r') as infile: previousblock = json.load(infile)
    with open('txpool.json', 'r') as infile: txpool = json.load(infile)
    if len(txpool) <= 10:
        listoftransactions = []
        listofids = []
        for x in txpool.keys():
            listoftransactions.append(txpool[x])
            listofids.append(x)
            
    merkle_root = create_tree(listoftransactions)
    bk = block()
    bk.insert_tx(listofids)
    bk.block["previousblockhash"] = hashlib.sha256(json.dumps(previousblock, sort_keys=True).encode()).hexdigest()
    bk.block["merkelroot"] = merkle_root.hash
    print(bk.block)
    bk.mine_block()
    
    print("Mined block:", bk.block) 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(8000, 9000):
        try: sock.bind(("127.0.0.1", i))
        except socket.error as e: continue
        address, port = sock.getsockname()
        if port >= 8000 and port <= 9000: break
    
    data = json.dumps((3, bk.block)).encode()
    sock.settimeout(0.0)
    with open('peerpool.json', 'r') as infile: peers = json.load(infile)
    for x in peers:
        sock.sendto(data, (x[0], x[1]))

node = Node()
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_foo = subparsers.add_parser('Send')
parser_foo.add_argument('address', type=str, default="")
parser_foo.add_argument('value', type=float)
parser_foo.add_argument('fee', type=float)
parser_foo.set_defaults(func=Send)

parser_bar = subparsers.add_parser('Receive')
parser_bar.set_defaults(func=Receive)

#parser_bar = subparsers.add_parser('Create')
#parser_bar.add_argument('z')
#parser_bar.set_defaults(func=bar)

parser_bar = subparsers.add_parser('Mine')
parser_bar.set_defaults(func=Mine)

args = parser.parse_args()
args.func(args)
