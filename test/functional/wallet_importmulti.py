#!/usr/bin/env python3
# Copyright (c) 2014-2019 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the importmulti RPC."""
from test_framework.test_framework import BitcoinTestFramework
<<<<<<< HEAD
from test_framework.util import assert_equal, assert_greater_than, assert_raises_rpc_error

class ImportMultiTest (BitcoinTestFramework):
=======
from test_framework.descriptors import descsum_create
from test_framework.util import (
    assert_equal,
    assert_greater_than,
    assert_raises_rpc_error,
)
from test_framework.wallet_util import (
    get_key,
    get_multisig,
    test_address,
)

class ImportMultiTest(BitcoinTestFramework):
>>>>>>> upstream/0.18
    def set_test_params(self):
        self.num_nodes = 2
        self.extra_args = [["-addresstype=legacy"], ["-addresstype=legacy"]]
        self.setup_clean_chain = True

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def setup_network(self):
        self.setup_nodes()

    def run_test (self):
        self.log.info("Mining blocks...")
        self.nodes[0].generate(1)
        self.nodes[1].generate(1)
        timestamp = self.nodes[1].getblock(self.nodes[1].getbestblockhash())['mediantime']

        node0_address1 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())

        #Check only one address
        assert_equal(node0_address1['ismine'], True)

        #Node 1 sync test
        assert_equal(self.nodes[1].getblockcount(),1)

        #Address Test - before import
        address_info = self.nodes[1].getaddressinfo(node0_address1['address'])
        assert_equal(address_info['iswatchonly'], False)
        assert_equal(address_info['ismine'], False)


        # RPC importmulti -----------------------------------------------

        # Bitcoin Address
        self.log.info("Should import an address")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": address['address']
            },
            "timestamp": "now",
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], True)
        assert_equal(address_assert['ismine'], False)
        assert_equal(address_assert['timestamp'], timestamp)
        watchonly_address = address['address']
        watchonly_timestamp = timestamp

        self.log.info("Should not import an invalid address")
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": "not valid address",
            },
            "timestamp": "now",
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -5)
        assert_equal(result[0]['error']['message'], 'Invalid address')

        # ScriptPubKey + internal
        self.log.info("Should import a scriptPubKey with internal flag")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": address['scriptPubKey'],
            "timestamp": "now",
            "internal": True
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], True)
        assert_equal(address_assert['ismine'], False)
        assert_equal(address_assert['timestamp'], timestamp)

        # ScriptPubKey + !internal
        self.log.info("Should not import a scriptPubKey without internal flag")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": address['scriptPubKey'],
            "timestamp": "now",
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -8)
        assert_equal(result[0]['error']['message'], 'Internal must be set for hex scriptPubKey')
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], False)
        assert_equal('timestamp' in address_assert, False)

<<<<<<< HEAD
=======
        # Nonstandard scriptPubKey + !internal
        self.log.info("Should not import a nonstandard scriptPubKey without internal flag")
        nonstandardScriptPubKey = key.p2pkh_script + CScript([OP_NOP]).hex()
        key = get_key(self.nodes[0])
        self.test_importmulti({"scriptPubKey": nonstandardScriptPubKey,
                               "timestamp": "now"},
                              success=False,
                              error_code=-8,
                              error_message='Internal must be set to true for nonstandard scriptPubKey imports.')
        test_address(self.nodes[1],
                     key.p2pkh_addr,
                     iswatchonly=False,
                     ismine=False,
                     timestamp=None)
>>>>>>> 3001cc61cf11e016c403ce83c9cbcfd3efcbcfd9

        # Address + Public key + !Internal
        self.log.info("Should import an address with public key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": address['address']
            },
            "timestamp": "now",
            "pubkeys": [ address['pubkey'] ]
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], True)
        assert_equal(address_assert['ismine'], False)
        assert_equal(address_assert['timestamp'], timestamp)


        # ScriptPubKey + Public key + internal
        self.log.info("Should import a scriptPubKey with internal and with public key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        request = [{
            "scriptPubKey": address['scriptPubKey'],
            "timestamp": "now",
            "pubkeys": [ address['pubkey'] ],
            "internal": True
        }]
        result = self.nodes[1].importmulti(request)
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], True)
        assert_equal(address_assert['ismine'], False)
        assert_equal(address_assert['timestamp'], timestamp)

        # ScriptPubKey + Public key + !internal
        self.log.info("Should not import a scriptPubKey without internal and with public key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        request = [{
            "scriptPubKey": address['scriptPubKey'],
            "timestamp": "now",
            "pubkeys": [ address['pubkey'] ]
        }]
        result = self.nodes[1].importmulti(request)
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -8)
        assert_equal(result[0]['error']['message'], 'Internal must be set for hex scriptPubKey')
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], False)
        assert_equal('timestamp' in address_assert, False)

        # Address + Private key + !watchonly
        self.log.info("Should import an address with private key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": address['address']
            },
            "timestamp": "now",
            "keys": [ self.nodes[0].dumpprivkey(address['address']) ]
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], True)
        assert_equal(address_assert['timestamp'], timestamp)

        self.log.info("Should not import an address with private key if is already imported")
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": address['address']
            },
            "timestamp": "now",
            "keys": [ self.nodes[0].dumpprivkey(address['address']) ]
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -4)
        assert_equal(result[0]['error']['message'], 'The wallet already contains the private key for this address or script')

        # Address + Private key + watchonly
        self.log.info("Should not import an address with private key and with watchonly")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": address['address']
            },
            "timestamp": "now",
            "keys": [ self.nodes[0].dumpprivkey(address['address']) ],
            "watchonly": True
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -8)
        assert_equal(result[0]['error']['message'], 'Incompatibility found between watchonly and keys')
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], False)
        assert_equal('timestamp' in address_assert, False)

        # ScriptPubKey + Private key + internal
        self.log.info("Should import a scriptPubKey with internal and with private key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": address['scriptPubKey'],
            "timestamp": "now",
            "keys": [ self.nodes[0].dumpprivkey(address['address']) ],
            "internal": True
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], True)
        assert_equal(address_assert['timestamp'], timestamp)

        # ScriptPubKey + Private key + !internal
        self.log.info("Should not import a scriptPubKey without internal and with private key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": address['scriptPubKey'],
            "timestamp": "now",
            "keys": [ self.nodes[0].dumpprivkey(address['address']) ]
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -8)
        assert_equal(result[0]['error']['message'], 'Internal must be set for hex scriptPubKey')
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], False)
        assert_equal('timestamp' in address_assert, False)


        # P2SH address
        sig_address_1 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        sig_address_2 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        sig_address_3 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        multi_sig_script = self.nodes[0].createmultisig(2, [sig_address_1['pubkey'], sig_address_2['pubkey'], sig_address_3['pubkey']])
        self.nodes[1].generate(100)
        self.nodes[1].sendtoaddress(multi_sig_script['address'], 10.00)
        self.nodes[1].generate(1)
        timestamp = self.nodes[1].getblock(self.nodes[1].getbestblockhash())['mediantime']

        self.log.info("Should import a p2sh")
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": multi_sig_script['address']
            },
            "timestamp": "now",
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(multi_sig_script['address'])
        assert_equal(address_assert['isscript'], True)
        assert_equal(address_assert['iswatchonly'], True)
        assert_equal(address_assert['timestamp'], timestamp)
        p2shunspent = self.nodes[1].listunspent(0,999999, [multi_sig_script['address']])[0]
        assert_equal(p2shunspent['spendable'], False)
        assert_equal(p2shunspent['solvable'], False)


        # P2SH + Redeem script
        sig_address_1 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        sig_address_2 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        sig_address_3 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        multi_sig_script = self.nodes[0].createmultisig(2, [sig_address_1['pubkey'], sig_address_2['pubkey'], sig_address_3['pubkey']])
        self.nodes[1].generate(100)
        self.nodes[1].sendtoaddress(multi_sig_script['address'], 10.00)
        self.nodes[1].generate(1)
        timestamp = self.nodes[1].getblock(self.nodes[1].getbestblockhash())['mediantime']

        self.log.info("Should import a p2sh with respective redeem script")
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": multi_sig_script['address']
            },
            "timestamp": "now",
            "redeemscript": multi_sig_script['redeemScript']
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(multi_sig_script['address'])
        assert_equal(address_assert['timestamp'], timestamp)

        p2shunspent = self.nodes[1].listunspent(0,999999, [multi_sig_script['address']])[0]
        assert_equal(p2shunspent['spendable'], False)
        assert_equal(p2shunspent['solvable'], True)


        # P2SH + Redeem script + Private Keys + !Watchonly
        sig_address_1 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        sig_address_2 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        sig_address_3 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        multi_sig_script = self.nodes[0].createmultisig(2, [sig_address_1['pubkey'], sig_address_2['pubkey'], sig_address_3['pubkey']])
        self.nodes[1].generate(100)
        self.nodes[1].sendtoaddress(multi_sig_script['address'], 10.00)
        self.nodes[1].generate(1)
        timestamp = self.nodes[1].getblock(self.nodes[1].getbestblockhash())['mediantime']

        self.log.info("Should import a p2sh with respective redeem script and private keys")
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": multi_sig_script['address']
            },
            "timestamp": "now",
            "redeemscript": multi_sig_script['redeemScript'],
            "keys": [ self.nodes[0].dumpprivkey(sig_address_1['address']), self.nodes[0].dumpprivkey(sig_address_2['address'])]
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(multi_sig_script['address'])
        assert_equal(address_assert['timestamp'], timestamp)

        p2shunspent = self.nodes[1].listunspent(0,999999, [multi_sig_script['address']])[0]
        assert_equal(p2shunspent['spendable'], False)
        assert_equal(p2shunspent['solvable'], True)

        # P2SH + Redeem script + Private Keys + Watchonly
        sig_address_1 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        sig_address_2 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        sig_address_3 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        multi_sig_script = self.nodes[0].createmultisig(2, [sig_address_1['pubkey'], sig_address_2['pubkey'], sig_address_3['pubkey']])
        self.nodes[1].generate(100)
        self.nodes[1].sendtoaddress(multi_sig_script['address'], 10.00)
        self.nodes[1].generate(1)
        timestamp = self.nodes[1].getblock(self.nodes[1].getbestblockhash())['mediantime']

        self.log.info("Should import a p2sh with respective redeem script and private keys")
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": multi_sig_script['address']
            },
            "timestamp": "now",
            "redeemscript": multi_sig_script['redeemScript'],
            "keys": [ self.nodes[0].dumpprivkey(sig_address_1['address']), self.nodes[0].dumpprivkey(sig_address_2['address'])],
            "watchonly": True
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -8)
        assert_equal(result[0]['error']['message'], 'Incompatibility found between watchonly and keys')


        # Address + Public key + !Internal + Wrong pubkey
        self.log.info("Should not import an address with a wrong public key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        address2 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": address['address']
            },
            "timestamp": "now",
            "pubkeys": [ address2['pubkey'] ]
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -5)
        assert_equal(result[0]['error']['message'], 'Consistency check failed')
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], False)
        assert_equal('timestamp' in address_assert, False)


        # ScriptPubKey + Public key + internal + Wrong pubkey
        self.log.info("Should not import a scriptPubKey with internal and with a wrong public key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        address2 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        request = [{
            "scriptPubKey": address['scriptPubKey'],
            "timestamp": "now",
            "pubkeys": [ address2['pubkey'] ],
            "internal": True
        }]
        result = self.nodes[1].importmulti(request)
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -5)
        assert_equal(result[0]['error']['message'], 'Consistency check failed')
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], False)
        assert_equal('timestamp' in address_assert, False)


        # Address + Private key + !watchonly + Wrong private key
        self.log.info("Should not import an address with a wrong private key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        address2 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": address['address']
            },
            "timestamp": "now",
            "keys": [ self.nodes[0].dumpprivkey(address2['address']) ]
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -5)
        assert_equal(result[0]['error']['message'], 'Consistency check failed')
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], False)
        assert_equal('timestamp' in address_assert, False)


        # ScriptPubKey + Private key + internal + Wrong private key
        self.log.info("Should not import a scriptPubKey with internal and with a wrong private key")
        address = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        address2 = self.nodes[0].getaddressinfo(self.nodes[0].getnewaddress())
        result = self.nodes[1].importmulti([{
            "scriptPubKey": address['scriptPubKey'],
            "timestamp": "now",
            "keys": [ self.nodes[0].dumpprivkey(address2['address']) ],
            "internal": True
        }])
        assert_equal(result[0]['success'], False)
        assert_equal(result[0]['error']['code'], -5)
        assert_equal(result[0]['error']['message'], 'Consistency check failed')
        address_assert = self.nodes[1].getaddressinfo(address['address'])
        assert_equal(address_assert['iswatchonly'], False)
        assert_equal(address_assert['ismine'], False)
        assert_equal('timestamp' in address_assert, False)


        # Importing existing watch only address with new timestamp should replace saved timestamp.
        assert_greater_than(timestamp, watchonly_timestamp)
        self.log.info("Should replace previously saved watch only timestamp.")
        result = self.nodes[1].importmulti([{
            "scriptPubKey": {
                "address": watchonly_address,
            },
            "timestamp": "now",
        }])
        assert_equal(result[0]['success'], True)
        address_assert = self.nodes[1].getaddressinfo(watchonly_address)
        assert_equal(address_assert['iswatchonly'], True)
        assert_equal(address_assert['ismine'], False)
        assert_equal(address_assert['timestamp'], timestamp)
        watchonly_timestamp = timestamp


        # restart nodes to check for proper serialization/deserialization of watch only address
        self.stop_nodes()
        self.start_nodes()
        address_assert = self.nodes[1].getaddressinfo(watchonly_address)
        assert_equal(address_assert['iswatchonly'], True)
        assert_equal(address_assert['ismine'], False)
        assert_equal(address_assert['timestamp'], watchonly_timestamp)

        # Bad or missing timestamps
        self.log.info("Should throw on invalid or missing timestamp values")
        assert_raises_rpc_error(-3, 'Missing required timestamp field for key',
            self.nodes[1].importmulti, [{
                "scriptPubKey": address['scriptPubKey'],
            }])
        assert_raises_rpc_error(-3, 'Expected number or "now" timestamp value for key. got type string',
<<<<<<< HEAD
            self.nodes[1].importmulti, [{
                "scriptPubKey": address['scriptPubKey'],
                "timestamp": "",
            }])
=======
                                self.nodes[1].importmulti, [{
                                    "scriptPubKey": key.p2pkh_script,
                                    "timestamp": ""
                                }])

        # Import P2WPKH address as watch only
        self.log.info("Should import a P2WPKH address as watch only")
        key = get_key(self.nodes[0])
        self.test_importmulti({"scriptPubKey": {"address": key.p2wpkh_addr},
                               "timestamp": "now"},
                              success=True)
        test_address(self.nodes[1],
                     key.p2wpkh_addr,
                     iswatchonly=True,
                     solvable=False)

        # Import P2WPKH address with public key but no private key
        self.log.info("Should import a P2WPKH address and public key as solvable but not spendable")
        key = get_key(self.nodes[0])
        self.test_importmulti({"scriptPubKey": {"address": key.p2wpkh_addr},
                               "timestamp": "now",
                               "pubkeys": [key.pubkey]},
                              success=True,
                              warnings=["Some private keys are missing, outputs will be considered watchonly. If this is intentional, specify the watchonly flag."])
        test_address(self.nodes[1],
                     key.p2wpkh_addr,
                     ismine=False,
                     solvable=True)

        # Import P2WPKH address with key and check it is spendable
        self.log.info("Should import a P2WPKH address with key")
        key = get_key(self.nodes[0])
        self.test_importmulti({"scriptPubKey": {"address": key.p2wpkh_addr},
                               "timestamp": "now",
                               "keys": [key.privkey]},
                              success=True)
        test_address(self.nodes[1],
                     key.p2wpkh_addr,
                     iswatchonly=False,
                     ismine=True)

        # P2WSH multisig address without scripts or keys
        multisig = get_multisig(self.nodes[0])
        self.log.info("Should import a p2wsh multisig as watch only without respective redeem script and private keys")
        self.test_importmulti({"scriptPubKey": {"address": multisig.p2wsh_addr},
                               "timestamp": "now"},
                              success=True)
        test_address(self.nodes[1],
                     multisig.p2sh_addr,
                     solvable=False)

        # Same P2WSH multisig address as above, but now with witnessscript + private keys
        self.log.info("Should import a p2wsh with respective witness script and private keys")
        self.test_importmulti({"scriptPubKey": {"address": multisig.p2wsh_addr},
                               "timestamp": "now",
                               "witnessscript": multisig.redeem_script,
                               "keys": multisig.privkeys},
                              success=True)
        test_address(self.nodes[1],
                     multisig.p2sh_addr,
                     solvable=True,
                     ismine=True,
                     sigsrequired=2)

        # P2SH-P2WPKH address with no redeemscript or public or private key
        key = get_key(self.nodes[0])
        self.log.info("Should import a p2sh-p2wpkh without redeem script or keys")
        self.test_importmulti({"scriptPubKey": {"address": key.p2sh_p2wpkh_addr},
                               "timestamp": "now"},
                              success=True)
        test_address(self.nodes[1],
                     key.p2sh_p2wpkh_addr,
                     solvable=False,
                     ismine=False)

        # P2SH-P2WPKH address + redeemscript + public key with no private key
        self.log.info("Should import a p2sh-p2wpkh with respective redeem script and pubkey as solvable")
        self.test_importmulti({"scriptPubKey": {"address": key.p2sh_p2wpkh_addr},
                               "timestamp": "now",
                               "redeemscript": key.p2sh_p2wpkh_redeem_script,
                               "pubkeys": [key.pubkey]},
                              success=True,
                              warnings=["Some private keys are missing, outputs will be considered watchonly. If this is intentional, specify the watchonly flag."])
        test_address(self.nodes[1],
                     key.p2sh_p2wpkh_addr,
                     solvable=True,
                     ismine=False)

        # P2SH-P2WPKH address + redeemscript + private key
        key = get_key(self.nodes[0])
        self.log.info("Should import a p2sh-p2wpkh with respective redeem script and private keys")
        self.test_importmulti({"scriptPubKey": {"address": key.p2sh_p2wpkh_addr},
                               "timestamp": "now",
                               "redeemscript": key.p2sh_p2wpkh_redeem_script,
                               "keys": [key.privkey]},
                              success=True)
        test_address(self.nodes[1],
                     key.p2sh_p2wpkh_addr,
                     solvable=True,
                     ismine=True)

        # P2SH-P2WSH multisig + redeemscript with no private key
        multisig = get_multisig(self.nodes[0])
        self.log.info("Should import a p2sh-p2wsh with respective redeem script but no private key")
        self.test_importmulti({"scriptPubKey": {"address": multisig.p2sh_p2wsh_addr},
                               "timestamp": "now",
                               "redeemscript": multisig.p2wsh_script,
                               "witnessscript": multisig.redeem_script},
                              success=True,
                              warnings=["Some private keys are missing, outputs will be considered watchonly. If this is intentional, specify the watchonly flag."])
        test_address(self.nodes[1],
                     multisig.p2sh_p2wsh_addr,
                     solvable=True,
                     ismine=False)

        # Test importing of a P2SH-P2WPKH address via descriptor + private key
        key = get_key(self.nodes[0])
        self.log.info("Should not import a p2sh-p2wpkh address from descriptor without checksum and private key")
        self.test_importmulti({"desc": "sh(wpkh(" + key.pubkey + "))",
                               "timestamp": "now",
                               "label": "Descriptor import test",
                               "keys": [key.privkey]},
                              success=False,
                              error_code=-5,
                              error_message="Descriptor is invalid")

        # Test importing of a P2SH-P2WPKH address via descriptor + private key
        key = get_key(self.nodes[0])
        self.log.info("Should import a p2sh-p2wpkh address from descriptor and private key")
        self.test_importmulti({"desc": descsum_create("sh(wpkh(" + key.pubkey + "))"),
                               "timestamp": "now",
                               "label": "Descriptor import test",
                               "keys": [key.privkey]},
                              success=True)
        test_address(self.nodes[1],
                     key.p2sh_p2wpkh_addr,
                     solvable=True,
                     ismine=True,
                     label="Descriptor import test")

        # Test ranged descriptor fails if range is not specified
        xpriv = "tprv8ZgxMBicQKsPeuVhWwi6wuMQGfPKi9Li5GtX35jVNknACgqe3CY4g5xgkfDDJcmtF7o1QnxWDRYw4H5P26PXq7sbcUkEqeR4fg3Kxp2tigg"
        addresses = ["2N7yv4p8G8yEaPddJxY41kPihnWvs39qCMf", "2MsHxyb2JS3pAySeNUsJ7mNnurtpeenDzLA"] # hdkeypath=m/0'/0'/0' and 1'
        desc = "sh(wpkh(" + xpriv + "/0'/0'/*'" + "))"
        self.log.info("Ranged descriptor import should fail without a specified range")
        self.test_importmulti({"desc": descsum_create(desc),
                               "timestamp": "now"},
                              success=False,
                              error_code=-8,
                              error_message='Descriptor is ranged, please specify the range')

        # Test importing of a ranged descriptor without keys
        self.log.info("Should import the ranged descriptor with specified range as solvable")
        self.test_importmulti({"desc": descsum_create(desc),
                               "timestamp": "now",
                               "range": 1},
                              success=True,
                              warnings=["Some private keys are missing, outputs will be considered watchonly. If this is intentional, specify the watchonly flag."])
        for address in addresses:
            test_address(self.nodes[1],
                         key.p2sh_p2wpkh_addr,
                         solvable=True)

        self.test_importmulti({"desc": descsum_create(desc), "timestamp": "now", "range": -1},
                              success=False, error_code=-8, error_message='End of range is too high')

        self.test_importmulti({"desc": descsum_create(desc), "timestamp": "now", "range": [-1, 10]},
                              success=False, error_code=-8, error_message='Range should be greater or equal than 0')

        self.test_importmulti({"desc": descsum_create(desc), "timestamp": "now", "range": [(2 << 31 + 1) - 1000000, (2 << 31 + 1)]},
                              success=False, error_code=-8, error_message='End of range is too high')

        self.test_importmulti({"desc": descsum_create(desc), "timestamp": "now", "range": [2, 1]},
                              success=False, error_code=-8, error_message='Range specified as [begin,end] must not have begin after end')

        self.test_importmulti({"desc": descsum_create(desc), "timestamp": "now", "range": [0, 1000001]},
                              success=False, error_code=-8, error_message='Range is too large')

        # Test importing of a P2PKH address via descriptor
        key = get_key(self.nodes[0])
        self.log.info("Should import a p2pkh address from descriptor")
        self.test_importmulti({"desc": descsum_create("pkh(" + key.pubkey + ")"),
                               "timestamp": "now",
                               "label": "Descriptor import test"},
                              True,
                              warnings=["Some private keys are missing, outputs will be considered watchonly. If this is intentional, specify the watchonly flag."])
        test_address(self.nodes[1],
                     key.p2pkh_addr,
                     solvable=True,
                     ismine=False,
                     label="Descriptor import test")

        # Test import fails if both desc and scriptPubKey are provided
        key = get_key(self.nodes[0])
        self.log.info("Import should fail if both scriptPubKey and desc are provided")
        self.test_importmulti({"desc": descsum_create("pkh(" + key.pubkey + ")"),
                               "scriptPubKey": {"address": key.p2pkh_addr},
                               "timestamp": "now"},
                              success=False,
                              error_code=-8,
                              error_message='Both a descriptor and a scriptPubKey should not be provided.')

        # Test import fails if neither desc nor scriptPubKey are present
        key = get_key(self.nodes[0])
        self.log.info("Import should fail if neither a descriptor nor a scriptPubKey are provided")
        self.test_importmulti({"timestamp": "now"},
                              success=False,
                              error_code=-8,
                              error_message='Either a descriptor or scriptPubKey must be provided.')

        # Test importing of a multisig via descriptor
        key1 = get_key(self.nodes[0])
        key2 = get_key(self.nodes[0])
        self.log.info("Should import a 1-of-2 bare multisig from descriptor")
        self.test_importmulti({"desc": descsum_create("multi(1," + key1.pubkey + "," + key2.pubkey + ")"),
                               "timestamp": "now"},
                              success=True,
                              warnings=["Some private keys are missing, outputs will be considered watchonly. If this is intentional, specify the watchonly flag."])
        self.log.info("Should not treat individual keys from the imported bare multisig as watchonly")
        test_address(self.nodes[1],
                     key1.p2pkh_addr,
                     ismine=False,
                     iswatchonly=False)
>>>>>>> upstream/0.18

        # Import pubkeys with key origin info
        self.log.info("Addresses should have hd keypath and master key id after import with key origin")
        pub_addr = self.nodes[1].getnewaddress()
        pub_addr = self.nodes[1].getnewaddress()
        info = self.nodes[1].getaddressinfo(pub_addr)
        pub = info['pubkey']
        pub_keypath = info['hdkeypath']
        pub_fpr = info['hdmasterfingerprint']
        result = self.nodes[0].importmulti(
            [{
                'desc' : descsum_create("wpkh([" + pub_fpr + pub_keypath[1:] +"]" + pub + ")"),
                "timestamp": "now",
            }]
        )
        assert result[0]['success']
        pub_import_info = self.nodes[0].getaddressinfo(pub_addr)
        assert_equal(pub_import_info['hdmasterfingerprint'], pub_fpr)
        assert_equal(pub_import_info['pubkey'], pub)
        assert_equal(pub_import_info['hdkeypath'], pub_keypath)

        # Import privkeys with key origin info
        priv_addr = self.nodes[1].getnewaddress()
        info = self.nodes[1].getaddressinfo(priv_addr)
        priv = self.nodes[1].dumpprivkey(priv_addr)
        priv_keypath = info['hdkeypath']
        priv_fpr = info['hdmasterfingerprint']
        result = self.nodes[0].importmulti(
            [{
                'desc' : descsum_create("wpkh([" + priv_fpr + priv_keypath[1:] + "]" + priv + ")"),
                "timestamp": "now",
            }]
        )
        assert result[0]['success']
        priv_import_info = self.nodes[0].getaddressinfo(priv_addr)
        assert_equal(priv_import_info['hdmasterfingerprint'], priv_fpr)
        assert_equal(priv_import_info['hdkeypath'], priv_keypath)

        # Make sure the key origin info are still there after a restart
        self.stop_nodes()
        self.start_nodes()
        import_info = self.nodes[0].getaddressinfo(pub_addr)
        assert_equal(import_info['hdmasterfingerprint'], pub_fpr)
        assert_equal(import_info['hdkeypath'], pub_keypath)
        import_info = self.nodes[0].getaddressinfo(priv_addr)
        assert_equal(import_info['hdmasterfingerprint'], priv_fpr)
        assert_equal(import_info['hdkeypath'], priv_keypath)

        # Check legacy import does not import key origin info
        self.log.info("Legacy imports don't have key origin info")
        pub_addr = self.nodes[1].getnewaddress()
        info = self.nodes[1].getaddressinfo(pub_addr)
        pub = info['pubkey']
        result = self.nodes[0].importmulti(
            [{
                'scriptPubKey': {'address': pub_addr},
                'pubkeys': [pub],
                "timestamp": "now",
            }]
        )
        assert result[0]['success']
        pub_import_info = self.nodes[0].getaddressinfo(pub_addr)
        assert_equal(pub_import_info['pubkey'], pub)
        assert 'hdmasterfingerprint' not in pub_import_info
        assert 'hdkeypath' not in pub_import_info

        # Import some public keys to the keypool of a no privkey wallet
        self.log.info("Adding pubkey to keypool of disableprivkey wallet")
        self.nodes[1].createwallet(wallet_name="noprivkeys", disable_private_keys=True)
        wrpc = self.nodes[1].get_wallet_rpc("noprivkeys")

        addr1 = self.nodes[0].getnewaddress()
        addr2 = self.nodes[0].getnewaddress()
        pub1 = self.nodes[0].getaddressinfo(addr1)['pubkey']
        pub2 = self.nodes[0].getaddressinfo(addr2)['pubkey']
        result = wrpc.importmulti(
            [{
                'desc': descsum_create('wpkh(' + pub1 + ')'),
                'keypool': True,
                "timestamp": "now",
            },
            {
                'desc': descsum_create('wpkh(' + pub2 + ')'),
                'keypool': True,
                "timestamp": "now",
            }]
        )
        assert result[0]['success']
        assert result[1]['success']
        assert_equal(wrpc.getwalletinfo()["keypoolsize"], 2)
        newaddr1 = wrpc.getnewaddress()
        assert_equal(addr1, newaddr1)
        newaddr2 = wrpc.getnewaddress()
        assert_equal(addr2, newaddr2)

        # Import some public keys to the internal keypool of a no privkey wallet
        self.log.info("Adding pubkey to internal keypool of disableprivkey wallet")
        addr1 = self.nodes[0].getnewaddress()
        addr2 = self.nodes[0].getnewaddress()
        pub1 = self.nodes[0].getaddressinfo(addr1)['pubkey']
        pub2 = self.nodes[0].getaddressinfo(addr2)['pubkey']
        result = wrpc.importmulti(
            [{
                'desc': descsum_create('wpkh(' + pub1 + ')'),
                'keypool': True,
                'internal': True,
                "timestamp": "now",
            },
            {
                'desc': descsum_create('wpkh(' + pub2 + ')'),
                'keypool': True,
                'internal': True,
                "timestamp": "now",
            }]
        )
        assert result[0]['success']
        assert result[1]['success']
        assert_equal(wrpc.getwalletinfo()["keypoolsize_hd_internal"], 2)
        newaddr1 = wrpc.getrawchangeaddress()
        assert_equal(addr1, newaddr1)
        newaddr2 = wrpc.getrawchangeaddress()
        assert_equal(addr2, newaddr2)

        # Import a multisig and make sure the keys don't go into the keypool
        self.log.info('Imported scripts with pubkeys should not have their pubkeys go into the keypool')
        addr1 = self.nodes[0].getnewaddress()
        addr2 = self.nodes[0].getnewaddress()
        pub1 = self.nodes[0].getaddressinfo(addr1)['pubkey']
        pub2 = self.nodes[0].getaddressinfo(addr2)['pubkey']
        result = wrpc.importmulti(
            [{
                'desc': descsum_create('wsh(multi(2,' + pub1 + ',' + pub2 + '))'),
                'keypool': True,
                "timestamp": "now",
            }]
        )
        assert result[0]['success']
        assert_equal(wrpc.getwalletinfo()["keypoolsize"], 0)

        # Cannot import those pubkeys to keypool of wallet with privkeys
        self.log.info("Pubkeys cannot be added to the keypool of a wallet with private keys")
        wrpc = self.nodes[1].get_wallet_rpc("")
        assert wrpc.getwalletinfo()['private_keys_enabled']
        result = wrpc.importmulti(
            [{
                'desc': descsum_create('wpkh(' + pub1 + ')'),
                'keypool': True,
                "timestamp": "now",
            }]
        )
        assert_equal(result[0]['error']['code'], -8)
        assert_equal(result[0]['error']['message'], "Keys can only be imported to the keypool when private keys are disabled")

        # Make sure ranged imports import keys in order
        self.log.info('Key ranges should be imported in order')
        wrpc = self.nodes[1].get_wallet_rpc("noprivkeys")
        assert_equal(wrpc.getwalletinfo()["keypoolsize"], 0)
        assert_equal(wrpc.getwalletinfo()["private_keys_enabled"], False)
        xpub = "tpubDAXcJ7s7ZwicqjprRaEWdPoHKrCS215qxGYxpusRLLmJuT69ZSicuGdSfyvyKpvUNYBW1s2U3NSrT6vrCYB9e6nZUEvrqnwXPF8ArTCRXMY"
        addresses = [
            'bcrt1qtmp74ayg7p24uslctssvjm06q5phz4yrxucgnv', # m/0'/0'/0
            'bcrt1q8vprchan07gzagd5e6v9wd7azyucksq2xc76k8', # m/0'/0'/1
            'bcrt1qtuqdtha7zmqgcrr26n2rqxztv5y8rafjp9lulu', # m/0'/0'/2
            'bcrt1qau64272ymawq26t90md6an0ps99qkrse58m640', # m/0'/0'/3
            'bcrt1qsg97266hrh6cpmutqen8s4s962aryy77jp0fg0', # m/0'/0'/4
        ]
        result = wrpc.importmulti(
            [{
                'desc': descsum_create('wpkh([80002067/0h/0h]' + xpub + '/*)'),
                'keypool': True,
                'timestamp': 'now',
                'range' : [0, 4],
            }]
        )
        for i in range(0, 5):
            addr = wrpc.getnewaddress('', 'bech32')
            assert_equal(addr, addresses[i])

if __name__ == '__main__':
    ImportMultiTest ().main ()
