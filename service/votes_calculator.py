from __future__ import print_function
import csv
import os
import sys
import ipfsApi
import crypto_utils
import settings


class VotingResultCalculator:
    def __init__(self, voters_file):
        self.api = ipfsApi.Client('127.0.0.1', 5001)
        self.voters = {}
        self.delegations = {}
        self.users_delegated = set()
        self.load_voters(voters_file)
        self.bulletins_data = []
        self.blacklist = self.load_blacklist()

    def load_blacklist(self):
        if not os.path.exists(settings.VOTERS_BLACKLIST):
            return set()
        with open(settings.VOTERS_BLACKLIST) as f:
            res = set()
            for line in f.readlines():
                res.add(line.strip())
            return res

    def load_voters(self, voters_file):
        with open(voters_file, 'rb') as csv_file:
            data = csv.reader(csv_file, delimiter='\t')
            for row in data:
                self.voters[row[0]] = float(row[1].replace(',', '.'))

    def load_bulletins(self, bulletins_hash):
        self.bulletins_data = []
        bulletins = self.api.object_get(bulletins_hash)
        if self.verify_list_signature(bulletins):
            self.bulletins_data = bulletins['Links']
        else:
            print('Incorrect signature for bulletins list: %s'
                  % bulletins_hash, file=sys.stderr)

    def load_delegations(self, delegations_file):
        self.delegations = {}
        self.users_delegated.clear()
        with open(delegations_file, 'rb') as f:
            data = crypto_utils.loads(f.read())
            self.delegations = data['delegations']
            for delegation in self.delegations.values():
                for item in delegation:
                    self.users_delegated.add(item)

    def verify_signature(self, bulletin, signature):
        pub_key = bulletin['publickey'].replace('_', '\n')
        return crypto_utils.verify_sign(
            crypto_utils.dumps(bulletin), pub_key, signature)

    def verify_list_signature(self, bulletins_list):
        try:
            data = crypto_utils.loads(bulletins_list['Data'])
        except ValueError:
            print('Incorrect bulletins list format', file=sys.stderr)
            return False

        with open(settings.PUBLIC_KEY_PATH, 'rb') as f:
            public_key = f.read()

        return crypto_utils.verify_sign(
                crypto_utils.dumps(bulletins_list['Links']),
                public_key, data['signature'])

    def _get_votes(self, bulletin_hashes):
        votes = {}
        users_voted = set()
        for hash_item in bulletin_hashes:
            hash = hash_item['Hash']
            try:
                vote_obj = self.api.object_get(hash)
                data = crypto_utils.loads(vote_obj['Data'])
            except:
                print('Invalid bulletin data for hash %s' % hash,
                      file=sys.stderr)
                continue
            bulletin = data['bulletin']
            try:
                if not self.verify_signature(bulletin, data['signature']):
                    print('Invalid signature for bulletin %s, skipped' % hash,
                          file=sys.stderr)
                    continue
            except IOError as e:
                print('IOError while trying to verify signature for '
                      'bulletin %s: %s' %
                      (hash, e.strerror),
                      file=sys.stderr)
                continue
            if bulletin['publickey'] in users_voted:
                print('Duplicated vote for %s, skipped' % bulletin['publickey'],
                      file=sys.stderr)
                continue
            users_voted.add(bulletin['publickey'])
            if bulletin['vote'] not in votes:
                votes[bulletin['vote']] = []
            votes[bulletin['vote']].append(bulletin['publickey'])
        return votes

    def get_voter_percent(self, voter, exclude_delegated=True):
        if exclude_delegated and voter in self.users_delegated:
            return 0
        if voter in self.blacklist:
            return 0
        percent = self.voters.get(voter, 0)
        if voter in self.delegations:
            for item in self.delegations[voter]:
                percent += self.get_voter_percent(item, False)
        return percent

    def calculate(self):
        hash_list = self.bulletins_data
        votes = self._get_votes(hash_list)
        vote_result = []
        total = 0
        for vote, voters in votes.iteritems():
            percent = 0
            for voter in voters:
                percent += self.get_voter_percent(voter)
            total += percent
            if percent > 0:
                vote_result.append({'vote': vote, 'percent': percent})
        for item in vote_result:
            item['percent'] = round(item['percent'] * 100 / total, 2)
        vote_result.sort(key=lambda x: x['percent'], reverse=True)
        return vote_result
