class UserData:
    @staticmethod
    def from_dict(user_data: dict):
        currentATokenBalance = user_data.get('currentATokenBalance', None)
        return UserData()
    
    borrower_aave_user_data = {'currentATokenBalance': borrower_aave_user_data[0], 'currentStableDebt': borrower_aave_user_data[1],
                     'currentVariableDebt': borrower_aave_user_data[2], 'principalStableDebt': borrower_aave_user_data[3],
                     'scaledVariableDebt': borrower_aave_user_data[4], 'stableBorrowRate': borrower_aave_user_data[5],
                     'liquidityRate': borrower_aave_user_data[6], 'stableRateLastUpdated': borrower_aave_user_data[7],
                     'usageAsCollateralEnabled': borrower_aave_user_data[8]}
