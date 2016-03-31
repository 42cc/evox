import unittest
import mock
import os
from service import settings

from service import crypto_utils
from service.get_list import add_to_list, get_current_list_or_create_new
from collections import OrderedDict
TEST_LAST_HASH_PATH = os.path.join(settings.BASE_DIR, 'tests/test_data/last_hash')


class TestScript(unittest.TestCase):

    def tearDown(self):
        try:
            os.remove(TEST_LAST_HASH_PATH)
        except Exception:
            pass

    def test_add_to_list_voting_exist(self):
        api = mock.MagicMock()
        list_hash = mock.Mock()
        data = mock.MagicMock()
        data.__getitem__.return_value = "List of bulletins"
        api.object_get.return_value = data
        resp = get_current_list_or_create_new(api, list_hash)
        self.assertEqual(resp, data)

        api.object_get.return_value = None
        resp = get_current_list_or_create_new(api, list_hash)
        self.assertEqual(resp, dict(Data="List of bulletins", Links=[]))

    @mock.patch('re.sub')
    @mock.patch('service.get_list.get_current_list_or_create_new')
    @mock.patch('tempfile.NamedTemporaryFile')
    @mock.patch('service.crypto_utils.dumps')
    @mock.patch('service.crypto_utils.sign_data')
    @mock.patch('service.settings.LAST_HASH_PATH', TEST_LAST_HASH_PATH)
    def test_add_hash_to_list(self, sign, dumps, tempfile, get_list, sub):
        api = mock.MagicMock()
        api.object_put.return_value.__getitem__.return_value = 'test'
        bulletin = mock.Mock()
        sub.return_value = 'test_hash'
        sign.return_value = 'test_signature'
        get_list.return_value = dict(Data="List of bulletins", Links=[])
        data_dict = dict(
            signature=sign.return_value,
            data="List of bulletins",
            previous=sub.return_value
        )
        bulletin_dict = dict(
            Data=dumps.return_value,
            Links=[OrderedDict(
                Name="",
                Hash=bulletin,
                Size=0)],
        )
        calls = [mock.call(data_dict), mock.call(bulletin_dict)]

        add_to_list(api, bulletin)

        dumps.assert_has_calls(calls)

    @mock.patch('re.sub')
    @mock.patch('service.get_list.get_current_list_or_create_new')
    @mock.patch('tempfile.NamedTemporaryFile')
    @mock.patch('json.dumps')
    @mock.patch('service.crypto_utils.sign_data')
    @mock.patch('service.settings.LAST_HASH_PATH', TEST_LAST_HASH_PATH)
    def test_save_new_list(self, sign, dumps, tempfile, get_list, sub):
        api = mock.MagicMock()
        api.object_put.return_value.__getitem__.return_value = 'test'
        bulletin = mock.Mock()
        sub.return_value = mock.Mock()
        get_list.return_value = dict(Data="List of bulletins", Links=[])

        add_to_list(api, bulletin)
        tempfile.return_value.write.assert_called_once_with(dumps.return_value)
        api.object_put.assert_called_once_with(tempfile.return_value)

    @mock.patch('re.sub')
    @mock.patch('service.get_list.get_current_list_or_create_new')
    @mock.patch('tempfile.NamedTemporaryFile')
    @mock.patch('json.dumps')
    @mock.patch('service.crypto_utils.sign_data')
    @mock.patch('service.settings.LAST_HASH_PATH', TEST_LAST_HASH_PATH)
    def test_return_hash(self,sign, dumps, tempfile, get_list, sub):
        api = mock.MagicMock()
        bulletin = mock.Mock()
        api.object_put.return_value.__getitem__.return_value = 'test'

        resp = add_to_list(api, bulletin)

        self.assertEqual(resp, 'test')

    # TODO: uncommit in ticket:15
    # @mock.patch('ipfsApi.Client')
    # @mock.patch('service.get_list.parse_arguments')
    # @mock.patch('service.get_list.add_to_list')
    # def test_compare_user_voter(self, adding_list, parse, client):
    #     parse.return_value.user = 'test1'
    #     client.return_value.object_get.return_value = \
    #         {'Data': {'bulletin': {'voter': 'test2'}}}
    #     with self.assertRaises(ValueError):
    #         main()

    #     adding_list.assert_not_called()

    #     client.return_value.object_get.return_value = \
    #         {'Data': {'bulletin': {'voter': 'test1'}}}
    #     main()

    #     self.assertTrue(adding_list.called)

    def test_sign_list(self):

        signature1 = crypto_utils.sign_data(crypto_utils.dumps(
            [{'hash': 'a'}]),
            settings.PRIVATE_KEY_PATH)
        signature1_1 = crypto_utils.sign_data(
            crypto_utils.dumps([{'hash': 'a'}]),
            settings.PRIVATE_KEY_PATH)

        self.assertEqual(signature1, signature1_1)

        signature2 = crypto_utils.sign_data(crypto_utils.dumps([{'hash': 'b'}]),
                                            settings.PRIVATE_KEY_PATH)

        self.assertNotEqual(signature1, signature2)

    @mock.patch('service.settings.LAST_HASH_PATH', TEST_LAST_HASH_PATH)
    @mock.patch('re.sub')
    @mock.patch('service.get_list.get_current_list_or_create_new')
    @mock.patch('tempfile.NamedTemporaryFile')
    @mock.patch('json.dumps')
    @mock.patch('service.crypto_utils.sign_data')
    def test_add_hash_to_file(self, sign, dumps, tempfile, get_list, sub):
        api = mock.MagicMock()
        api.object_put.return_value.__getitem__.return_value = 'test'
        bulletin = mock.Mock()
        sub.return_value = mock.Mock()
        get_list.return_value = dict(Data="List of bulletins", Links=[])

        add_to_list(api, bulletin)
        with open(TEST_LAST_HASH_PATH, 'r') as f:
            self.assertEqual(f.read(), 'test')
        os.remove(TEST_LAST_HASH_PATH)

    @mock.patch('service.settings.LAST_HASH_PATH', TEST_LAST_HASH_PATH)
    @mock.patch('re.sub')
    @mock.patch('service.get_list.get_current_list_or_create_new')
    @mock.patch('tempfile.NamedTemporaryFile')
    @mock.patch('json.dumps')
    @mock.patch('service.crypto_utils.sign_data')
    def test_get_list_with_hash_from_file(self, sign, dumps, tempfile, get_list, sub):
        """
        Check using hash from LAST_HASH_PATH file
        """
        api = mock.MagicMock()
        api.object_put.return_value.__getitem__.return_value = 'test_hash_1'
        bulletin = mock.Mock()
        sub.return_value = mock.Mock()
        get_list.return_value = dict(Data="List of bulletins", Links=[])
        with open(TEST_LAST_HASH_PATH, 'w') as f:
            f.write('test_hash_2')
        add_to_list(api, bulletin)
        get_list.assert_called_once_with(api, 'test_hash_2')

    @mock.patch('service.settings.LAST_HASH_PATH', TEST_LAST_HASH_PATH)
    @mock.patch('re.sub')
    @mock.patch('service.get_list.get_current_list_or_create_new')
    @mock.patch('tempfile.NamedTemporaryFile')
    @mock.patch('json.dumps')
    @mock.patch('service.crypto_utils.sign_data')
    def test_get_list_with_hash_from_name_resolve(self, sign, dumps, tempfile, get_list, sub):
        """
        Check gettings hash from name_resolve, when LAST_HASH_PATH doesn't exist
        """

        api = mock.MagicMock()
        api.object_put.return_value.__getitem__.return_value = 'test_hash_3'
        bulletin = mock.Mock()
        sub.return_value = mock.Mock()
        get_list.return_value = dict(Data="List of bulletins", Links=[])
        add_to_list(api, bulletin)
        get_list.assert_called_once_with(api, sub.return_value)
