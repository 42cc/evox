import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

LIST_DEPTH = 1000
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'tests/test_data/rsa_key')
PUBLIC_KEY_PATH = os.path.join(BASE_DIR, 'tests/test_data/rsa_key.pub')
VOTERS_BLACKLIST = os.path.join(BASE_DIR, 'tests/test_data/test_blacklist.txt')
LAST_HASH_PATH = os.path.join(BASE_DIR, 'service/last_hash')

