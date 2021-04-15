import hashlib
import json

class merkle_node:
    def __init__(self):
        self.parent = None
        self.child = None
        self.hash = None

def create_tree(listoftransactions):
    tree_nodes = []
    if(len(listoftransactions) % 2 == 1): listoftransactions.append(listoftransactions[-1])
    for i in range(0, len(listoftransactions)):
           hash_node = merkle_node()
           hash_node.child = listoftransactions[i]
           hash_node.hash = hashlib.sha256(json.dumps(listoftransactions[i], sort_keys=True).encode()).hexdigest()
           tree_nodes.append(hash_node)
        
    while(len(tree_nodes) != 1):
        temp = []
        for i in range(0, len(tree_nodes), 2):
            hash_node = merkle_node()
            hash_node.child = [tree_nodes[i], tree_nodes[i+1]]
            hash_node.hash = hashlib.sha256(bytes(tree_nodes[i].hash+tree_nodes[i+1].hash, 'ascii')).hexdigest()
            tree_nodes[i].parent = hash_node
            tree_nodes[i+1].parent = hash_node
            temp.append(hash_node)
        tree_nodes = temp
        
    return tree_nodes[0]

def verify_transaction(tx, merkle_root, listofhashes):
    hash = hashlib.sha256(json.dumps(tx.tx, sort_keys=True).encode()).hexdigest()
    for i in range(len(listofhashes)):
        hash = hashlib.sha256(bytes(hash+listofhashes[i], 'ascii')).hexdigest()
    if hash == merkle_root.hash: return True
    return False

