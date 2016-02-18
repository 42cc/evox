# coding=utf-8
import copy
import unittest
import mock as mock
from service import crypto_utils
from service.crypto_utils import sign_data

from service.votes_calculator import VotingResultCalculator

TEST_VOTERS_FILE = 'tests/test_data/test_voters.csv'
TEST_VOTERS_FILE_EQUAL = 'tests/test_data/test_voters_equal.csv'
TEST_PRIVKEY_PATH = 'tests/test_data/rsa_key'
TEST_DELEGATIONS_FILE = 'tests/test_data/test_delegations.json'
TEST_DELEGATIONS_FILE_BL = 'tests/test_data/test_delegations_blacklist.json'

TEST_BULLETINS = {
    'QmPDBf5H6GM2A9hTU65qt1qfFkaL7Xm7sKKuG1SoyY65zH':
    # only this one has correct signature
        {
            "Links": [],
            "Data": crypto_utils.dumps(
                {"bulletin": {
                    "voting": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "vote": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "voter": "QmPDBf5H6GM2A9hTU65qt1qfFkaL7Xm7sKKuG1SoyY65zH",
                    "datetime": "2016-15-02T21:03:03.983Z",
                    "publickey": "-----BEGIN PUBLIC KEY-----_MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDuSAd79LwrPujBfBzzIhSf3OgR_7YsChFeXEnEg8QtfU4rMnxA9/Dr1sWhKAQMfrLypvekzQXKADtzeIgszof7wbkWg_2Sf5L/c2xmgNchMoofX+3VKYVh8Px1q5krpJvJPEqL/jsVrHqz72x1Isi8SySssl_L5eJ9O8LlSO+IEcJ0QIDAQAB_-----END PUBLIC KEY-----"
                },
                    "signature": "GC1ZU4UG5BtQvawG0MVrmrVN8AarCFZiHUKv9zIXXwaq4H84nRk9yRiW1C8Qwjbwe74phYxkeM0iZgQROVs2wktWqOa5LWpAvQNQRQgoOLeylz75Ob0oKjfCQXntsQ+oeGik+O5yewbgF0PoHUttdaMpLatLOsyn78WKvEvKeQI="
                }
            )
        },
    'QmPDBf5H6GM2A9hTU65qt1qfFkaL7Xm7sKKuG1SoyY65z1':
        {
            "Links": [],
            "Data": crypto_utils.dumps(
                {"bulletin": {
                    "voting": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "vote": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "voter": "QmZCR55FXELi7aW4TVfk1WwEHTficniTAVBmJYuw51uq6c",
                    "datetime": "2016-15-02T21:03:03.983Z",
                    "publickey": "-----BEGIN RSA PUBLIC KEY-----_MIIBCgKCAQEA61BjmfXGEvWmegnBGSuS+rU9soUg2FnODva32D1AqhwdziwHINFa_D1MVlcrYG6XRKfkcxnaXGfFDWHLEvNBSEVCgJjtHAGZIm5GL/KA86KDp/CwDFMSw_luowcXwDwoyinmeOY9eKyh6aY72xJh7noLBBq1N0bWi1e2i+83txOCg4yV2oVXhB_o8pYEJ8LT3el6Smxol3C1oFMVdwPgc0vTl25XucMcG/ALE/KNY6pqC2AQ6R2ERlV_gPiUWOPatVkt7+Bs3h5Ramxh7XjBOXeulmCpGSynXNcpZ/06+vofGi/2MlpQZNhH_Ao8eayMp6FcvNucIpUndo1X8dKMv3Y26ZQIDAQAB_-----END RSA PUBLIC KEY-----"
                },
                    "signature": "pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1P6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw=="
                }
            )
        },
    'QmNgYn9TKW7X1roE5tmbGb7tcUCfT4wA8fJttRYsG6SVP3':
        {
            "Links": [],
            "Data": crypto_utils.dumps(
                {"bulletin": {
                    "voting": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "vote": "QmZD7RuvjwFmwDtFHMzA4d3pp3gSQFvLFSE3yipz9z3HBt",
                    "voter": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "datetime": "2016-15-02T21:03:03.983Z",
                    "publickey": "-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hTf8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/AnsCAwEAAQ==_-----END PUBLIC KEY-----"
                },
                    "signature": "pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1P6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw=="
                }
            )
        },
    # invalid one
    'QmZD7RuvjwFmwDtFHMzA4d3pp3gSQFvLFSE3yipz9z3HBt':
        {
            "Links": [],
            "Data":
                {"bulletin": {
                    "voting": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "vote": "QmZD7RuvjwFmwDtFHMzA4d3pp3gSQFvLFSE3yipz9z3HBt",
                    "voter": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "datetime": "2016-15-02T21:03:03.983Z",
                    "publickey": "-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hTf8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/AnsCAwEAAQ==_-----END PUBLIC KEY-----"
                },
                    "signature": "pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1P6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw=="
                }
        },
    # duplicate of first bulletin
    'QmNgYn9TKW7X1roE5tmbGb7tcUCfT4wA8fJttRYsG6SVPz':
        {
            "Links": [],
            "Data": crypto_utils.dumps(
                {"bulletin": {
                    "voting": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "vote": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "voter": "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
                    "datetime": "2016-15-02T21:03:03.983Z",
                    "publickey": "-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hTf8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/AnsCAwEAAQ==_-----END PUBLIC KEY-----"
                },
                    "signature": "pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1P6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw=="
                }
            )
        },
}
TEST_SIGNATURES = {
    'QmPDBf5H6GM2A9hTU65qt1qfFkaL7Xm7sKKuG1SoyY65zH':
        'GC1ZU4UG5BtQvawG0MVrmrVN8AarCFZiHUKv9zIXXwaq4H84nRk9yRiW1'
        'C8Qwjbwe74phYxkeM0iZgQROVs2wktWqOa5LWpAvQNQRQgoOLeylz75Ob'
        '0oKjfCQXntsQ+oeGik+O5yewbgF0PoHUttdaMpLatLOsyn78WKvEvKeQI='
}

TEST_SIGNATURE_2 = {
    'data': {"Links":[],"Data":"{\"bulletin\":{\"voting\":\"QmbLejxDBYXudpeGgdtZPnbj6oxVLocF41MgwYEAtdFRmr\",\"vote\":\"QmbLejxDBYXudpeGgdtZPnbj6oxVLocF41MgwYEAedFRmv\",\"voter\":\"QmbLejxDBYXudpeGgdtZPnbj6oxVLocF41MgwYEAadFRma\",\"datetime\":\"2016-18-02T12:11:25.703Z\",\"publickey\":\"-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hTf8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/AnsCAwEAAQ==_-----END PUBLIC KEY-----\"},\"signature\":\"AmEHabyPauvSkl4XWThQ9EvFwR2ZAQqT3nGcI6GRVobUxXvoTDNit06njiY56n4BswLR4Vcs1q9YwCbGNdvj1g==\"}"}
}

TEST_BULLETINS_LISTS = {}
with open('tests/test_data/test_bulletins.json', 'r') as f:
    data = crypto_utils.loads(f.read())
TEST_BULLETINS_LISTS['QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw358'] = data

with open('tests/test_data/test_bulletins_duplicates.json', 'r') as f:
    data = crypto_utils.loads(f.read())
TEST_BULLETINS_LISTS['QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw359'] = data
with open('tests/test_data/test_bulletins_signed.json', 'r') as f:
    data = crypto_utils.loads(f.read())
TEST_BULLETINS_LISTS['QmQebYKTFSqYRoUPFmEgYvXxiNTBcj2QqarqJPGM9nUEQj'] = data


class TestVotingResult(unittest.TestCase):

    def test_load_voters(self):
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        self.assertDictEqual(calc.voters, {
            '-----BEGIN PUBLIC KEY-----_MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDuSAd79LwrPujBfBzzIhSf3OgR_7YsChFeXEnEg8QtfU4rMnxA9/Dr1sWhKAQMfrLypvekzQXKADtzeIgszof7wbkWg_2Sf5L/c2xmgNchMoofX+3VKYVh8Px1q5krpJvJPEqL/jsVrHqz72x1Isi8SySssl_L5eJ9O8LlSO+IEcJ0QIDAQAB_-----END PUBLIC KEY-----': 10,
            '-----BEGIN RSA PUBLIC KEY-----_MIIBCgKCAQEA61BjmfXGEvWmegnBGSuS+rU9soUg2FnODva32D1AqhwdziwHINFa_D1MVlcrYG6XRKfkcxnaXGfFDWHLEvNBSEVCgJjtHAGZIm5GL/KA86KDp/CwDFMSw_luowcXwDwoyinmeOY9eKyh6aY72xJh7noLBBq1N0bWi1e2i+83txOCg4yV2oVXhB_o8pYEJ8LT3el6Smxol3C1oFMVdwPgc0vTl25XucMcG/ALE/KNY6pqC2AQ6R2ERlV_gPiUWOPatVkt7+Bs3h5Ramxh7XjBOXeulmCpGSynXNcpZ/06+vofGi/2MlpQZNhH_Ao8eayMp6FcvNucIpUndo1X8dKMv3Y26ZQIDAQAB_-----END RSA PUBLIC KEY-----': 46.5,
            '-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hTf8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/AnsCAwEAAQ==_-----END PUBLIC KEY-----': 43.5})

    def ipfs_object_get(self, hash):
        if hash in TEST_BULLETINS:
            return copy.deepcopy(TEST_BULLETINS[hash])
        elif hash in TEST_BULLETINS_LISTS:
            return copy.deepcopy(TEST_BULLETINS_LISTS[hash])
        return None

    @mock.patch('ipfsApi.Client.object_get', ipfs_object_get)
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_signature')
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_list_signature')
    @mock.patch('service.settings.VOTERS_BLACKLIST', '')
    def test_vote_result(self, verify_signature, verify_list_signature):
        verify_signature.return_value = True
        verify_list_signature.return_value = True
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        calc.load_bulletins('QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw358')
        result = calc.calculate()
        self.assertEqual(result, [
            {'vote': 'Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg',
             'percent': 56.5},
            {'vote': 'QmZD7RuvjwFmwDtFHMzA4d3pp3gSQFvLFSE3yipz9z3HBt',
             'percent': 43.5},
        ])

    @mock.patch('ipfsApi.Client.object_get', ipfs_object_get)
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_signature')
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_list_signature')
    @mock.patch('service.settings.VOTERS_BLACKLIST', '')
    def test_invalid_bulletin(self, verify_signature, verify_list_signature):
        verify_signature.return_value = True
        verify_list_signature.return_value = True
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        calc.load_bulletins('QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw358')
        # change last bulletin
        calc.bulletins_data[-1]['Hash'] = \
            'QmZD7RuvjwFmwDtFHMzA4d3pp3gSQFvLFSE3yipz9z3HBt'
        result = calc.calculate()
        self.assertEqual(result, [
            {'vote': 'Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg',
             'percent': 100},
        ])

    @mock.patch('ipfsApi.Client.object_get', ipfs_object_get)
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_signature')
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_list_signature')
    @mock.patch('service.settings.VOTERS_BLACKLIST', '')
    def test_duplicate_votes(self, verify_signature, verify_list_signature):
        verify_signature.return_value = True
        verify_list_signature.return_value = True
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        calc.load_bulletins('QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw359')
        result = calc.calculate()
        self.assertEqual(result, [
            {'vote': 'Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg',
             'percent': 56.5},
            {'vote': 'QmZD7RuvjwFmwDtFHMzA4d3pp3gSQFvLFSE3yipz9z3HBt',
             'percent': 43.5},
        ])

    @mock.patch('ipfsApi.Client.object_get', ipfs_object_get)
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_list_signature')
    def test_verify_bulletin_signatures(self, verify_list_signature):
        verify_list_signature.return_value = True
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        vote_data = TEST_BULLETINS[
            'QmPDBf5H6GM2A9hTU65qt1qfFkaL7Xm7sKKuG1SoyY65zH']
        data = crypto_utils.loads(vote_data['Data'])
        bulletin = data['bulletin']

        # sign data
        signature = sign_data(crypto_utils.dumps(bulletin), TEST_PRIVKEY_PATH)
        # verify we can check signature
        self.assertTrue(calc.verify_signature(bulletin, signature))
        # # verify signature is correct
        self.assertEqual(
            signature,
            TEST_SIGNATURES['QmPDBf5H6GM2A9hTU65qt1qfFkaL7Xm7sKKuG1SoyY65zH'])

        # modify bulletin
        bulletin['datetime'] = '2016-01-02T20:03:03.983Z'
        # ensure signature does not verify now
        self.assertFalse(calc.verify_signature(bulletin, signature))

        # check another key
        vote = TEST_SIGNATURE_2['data']
        data = crypto_utils.loads(vote['Data'])

        self.assertTrue(calc.verify_signature(data['bulletin'], data['signature']))

        # verify calculation
        calc.load_bulletins('QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw358')
        result = calc.calculate()
        self.assertEqual(result, [
            {'vote': 'Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg',
             'percent': 100.0},
        ])

    @mock.patch('ipfsApi.Client.object_get', ipfs_object_get)
    def test_bulletins_signature(self):
        # correct signature
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        calc.load_bulletins('QmQebYKTFSqYRoUPFmEgYvXxiNTBcj2QqarqJPGM9nUEQj')
        self.assertEqual(len(calc.bulletins_data), 4)
        # no signature
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        calc.load_bulletins('QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw359')
        self.assertEqual(len(calc.bulletins_data), 0)
        # incorrect signature
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        calc.load_bulletins('QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw358')
        self.assertEqual(len(calc.bulletins_data), 0)

    @mock.patch('ipfsApi.Client.object_get', ipfs_object_get)
    @mock.patch('service.settings.VOTERS_BLACKLIST', '')
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_signature')
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_list_signature')
    def test_delegations(self, verify_signature, verify_list_signature):
        verify_signature.return_value = True
        verify_list_signature.return_value = True
        calc = VotingResultCalculator(TEST_VOTERS_FILE)
        calc.load_bulletins('QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw358')
        calc.load_delegations(TEST_DELEGATIONS_FILE)
        result = calc.calculate()
        self.assertEqual(result, [
            {'vote': 'QmZD7RuvjwFmwDtFHMzA4d3pp3gSQFvLFSE3yipz9z3HBt',
             'percent': 100.0},
        ])

    @mock.patch('ipfsApi.Client.object_get', ipfs_object_get)
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_signature')
    @mock.patch('tests.test_get_voting_result.VotingResultCalculator.verify_list_signature')
    def test_blacklist(self, verify_signature, verify_list_signature):
        verify_signature.return_value = True
        verify_list_signature.return_value = True
        calc = VotingResultCalculator(TEST_VOTERS_FILE_EQUAL)
        calc.load_bulletins('QmVFMoYRf2AKd5EoMV6zmuSa8hJJimjYmrSD8Mq73Tw358')
        calc.load_delegations(TEST_DELEGATIONS_FILE_BL)
        result = calc.calculate()
        self.assertEqual(result, [
            {'vote': 'Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg',
             'percent': 50.0},
            {'vote': 'QmZD7RuvjwFmwDtFHMzA4d3pp3gSQFvLFSE3yipz9z3HBt',
             'percent': 50.0},
        ])
