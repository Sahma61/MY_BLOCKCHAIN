#!/bin/bash
mkdir "Node$1"
cp modules/bks.py "Node$1/bks.py"
cp modules/txs.py "Node$1/txs.py"
cp modules/utils.py "Node$1/utils.py"
cp modules/gen_keys.py "Node$1/gen_keys.py"
cp modules/node.py "Node$1/node.py"
cp modules/client.py "Node$1/client.py"
cp modules/genesis.json "Node$1/genesis.json"
cp modules/UTXO.json "Node$1/UTXO.json"
mkdir "Node$1/BKS"
cd "Node$1"
#pyinstaller --onefile client.py
#pyinstaller client.py

