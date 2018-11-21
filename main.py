#!/usr/bin/env python3
# boilerplate CLI from: https://www.python-boilerplate.com/py3+executable
"""

Test:

python main.py 0x06012c8cf97bead5deae237070f9587f8e7a266d --host https://mainnet.infura.io/XXX

"""

import argparse
import math
from web3 import Web3, HTTPProvider

__author__ = "Ed Colmar"
__version__ = "0.1.1"
__license__ = "MIT"

API_KEY = "XXX"
INFURA_NETWORK = "https://mainnet.infura.io/"
NETWORK_URL = INFURA_NETWORK + API_KEY

def main(contract_addr, host):
    """
    The prompt is: Write a python CLI that uses the web3.py module to find the
    hashes of the block and transaction from which a contract address was deployed.
    For your web3 host, please sign up for https://infura.io/ to get an API key.

    For example:

    inputs:
    - contract address
    - web3 host domain (https://mainnet.infura.io/<API_SECRET>)

    outputs:
    - Block Hash
    - Transaction Hash

    Below is an example test case.

    > python main.py 0xcontract_address_here --host https://mainnet.infura.io/<API_SECRET>

    Block: 0xblock_from_which_contract_was_deployed
    Transaction: 0xtransaction_with_which_contract_was deployed

    Additional instructions from Connor:

    If you have time in the next couple weeks, I am wondering if you can find a way to aleter it so it runs quickly using web3.py alone without the call to bigquery.

    A hint is you will want to look at the web3.eth.getCode method and its block_identifier parameter. Feel free to reach out with additional questions, I will be more responsive going forward.


    """

    ## Based on the new instructions, only web3.py may be used.
    ## getCode will return a result only if the supplied block_identifier is newer than the contract
    ## looping over the blockchain is therefore the only solution available.

    # Use command line host if entered
    if host:
        #print('Using command line host')
        w3 = Web3(HTTPProvider(host))
    else:
        w3 = Web3(HTTPProvider(NETWORK_URL))

    contract_addr = w3.toChecksumAddress(contract_addr)
    latest_block = w3.eth.blockNumber


    contract_code = w3.eth.getCode(contract_addr, block_identifier=latest_block)
    if not contract_code:
        print('contract not found')
        return

    #print('found contract')

    ## a valid contract has been found on the latest block
    ## recursively split the list in half, searching again.

    oldest_block_to_check = 0
    newest_block_to_check = latest_block
    scanning = True

    while scanning:
        midpoint = math.ceil((newest_block_to_check + oldest_block_to_check) / 2)
        #print('scanning block: %s' %midpoint)

        if newest_block_to_check == midpoint:
            #print('found origin block')

            origin_block = w3.eth.getBlock(newest_block_to_check)
            ## check the transactions looking for our contractAddress
            for transaction in origin_block['transactions']:
                #print('checking transaction')
                trans_rcpt = w3.eth.getTransactionReceipt(transaction)
                if trans_rcpt['contractAddress'] == contract_addr:
                    transaction_hash = trans_rcpt['transactionHash'].hex()
                    block_hash = trans_rcpt['blockHash'].hex()

                    print("Block: {}".format(block_hash))
                    print("Transaction: {}".format(transaction_hash))

                    return

        contract_code_at_block = w3.eth.getCode(contract_addr, block_identifier=midpoint)
        if contract_code_at_block:
            #print('found contract code at block')
            newest_block_to_check = midpoint
        else:
            #print('contract_code_at_block not found')
            oldest_block_to_check = midpoint

if __name__ == "__main__":
    """ Return Block Hash and Transaction Hash from a given contract address """

    parser = argparse.ArgumentParser()
    parser.add_argument('contract_addr', help='Contract Address')
    parser.add_argument("--host", help="Infura Network to use", action='store',
                        type=str)
    args = parser.parse_args()

    main(args.contract_addr, args.host)
