#! /usr/bin/env python
import ipfsApi
import json

from get_list import get_all_hashes
from settings import LAST_HASH_PATH, LIST_DEPTH


def check_previous(api, last_used, new_list):
    if not new_list:
        return False

    if not last_used:
        return True

    for i in range(LIST_DEPTH):
        data = api.object_get(new_list)
        data = json.loads(data['Data'])

        if not data.get('previous'):
            return False

        if data.get('previous') == last_used:
            return True

    return False


def main():
    api = ipfsApi.Client()
    last_pined_list = None
    while True:
        with open(LAST_HASH_PATH, 'r') as f:
            list_hash = f.read()

        if list_hash == last_pined_list:
            continue

        if check_previous(api, last_pined_list, list_hash):
            data = api.object_get(list_hash)
            bulletin_hashes = get_all_hashes(data['Links'])

            for bulletin_hash in bulletin_hashes:
                api.pin_add(bulletin_hash)
                print 'pined %s' % bulletin_hash

            last_pined_list = list_hash

if __name__ == '__main__':
    main()
