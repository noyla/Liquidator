from datetime import datetime
import os

# import uint
from web3 import Web3
from services.users_service import UsersService

from toolkit import toolkit_
from pools import LendingPool, ProtocolDataProvider

DAI_KOVAN_ADDRESS = '0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD' # DAI token Kovan testnet address
BUSD_KOVAN_ADDRESS = '0x4c6E1EFC12FDfD568186b7BAEc0A43fFfb4bCcCf' # Bincance USD Kovan testnet address
AAVE_TOKEN_KOVAN_ADDRESS = '0xB597cd8D3217ea6477232F9217fa70837ff667Af' # AAVE Kovan testnet address
LIQUIDATION_CLOSE_FACTOR = 0.5
AAVE_ETHER_CONVERSION = 0.0566
DAI_ETHER_CONVERSION = 0.000345


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
            nonce = toolkit_.w3.eth.getTransactionCount(liquidator_account.address)
            debtToCover = (borrower_aave_user_data['currentStableDebt'] + borrower_aave_user_data['currentVariableDebt']) * \
                        LIQUIDATION_CLOSE_FACTOR
            debtToCover = toolkit_.w3.toWei(1, 'ether')
            approval_hash = exec_contract(liquidator_account, nonce, aave.functions.approve(LendingPool.address, debtToCover*2))

        # c = toolkit.w3.eth.getBalance(liquidator_account.address)
        # balance = aave.functions.balanceOf(liquidator_account.address).call()

        liquidation_func = LendingPool.functions.liquidationCall(
            dai.address,
            aave.address,
            borrower,
            debtToCover,#.toolkit.w3.toHex(-1),# amountAave,
            # toolkit.w3.toWei(amountAave * AAVE_ETHER_CONVERSION, 'ether'),
            False
        )
        # allowance_after = aave.functions.allowance(, lendingPool.address).call()
        nonce = toolkit_.w3.eth.getTransactionCount(liquidator_account.address)
        tx_hash = exec_contract(liquidator_account,nonce, liquidation_func)
        print("Transaction accepted. %s" % tx_hash)
    except Exception as e:
        print(e)

def transfer(user, liquidator, amountDai):
    # estimated_gas = toolkit.w3.eth.estimateGas(txn)
    # 'gas': 21000, 'gasPrice': 210000
    transfer_transaction = {
        'from': liquidator,
        'to': user,
        'value': toolkit_.w3.toWei(amountDai * 0.000345, 'ether'),
        'nonce': toolkit_.w3.eth.getTransactionCount("0xaa29b6365eAC1FFf89e82ae24dDf704293ef3bbB"),
        'gas': 25000, #estimated_gas, #2000000,
        'gasPrice': 210000
        #'chainId': None,
    }
    key = os.environ.get('TESTNET_PRIVATE_KEY')
    signed_transaction = toolkit_.w3.eth.account.signTransaction(transfer_transaction, key)
    # hex = toolkit.w3.eth.sendRawTransaction(signed_transaction.rawTransaction)

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



if __name__ == "__main__":
    # datetime_object = datetime.strptime('2022-03-07 04:13:03+00:00', '%Y-%m-%d %H:%M:%S%z')
    # datetime_object.strftime('%Y-%m-%d %H:%M:%S')
    # svc = UsersService()
    # svc.migrate_to_redis()
    # exists, user_data = svc.get_user_data('0x816E27f645F663743a5DAEDfc9a38ed02D0B2211')
    # aave_debt = 1

    




