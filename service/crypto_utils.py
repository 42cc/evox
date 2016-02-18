import base64
from collections import OrderedDict
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA


def loads(json_str):
    return json.loads(json_str, object_pairs_hook=OrderedDict)


def dumps(obj):
    return json.dumps(obj, separators=(',', ':'))


def sign_data(data, key_path):
    with open(key_path, 'r') as f:
        key = RSA.importKey(f.read())
    signer = PKCS1_v1_5.new(key)
    hash = SHA.new(data)
    signature = signer.sign(hash)
    return base64.b64encode(signature)


def verify_sign(data, pubkey, signature):
    key = RSA.importKey(pubkey)
    hash = SHA.new(data)
    signer = PKCS1_v1_5.new(key)
    return signer.verify(hash, base64.b64decode(signature))
