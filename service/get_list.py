#! /usr/bin/env python

import sys
import ipfsApi
import argparse
import re
import tempfile

import crypto_utils
import settings

from collections import OrderedDict


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    # TODO: uncommit in ticket:15
    # parser.add_argument(
    #     '-u', '--user', required=True, help='user\'s hash')
    parser.add_argument(
        '-b', '--bulletin', required=True, help='bulletin\'s hash')
    return parser.parse_args()


def get_current_list_or_create_new(api, list_hash):
    data = api.object_get(list_hash)
    if data and data.get('Data') and "List of bulletins" in data['Data']:
        return data
    return dict(Data="List of bulletins", Links=[])


def get_all_hashes(links):
    return {link['Hash'] for link in links}


def add_to_list(api, bulletin_hash):
    peer_id = api.id()['ID']
    try:
        with open(settings.LAST_HASH_PATH) as f:
            old_hash = f.read()
    except IOError:
        path = api.name_resolve(peer_id)['Path']
        old_hash = re.sub("/ipfs/", "", path)

    data = get_current_list_or_create_new(api, old_hash)

    if bulletin_hash in get_all_hashes(data['Links']):
        return 'Already in bulletin\'s list'

    data['Links'].append(OrderedDict(Name="", Hash=bulletin_hash, Size=0))
    data['Data'] = crypto_utils.dumps(dict(
        signature=crypto_utils.sign_data(
            crypto_utils.dumps(data['Links']),
            settings.PRIVATE_KEY_PATH
        ),
        data="List of bulletins",
        previous=old_hash
    )
    )

    fake_json_file = tempfile.NamedTemporaryFile(suffix='.json')
    fake_json_file.write(crypto_utils.dumps(data))
    fake_json_file.seek(0)

    new_file = api.object_put(fake_json_file)
    new_hash = new_file['Hash']

    with open(settings.LAST_HASH_PATH, 'w') as f:
        f.write(new_hash)

    return new_hash


def check_user(api, user, bulletin_hash):
    bulletin = api.object_get(bulletin_hash)
    try:
        voter = bulletin['Data']['bulletin']['voter']
    except Exception:
        return
    if user != voter:
        raise ValueError('User and voter are different')


def main():
    api = ipfsApi.Client('127.0.0.1', 5401)
    args = parse_arguments(sys.argv[1:])
    # TODO: uncommit in ticket:15
    # check_user(api, args.user, args.bulletin)
    print add_to_list(api, args.bulletin)

if __name__ == '__main__':
    main()
