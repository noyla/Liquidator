pragma solidity ^0.6.6;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./ILendingPoolAddressesProvider.sol";
import "./ILendingPool.sol";


contract Liquidator {
    address public lendingPoolAddressProvider;
    // ILendingPool public lendingPool;
    
    // constructor(address _lendingPoolAddressProvider) public {
    constructor(ILendingPool _lendingPool) public {
        lendingPoolAddressProvider = _lendingPoolAddressProvider;
        // lendingPool = _lendingPool
    }

    function flashLiquidate(
        ILendingPool _lendingPool,
        address memory _collateral, 
        address memory _reserve,
        address memory _user,
        uint256 memory _purchaseAmount,
        bool memory _receiveaToken
    )
        external
        returns (bool)
    {        
        require(IERC20(_reserve).approve(address(_lendingPool), _purchaseAmount), "Approval error");

        // Assumes this contract already has `_purchaseAmount` of `_reserve`.
        lendingPool.liquidationCall(_collateral, _reserve, _user, -1 /*_purchaseAmount*/, 
                                    _receiveaToken);
        
        return true;
    }

    function liquidate(
        address memory _lendingPoolAddressProvider,
        address memory _collateral, 
        address memory _reserve,
        address memory _user,
        uint256 memory _purchaseAmount,
        bool memory _receiveaToken
    )
        external
    {
        // Get lending pool
        ILendingPoolAddressesProvider addressProvider = ILendingPoolAddressesProvider(_lendingPoolAddressProvider);
        ILendingPool lendingPool = ILendingPool(addressProvider.getLendingPool());
        
        // Approve the liquidated amount
        require(IERC20(_reserve).approve(address(lendingPool), _purchaseAmount), "Approval error");

        // Assumes this contract already has `_purchaseAmount` of `_reserve`.
        lendingPool.liquidationCall(_collateral, _reserve, _user, -1 /*_purchaseAmount*/, 
                                    _receiveaToken);
        
        return true;
    }
}