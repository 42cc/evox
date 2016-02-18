#! /usr/bin/env python
import ipfsApi

from settings import LAST_HASH_PATH
from pin_bulletin import check_previous


def main():
    api = ipfsApi.Client()
    last_published_list = None
    while True:
        with open(LAST_HASH_PATH, 'r') as f:
            list_hash = f.read()

        if list_hash == last_published_list:
            continue

        if check_previous(api, last_published_list, list_hash):
            api.name_publish(list_hash)
            print 'published %s' % list_hash
            last_published_list = list_hash

if __name__ == '__main__':
    main()
