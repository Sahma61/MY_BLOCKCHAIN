import argparse
import json
import copy
from node import Node
from txs import *
import socket

def Send(args):
    UTXO = node.config["UTXO"]
    tx_in = []
    balance = 0
    for x in UTXO.keys():
        if UTXO[x].get(node.config["address"]) == None: continue
        if UTXO[x][node.config["address"]] >= (args.value - args.fee): tx_in.append(x); break
        else: tx_in.append(x); balance += UTXO[x][node.config["address"]]
        if balance >= (args.value - args.fee): break
    if balance >= (args.value - args.fee):
        tx = transaction(tx_in, {args.address: args.value, node.config["address"]: balance - args.value - args.fee})
    else:
        print("Not enough balance!")
        exit()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 8085))
    data = json.dumps(tx.tx, sort_keys=True).encode()
    sock.sendto(data, ('127.0.0.1', 8080))
    
def Receive(args):
    node.receive_thread()

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

#parser_bar = subparsers.add_parser('Mine')
#parser_bar.add_argument('z')
#parser_bar.set_defaults(func=bar)

args = parser.parse_args()
args.func(args)
