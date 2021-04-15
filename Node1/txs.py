class transaction:
    def __init__(self, vin = [], vout = []):
        self.tx = {}
        self.tx['version'] = 1
        self.tx['locktime'] = 0
        self.tx['vin'] = vin
        self.tx['vout'] = vout
        
    def feed_input(): return 
    def get_output(): return

class tx_in:
    def __init__(self):
        self.inp = {}
        self.inp["txid"] = ""
        self.inp["vin"] = 0
        self.inp["scriptSig"] = ""
        self.inp["sequence"] = 0
        
class tx_out:
    def __init__(self):
        self.out = {}
        self.out["value"] = ""
        self.out["scriptpubKey"] = ""

def verify_tx(tx):
    return

def add_new_tx(tx_pool, tx):
    verify_tx(tx)
    tx_pool[hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()] = tx
    #send it to every peer

def getsign(private_key, tx):
    sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1, hashfunc = hashlib.sha256)
    vk = sk.verifying_key
    data = hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest().encode()
    sign = sk.sign(data)
    print(type(vk))
    return vk, sign

def p2pkh(sigPubKey, Sig, tx):
    vk = Sig[0]
    check = hashlib.sha256(Sig[0].to_string().hex().encode()).hexdigest() == sigPubKey
    data = hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest().encode()
    print(type(Sig[0]))
    if check and  vk.verify(Sig[1], data):
        return True
    return check


