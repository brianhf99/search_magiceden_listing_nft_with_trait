import requests
from time import sleep
import json


market_contracts = [
    'M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K']  # ME V2 program

s = set()


def handle_request(query):
    resp = requests.get(query)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception('Http request died')



# Extract key parameters from each txn
def handle_MEv2(resp):
    price = 0
    if 'Program log: Instruction: Sell' in resp['logMessage']:
        for i in range(len(resp['logMessage'])):
            if 'price' in resp['logMessage'][i]:
                try:
                    price = json.loads(resp['logMessage'][i][12:])['price'] / 1000000000
                except Exception as e:
                    print(f'Unable to get price due to {e}\n{resp["logMessage"][i]}')
                break
        if len(resp['parsedInstruction']) == 1:
            nft_address = resp['inputAccount'][4]['account']
            if nft_address == '11111111111111111111111111111111':
                nft_address = resp['inputAccount'][5]['account']

            resp = handle_request(f'https://public-api.solscan.io/account/{nft_address}')


            tokenSymbol = resp['tokenInfo']['symbol']

            # modify this for other projects and traits
            traitsQuery = 'Nonsmoker'
            symbolQuery = 'BOHEMIA'

            # -----------------------------------------



            if tokenSymbol == symbolQuery:
                tokenAttr = resp['metadata']['data']['attributes']
                for trait in tokenAttr:
                    strtrait = str(trait)
                    intResult = strtrait.find(traitsQuery, 1)
                    if intResult != -1:

                        # can be sent to email for further notifications

                        print(f'Price: {price}')
                        print(f'Rarity: {traitsQuery}')
                        # print(f'tokenName: {tokenName}')
                        print(resp['tokenInfo']['name'])
                        print(f'tokensymbol: {tokenSymbol}')
                        print(f'https://magiceden.io/item-details/{resp["metadata"]["mint"]}')
                        break


# Fetch sepcific txn
def process_txn(txn, contract):
    h = txn['txHash']
    if h in s:
        return
    s.add(h)
    resp = handle_request(f'https://public-api.solscan.io/transaction/{h}')
    if contract == 'M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K':
        handle_MEv2(resp)
    # print('')


# Poll for txns interacting with ME V2 program
def job():
    try:
        for contract in market_contracts:
            resp = handle_request(f'https://public-api.solscan.io/account/transactions?account={contract}&limit=10')
            for txn in resp:
                process_txn(txn, contract)

    except Exception as e:
        print(f'Http request failed due to {e}')


while True:
    job()
    sleep(100)
