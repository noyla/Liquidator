import traceback
from dotenv import load_dotenv

# import uint
from web3 import Web3
import json

# PROVIDER_URL = "https://speedy-nodes-nyc.moralis.io/81b3a1be5e6aebb3bbde9e23/eth/kovan"
PROVIDER_URL = "https://kovan.infura.io/v3/cf34bf113ea14801a4d33a9db6822e5b"
DAI_KOVAN_ADDRESS = '0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD' # DAI token Kovan testnet address
# DAI_KOVAN_ADDRESS = '0xfdf7f21EDA1fB8AeBEd2FC8b0e8F72a8f17cf823' # DAI token Kovan testnet address
BUSD_KOVAN_ADDRESS = '0x4c6E1EFC12FDfD568186b7BAEc0A43fFfb4bCcCf' # Bincance USD Kovan testnet address
# AAVE_TOKEN_KOVAN_ADDRESS = '0x1d70fE7272F07E38e4bE71636e711bC007341273' # AAVE Kovan testnet address
AAVE_TOKEN_KOVAN_ADDRESS = '0xB597cd8D3217ea6477232F9217fa70837ff667Af' # AAVE Kovan testnet address
# BUSD_KOVAN_ADDRESS = '0x73eF351Ed451A52CB2D9651eCDE4b72520d343bE' # Bincance USD Kovan testnet address
# BUSD_KOVAN_ADDRESS = '0x822f658628169239d4a07afd1d392c6d7e7cc1d5' # Bincance USD Kovan testnet address
LENDINGPOOL_KOVAN_CONTRACT_ADDRESS = '0xE0fBa4Fc209b4948668006B2bE61711b7f465bAe'
PROTOCOL_DATA_PROVIDER = '0x3c73A5E5785cAC854D468F727c606C07488a29D6'
# Borrow / Deposit / Repay / LiquidationCall
# LENDINGPOOL_KOVAN_ABI = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"reserve","type":"address"},{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"repayer","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Repay","type":"event"},'
#                               '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"reserve","type":"address"},{"indexed":false,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"onBehalfOf","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"borrowRateMode","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"borrowRate","type":"uint256"},{"indexed":true,"internalType":"uint16","name":"referral","type":"uint16"}],"name":"Borrow","type":"event"},'
#                               '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"reserve","type":"address"},{"indexed":false,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"onBehalfOf","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"uint16","name":"referral","type":"uint16"}],"name":"Deposit","type":"event"},'
#                               '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"collateralAsset","type":"address"},{"indexed":true,"internalType":"address","name":"debtAsset","type":"address"},{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"debtToCover","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"liquidatedCollateralAmount","type":"uint256"},{"indexed":false,"internalType":"address","name":"liquidator","type":"address"},{"indexed":false,"internalType":"bool","name":"receiveAToken","type":"bool"}],"name":"LiquidationCall","type":"event"},'
#                               '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"target","type":"address"},{"indexed":true,"internalType":"address","name":"initiator","type":"address"},{"indexed":true,"internalType":"address","name":"asset","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"premium","type":"uint256"},{"indexed":false,"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"FlashLoan","type":"event"},'
#                               '{AAVE_ETHER_CONVERSION"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserAccountData","outputs":[{"internalType":"uint256","name":"totalCollateralETH","type":"uint256"},{"internalType":"uint256","name":"totalDebtETH","type":"uint256"},{"internalType":"uint256","name":"availableBorrowsETH","type":"uint256"},{"internalType":"uint256","name":"currentLiquidationThreshold","type":"uint256"},{"internalType":"uint256","name":"ltv","type":"uint256"},{"internalType":"uint256","name":"healthFactor","type":"uint256"}],"stateMutability":"view","type":"function"}]')
TESTNET_WALLET = '0x9998b4021d410c1E8A7C512EF68c9d613B5B1667'
LIQUIDATOR_WALLET = '0xaa29b6365eAC1FFf89e82ae24dDf704293ef3bbB'

LIQUIDATION_CLOSE_FACTOR = 0.5
AAVE_ETHER_CONVERSION = 0.0566
DAI_ETHER_CONVERSION = 0.000345


w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
w3.eth.handleRevert = True

def loadAbi(abi):
    return json.load(open("./abis/%s"%(abi)))

def getContractInstance(address, abiFile):
    return w3.eth.contract(address, abi=loadAbi(abiFile))


def exec_contract(account, nonce, func):
    """
    Call a contract that commits a transaction
    """
    try:
        transaction = func.buildTransaction({'from': account.address, 'nonce': nonce})
                                             # 'gas': 2500000, 'gasPrice': 2500000})#estimated_gas, #2000000,})
        # transaction = func.buildTransaction({'from': account.address, 'nonce': nonce})
        signed = account.signTransaction(transaction)#, '5de576d650dcdbfc7a1d3e947c636ca4e6c9c2df19e40be99e249b9e24d9b06f')
        trans_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        if trans_hash:
            tx_receipt = w3.eth.waitForTransactionReceipt(trans_hash, timeout=60)
    except:
        traceback.print_exc()
        return None
    print("Transaction hash for func %s. %s" % (func, trans_hash.hex()))
    return trans_hash.hex()

def liquidate(borrower, liquidator_account, amountAave = -1):
    try:
        # allowance = 0
        borrower_aave_user_data = protocolDataProvider.functions.getUserReserveData(aave_address, borrower).call()
        borrower_aave_user_data = {'currentATokenBalance': borrower_aave_user_data[0], 'currentStableDebt': borrower_aave_user_data[1],
                     'currentVariableDebt': borrower_aave_user_data[2], 'principalStableDebt': borrower_aave_user_data[3],
                     'scaledVariableDebt': borrower_aave_user_data[4], 'stableBorrowRate': borrower_aave_user_data[5],
                     'liquidityRate': borrower_aave_user_data[6], 'stableRateLastUpdated': borrower_aave_user_data[7],
                     'usageAsCollateralEnabled': borrower_aave_user_data[8]}
        borrower_dai_user_data = protocolDataProvider.functions.getUserReserveData(dai_address, borrower).call()
        borrower_dai_user_data = {'currentATokenBalance': borrower_dai_user_data[0], 'currentStableDebt': borrower_dai_user_data[1],
                                   'currentVariableDebt': borrower_dai_user_data[2], 'principalStableDebt': borrower_dai_user_data[3],
                                   'scaledVariableDebt': borrower_dai_user_data[4], 'stableBorrowRate': borrower_dai_user_data[5],
                                   'liquidityRate': borrower_dai_user_data[6], 'stableRateLastUpdated': borrower_dai_user_data[7],
                                   'usageAsCollateralEnabled': borrower_dai_user_data[8]}
        print(borrower_dai_user_data)
        if not borrower_dai_user_data or not borrower_dai_user_data.get('usageAsCollateralEnabled'):
            return

            pass
        # Approve lendingPool to spend liquidator's funds
        allowance_before = aave.functions.allowance(liquidator_account.address, lendingPool.address).call()
        # if allowance <= 0:

        nonce = w3.eth.getTransactionCount(liquidator_account.address)
        debtToCover = (borrower_aave_user_data['currentStableDebt'] + borrower_aave_user_data['currentVariableDebt']) * \
                      LIQUIDATION_CLOSE_FACTOR
        debtToCover = w3.toWei(1, 'ether')
        approval_hash = exec_contract(liquidator_account, nonce, aave.functions.approve(lendingPool.address, debtToCover*2))

        # c = w3.eth.getBalance(liquidator_account.address)
        # balance = aave.functions.balanceOf(liquidator_account.address).call()

        liquidation_func = lendingPool.functions.liquidationCall(
            dai.address,
            aave.address,
            borrower,
            debtToCover,#w3.toHex(-1),# amountAave,
            # w3.toWei(amountAave * AAVE_ETHER_CONVERSION, 'ether'),
            False
        )
        # allowance_after = aave.functions.allowance(, lendingPool.address).call()
        nonce = w3.eth.getTransactionCount(liquidator_account.address)
        tx_hash = exec_contract(liquidator_account,nonce, liquidation_func)
        print("Transaction accepted. %s" % tx_hash)
    except Exception as e:
        print(e)

def transfer(user, liquidator, amountDai):
    # estimated_gas = w3.eth.estimateGas(txn)
    # 'gas': 21000, 'gasPrice': 210000
    transfer_transaction = {
        'from': liquidator,
        'to': user,
        'value': w3.toWei(amountDai * 0.000345, 'ether'),
        'nonce': w3.eth.getTransactionCount("0xaa29b6365eAC1FFf89e82ae24dDf704293ef3bbB"),
        'gas': 25000, #estimated_gas, #2000000,
        'gasPrice': 210000
        #'chainId': None,
    }
    signed_transaction = w3.eth.account.signTransaction(transfer_transaction, "5de576d650dcdbfc7a1d3e947c636ca4e6c9c2df19e40be99e249b9e24d9b06f")
    # hex = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)

# dai = getContractInstance(DAI_KOVAN_ADDRESS, "DAI.json")
# busd = getContractInstance(BUSD_KOVAN_ADDRESS, "BUSD.json")
# aave = getContractInstance(AAVE_TOKEN_KOVAN_ADDRESS, "AAVE.json")

lendingPoolAddressProviderRegistry = getContractInstance("0x1E40B561EC587036f9789aF83236f057D1ed2A90",
                                                         "LENDING_POOL_PROVIDER_REGISTRY.json")
lendingPool_providers = lendingPoolAddressProviderRegistry.functions.getAddressesProvidersList().call()
# try:
lendingpool_provider_address = next(filter(lambda provider: provider != '0x0000000000000000000000000000000000000000',
                                           lendingPool_providers))
# except StopIteration:
#     pass
lendingPoolAddressProvider = getContractInstance(lendingpool_provider_address, "LENDING_POOL_PROVIDER.json") # Kovan
# lendingPoolAddressProvider = getContractInstance("0x88757f2f99175387aB4C6a4b3067c77A695b0349", "LENDING_POOL_PROVIDER.json") # Kovan
# lendingPool_address = '0x2646FcF7F0AbB1ff279ED9845AdE04019C907EBE'
lendingPool_address = lendingPoolAddressProvider.functions.getLendingPool().call()
lendingPool = getContractInstance(lendingPool_address, 'LENDING_POOL.json')
protocolDataProvider = getContractInstance(PROTOCOL_DATA_PROVIDER, "PROTOCOL_DATA_PROVIDER.json")

def init():
    load_dotenv()  # take environment variables from .env.
reserves = protocolDataProvider.functions.getAllReservesTokens().call()
# if not reserves:
#     return
reserves = dict(reserves)
aave_address = reserves.get('AAVE', None)
aave = getContractInstance(aave_address, "AAVE.json")
dai_address = reserves.get('DAI', None)
dai = getContractInstance(dai_address, "DAI.json")
print(reserves)
# lendingPool = getContractInstance(
#     Get address of latest lendingPool from lendingPoolAddressProvider
    # lendingPoolAddressProvider.functions.getLendingPool().call(),
    # "LENDING_POOL.json"
# )

if __name__ == "__main__":
    init()
    # nonce = w3.eth.getTransactionCount("0xaa29b6365eAC1FFf89e82ae24dDf704293ef3bbB")
    # tokens = lendingPoolAddressProvider.functions.getAllReservesTokens()
    # 1 aave = 165.19 dai. 5 dai = 5/165.19 = 0.030268 aave
    aave_debt = 1
    # aave_debt = 0.036022
    liquidator_account = w3.eth.account.privateKeyToAccount("5de576d650dcdbfc7a1d3e947c636ca4e6c9c2df19e40be99e249b9e24d9b06f")
    debt_account = w3.eth.account.privateKeyToAccount("6965e8c138ac48e06562a09f867a458d8c96fd51ba45b2012aae0156f8c66feb")
    liquidate(debt_account.address, liquidator_account, aave_debt)

    # protocolDataProvider.functions.

