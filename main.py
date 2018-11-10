#!/usr/bin/env python3
# boilerplate CLI from: https://www.python-boilerplate.com/py3+executable
"""

Test:

python main.py 0x06012c8cf97bead5deae237070f9587f8e7a266d --host https://mainnet.infura.io/508a668035334ce5afdbc4e55f918561

"""

import argparse
from web3 import Web3, HTTPProvider
from google.cloud import bigquery

__author__ = "Ed Colmar"
__version__ = "0.1.0"
__license__ = "MIT"

API_KEY = "xxx"
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
    """

    ## Several steps are required in order to accomplish this task.
    ## First, I need to know the transaction that created the contract
    ## Getting this information from the blockchain itself would require looping over transactions to
    ## find the correct one. But, this is expensive and time consuming.
    ##
    ## The prompt only specifies using web3.py "to find the hashes of the
    ## block and transaction" but does not specifically indicate how to get the
    ## transaction itself.  So, I am using Google BigQuery to get the transaction from the contract address

    client = bigquery.Client()
    query_job = client.query("""
        SELECT contracts.address,transactions.block_timestamp, transactions.hash, transactions.block_hash
        FROM `bigquery-public-data.ethereum_blockchain.contracts` AS contracts
        JOIN `bigquery-public-data.ethereum_blockchain.transactions` AS transactions ON (transactions.receipt_contract_address = contracts.address)
        WHERE contracts.address = '%s'
        LIMIT 1
        """ % contract_addr)

    results = query_job.result()  # Waits for job to complete.

    transaction_hash = None
    block_hash = None

    for row in results:
        # there will only be one, but this is an Iterator.
        transaction_hash = row.hash
        block_hash = row.block_hash

    if not transaction_hash:
        print("The contract transaction was not found")
        return

    ## At this point I already have the block and transaction hashes that I need, but in order to satisfy the prompt
    ## I will use Infura to get this data again

    #print("Block: {}".format(block_hash))
    #print("Transaction: {}".format(transaction_hash))

    # Use command line host if entered
    if host:
        #print('Using command line host')
        w3 = Web3(HTTPProvider(host))
    else:
        w3 = Web3(HTTPProvider(NETWORK_URL))

    trans_rcpt = w3.eth.getTransactionReceipt(transaction_hash)
    #print(trans_rcpt)

    transaction_hash = trans_rcpt['transactionHash'].hex()
    block_hash = trans_rcpt['blockHash'].hex()

    print("Block: {}".format(block_hash))
    print("Transaction: {}".format(transaction_hash))
    
    
if __name__ == "__main__":
    """ Return Block Hash and Transaction Hash from a given contract address """

    parser = argparse.ArgumentParser()
    parser.add_argument('contract_addr', help='Contract Address')
    parser.add_argument("--host", help="Infura Network to use", action='store',
                        type=str)
    args = parser.parse_args()
    
    main(args.contract_addr, args.host)
