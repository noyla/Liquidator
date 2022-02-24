# RESERVE_CONFIGURATION_DATA = ['decimals', 'ltv', 'liquidationThreshold', 'liquidationBonus',
#                               'reserveFactor', 'usageAsCollateralEnabled', 'borrowingEnabled',
#                               'stableBorrowRateEnabled', 'isActive', 'isFrozen']

# class ReserveConfigurationData:
#     def __init__(self, decimals, ltv, liquidationThreshold, 
#                 liquidationBonus, reserveFactor, usageAsCollateralEnabled,
#                 borrowingEnabled, stableBorrowRateEnabled, isActive, isFrozen):
#             self.decimals = decimals
#             self.ltv = ltv
#             self.liquidationThreshold = liquidationThreshold
#             self.liquidationBonus = liquidationBonus
#             self.reserveFactor = reserveFactor
#             self.usageAsCollateralEnabled = usageAsCollateralEnabled
#             self.borrowingEnabled = borrowingEnabled 
#             self.stableBorrowRateEnabled = stableBorrowRateEnabled
#             self.isActive = isActive
#             self.isFrozen = isFrozen
#     @staticmethod
#     def from_raw_list(user_data: list):
#         res = {}
#         for i, v in enumerate(user_data):
#             res[RESERVE_CONFIGURATION_DATA[i]] = v
#         res = list(res.values())
#         return ReserveConfigurationData(res[0],res[1], res[2], res[3], res[4], res[5], res[6], 
#                                         res[7], res[8], res[9])