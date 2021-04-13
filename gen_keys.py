import bitcoin
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json

def get_keys():
    # Generate a random private key
    valid_private_key = False
    while not valid_private_key:
        private_key = bitcoin.random_key()
        decoded_private_key = bitcoin.decode_privkey(private_key, 'hex')
        valid_private_key =  0 < decoded_private_key < bitcoin.N
        
    keys = {}
        
    keys["private_key"] = private_key
    keys["decoded_private_key"] = decoded_private_key
        
    # Convert private key to WIF format
    wif_encoded_private_key = bitcoin.encode_privkey(decoded_private_key, 'wif')
    keys["wif_encoded_private_key"] = wif_encoded_private_key\
    
    # Add suffix "01" to indicate a compressed private key
    compressed_private_key = private_key + '01'
    keys["compressed_private_key"] = compressed_private_key
    
    # Generate a WIF format from the compressed private key (WIF-compressed)
    wif_compressed_private_key = bitcoin.encode_privkey(
        bitcoin.decode_privkey(compressed_private_key, 'hex'), 'wif')
    keys["wif_compressed_private_key"] = wif_compressed_private_key
    
    # Multiply the EC generator point G with the private key to get a public key point
    public_key = bitcoin.multiply(bitcoin.G, decoded_private_key)
    keys["public_key"] = public_key
    
    # Encode as hex, prefix 04
    hex_encoded_public_key = bitcoin.encode_pubkey(public_key,'hex')
    keys["hex_encoded_public_key"] = hex_encoded_public_key
    
    # Compress public key, adjust prefix depending on whether y is even or odd
    (public_key_x, public_key_y) = public_key
    if (public_key_y % 2) == 0:
        compressed_prefix = '02'
    else:
        compressed_prefix = '03'
        
    hex_compressed_public_key = compressed_prefix + bitcoin.encode(public_key_x, 16)
    keys["hex_compressed_public_key"] = hex_compressed_public_key
    
    # Generate bitcoin address from public key
    keys["bitcoin_address"] = bitcoin.pubkey_to_address(public_key)
    
    # Generate compressed bitcoin address from compressed public key
    keys["bitcoin_address_compressed"] = bitcoin.pubkey_to_address(hex_compressed_public_key)
    
    while(True):
        password1 = input("Enter the password:")
        password2 = input("Enter the password to confirm:")
        if password1 != password2:
            print("Passwords don't match")
            continue
        break
        
    for i in range(16 - len(password1) % 16): 
        password1 = password1 + "0"
    key = password1.encode()
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(bytes(f'{json.dumps(keys, sort_keys=True)}'.encode()))
    
    file_out = open("encrypted.bin", "wb")
    [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
    file_out.close()
