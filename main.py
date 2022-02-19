import traceback
from dotenv import load_dotenv

# import uint
from web3 import Web3

from toolkit import Toolkit
from pools import LendingPool, ProtocolDataProvider

DAI_KOVAN_ADDRESS = '0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD' # DAI token Kovan testnet address
# DAI_KOVAN_ADDRESS = '0xfdf7f21EDA1fB8AeBEd2FC8b0e8F72a8f17cf823' # DAI token Kovan testnet address
BUSD_KOVAN_ADDRESS = '0x4c6E1EFC12FDfD568186b7BAEc0A43fFfb4bCcCf' # Bincance USD Kovan testnet address
# AAVE_TOKEN_KOVAN_ADDRESS = '0x1d70fE7272F07E38e4bE71636e711bC007341273' # AAVE Kovan testnet address
AAVE_TOKEN_KOVAN_ADDRESS = '0xB597cd8D3217ea6477232F9217fa70837ff667Af' # AAVE Kovan testnet address
# BUSD_KOVAN_ADDRESS = '0x73eF351Ed451A52CB2D9651eCDE4b72520d343bE' # Bincance USD Kovan testnet address
# BUSD_KOVAN_ADDRESS = '0x822f658628169239d4a07afd1d392c6d7e7cc1d5' # Bincance USD Kovan testnet address

LIQUIDATION_CLOSE_FACTOR = 0.5
AAVE_ETHER_CONVERSION = 0.0566
DAI_ETHER_CONVERSION = 0.000345

# def exec_contract(account, nonce, func):
#     """
#     Call a contract that commits a transaction
#     """
#     try:
#         transaction = func.buildTransaction({'from': account.address, 'nonce': nonce})
#                                              # 'gas': 2500000, 'gasPrice': 2500000})#estimated_gas, #2000000,})
#         # transaction = func.buildTransaction({'from': account.address, 'nonce': nonce})
#         signed = account.signTransaction(transaction)#, '5de576d650dcdbfc7a1d3e947c636ca4e6c9c2df19e40be99e249b9e24d9b06f')
#         trans_hash = Toolkit.w3().eth.sendRawTransaction(signed.rawTransaction)
#         if trans_hash:
#             tx_receipt = Toolkit.w3().eth.waitForTransactionReceipt(trans_hash, timeout=60)
#     except:
#         traceback.print_exc()
#         return None
#     print("Transaction hash for func %s. %s" % (func, trans_hash.hex()))
#     return trans_hash.hex()

def liquidate(borrower, liquidator_account):
    try:
        # allowance = 0
        borrower_aave_user_data = ProtocolDataProvider.functions.getUserReserveData(aave_address, borrower).call()
        borrower_aave_user_data = {'currentATokenBalance': borrower_aave_user_data[0], 'currentStableDebt': borrower_aave_user_data[1],
                     'currentVariableDebt': borrower_aave_user_data[2], 'principalStableDebt': borrower_aave_user_data[3],
                     'scaledVariableDebt': borrower_aave_user_data[4], 'stableBorrowRate': borrower_aave_user_data[5],
                     'liquidityRate': borrower_aave_user_data[6], 'stableRateLastUpdated': borrower_aave_user_data[7],
                     'usageAsCollateralEnabled': borrower_aave_user_data[8]}
        borrower_dai_user_data = ProtocolDataProvider.functions.getUserReserveData(dai_address, borrower).call()
        borrower_dai_user_data = {'currentATokenBalance': borrower_dai_user_data[0], 'currentStableDebt': borrower_dai_user_data[1],
                                   'currentVariableDebt': borrower_dai_user_data[2], 'principalStableDebt': borrower_dai_user_data[3],
                                   'scaledVariableDebt': borrower_dai_user_data[4], 'stableBorrowRate': borrower_dai_user_data[5],
                                   'liquidityRate': borrower_dai_user_data[6], 'stableRateLastUpdated': borrower_dai_user_data[7],
                                   'usageAsCollateralEnabled': borrower_dai_user_data[8]}
        print(borrower_dai_user_data)
        if not borrower_dai_user_data or not borrower_dai_user_data.get('usageAsCollateralEnabled'):
            return

        # Approve lendingPool to spend liquidator's funds
        allowance = aave.functions.allowance(liquidator_account.address, LendingPool.address).call()
        if allowance <= 0:
            nonce = Toolkit.w3().eth.getTransactionCount(liquidator_account.address)
            debtToCover = (borrower_aave_user_data['currentStableDebt'] + borrower_aave_user_data['currentVariableDebt']) * \
                        LIQUIDATION_CLOSE_FACTOR
            debtToCover = Toolkit.w3().toWei(1, 'ether')
            approval_hash = exec_contract(liquidator_account, nonce, aave.functions.approve(LendingPool.address, debtToCover*2))

        # c = Toolkit.w3().eth.getBalance(liquidator_account.address)
        # balance = aave.functions.balanceOf(liquidator_account.address).call()

        liquidation_func = LendingPool.functions.liquidationCall(
            dai.address,
            aave.address,
            borrower,
            debtToCover,#.Toolkit.w3().toHex(-1),# amountAave,
            # Toolkit.w3().toWei(amountAave * AAVE_ETHER_CONVERSION, 'ether'),
            False
        )
        # allowance_after = aave.functions.allowance(, lendingPool.address).call()
        nonce = Toolkit.w3().eth.getTransactionCount(liquidator_account.address)
        tx_hash = exec_contract(liquidator_account,nonce, liquidation_func)
        print("Transaction accepted. %s" % tx_hash)
    except Exception as e:
        print(e)

def transfer(user, liquidator, amountDai):
    # estimated_gas = Toolkit.w3().eth.estimateGas(txn)
    # 'gas': 21000, 'gasPrice': 210000
    transfer_transaction = {
        'from': liquidator,
        'to': user,
        'value': Toolkit.w3().toWei(amountDai * 0.000345, 'ether'),
        'nonce': Toolkit.w3().eth.getTransactionCount("0xaa29b6365eAC1FFf89e82ae24dDf704293ef3bbB"),
        'gas': 25000, #estimated_gas, #2000000,
        'gasPrice': 210000
        #'chainId': None,
    }
    signed_transaction = Toolkit.w3().eth.account.signTransaction(transfer_transaction, "5de576d650dcdbfc7a1d3e947c636ca4e6c9c2df19e40be99e249b9e24d9b06f")
    # hex = Toolkit.w3().eth.sendRawTransaction(signed_transaction.rawTransaction)

# dai = Toolkit.getContractInstance(DAI_KOVAN_ADDRESS, "DAI.json")
# busd = Toolkit.getContractInstance(BUSD_KOVAN_ADDRESS, "BUSD.json")
# aave = Toolkit.getContractInstance(AAVE_TOKEN_KOVAN_ADDRESS, "AAVE.json")

# lendingPoolAddressProviderRegistry = Toolkit.getContractInstance("0x1E40B561EC587036f9789aF83236f057D1ed2A90", 
                                                                #  "LENDING_POOL_PROVIDER_REGISTRY.json")
# lendingPool_providers = lendingPoolAddressProviderRegistry.functions.getAddressesProvidersList().call()
# try:
# lendingpool_provider_address = next(filter(lambda provider: provider != '0x0000000000000000000000000000000000000000',
                                        #    lendingPool_providers))
# except StopIteration:
#     pass
# lendingPoolAddressProvider = Toolkit.getContractInstance(lendingpool_provider_address, "LENDING_POOL_PROVIDER.json") # Kovan
# lendingPoolAddressProvider = Toolkit.getContractInstance("0x88757f2f99175387aB4C6a4b3067c77A695b0349", "LENDING_POOL_PROVIDER.json") # Kovan
# lendingPool_address = '0x2646FcF7F0AbB1ff279ED9845AdE04019C907EBE'
# lendingPool_address = lendingPoolAddressProvider.functions.getLendingPool().call()
# lendingPool = Toolkit.getContractInstance(lendingPool_address, 'LENDING_POOL.json')
# protocolDataProvider = Toolkit.getContractInstance(PROTOCOL_DATA_PROVIDER, "PROTOCOL_DATA_PROVIDER.json")

def init():
    load_dotenv()  # take environment variables from .env.


if __name__ == "__main__":
    init()
    aave_debt = 1
    # aave_debt = 0.036022
    liquidator_account = Toolkit.w3().eth.account.privateKeyToAccount("5de576d650dcdbfc7a1d3e947c636ca4e6c9c2df19e40be99e249b9e24d9b06f")
    debt_account = Toolkit.w3().eth.account.privateKeyToAccount("6965e8c138ac48e06562a09f867a458d8c96fd51ba45b2012aae0156f8c66feb")
    liquidate(debt_account.address, liquidator_account)


