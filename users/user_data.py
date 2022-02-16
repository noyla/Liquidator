USER_RESERVE_DATA = ['currentATokenBalance', 'currentStableDebt',
                     'currentVariableDebt', 'principalStableDebt',
                     'scaledVariableDebt', 'stableBorrowRate',
                     'liquidityRate', 'stableRateLastUpdated',
                     'usageAsCollateralEnabled']
class UserData:
    def __init__(self, currentATokenBalance, currentStableDebt, currentVariableDebt,
    principalStableDebt, scaledVariableDebt, stableBorrowRate, liquidityRate, 
    stableRateLastUpdated, usageAsCollateralEnabled: bool) -> None:
        self.currentATokenBalance = currentATokenBalance
        self.currentStableDebt = currentStableDebt
        self.currentVariableDebt = currentVariableDebt
        self.principalStableDebt = principalStableDebt
        self.scaledVariableDebt = scaledVariableDebt
        self.stableBorrowRate = stableBorrowRate
        self.liquidityRate = liquidityRate
        self.stableRateLastUpdated = stableRateLastUpdated
        self.usageAsCollateralEnabled = usageAsCollateralEnabled

    @staticmethod
    def from_raw_list(user_data: list):
        res = {}
        for i, v in enumerate(user_data):
            res[USER_RESERVE_DATA[i]] = v
        
        return UserData(list(res.values))
    
    borrower_aave_user_data = {'currentATokenBalance': borrower_aave_user_data[0], 'currentStableDebt': borrower_aave_user_data[1],
                     'currentVariableDebt': borrower_aave_user_data[2], 'principalStableDebt': borrower_aave_user_data[3],
                     'scaledVariableDebt': borrower_aave_user_data[4], 'stableBorrowRate': borrower_aave_user_data[5],
                     'liquidityRate': borrower_aave_user_data[6], 'stableRateLastUpdated': borrower_aave_user_data[7],
                     'usageAsCollateralEnabled': borrower_aave_user_data[8]}
