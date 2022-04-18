pragma solidity ^0.6.6;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPoolAddressesProvider.sol";
import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPool.sol";

interface ILiquidator {
    function flashLiquidate() external returns (bool);
}

contract Liquidator {
    // address public lendingPoolAddressProvider;
    // ILendingPool public lendingPool;
    
    // constructor(address _lendingPoolAddressProvider) public {
    // constructor(ILendingPool _lendingPool) public {
    constructor() public {
    }

    function flashLiquidate(
        address memory _lendingPoolAddress,
        address memory _collateral, 
        address memory _debtReserve,
        address memory _user,
        uint256 memory _purchaseAmount,
        bool memory _receiveaToken
    )
        external
        returns (bool)
    {        
        // Approve the lending pool to spend `_purchaseAmount` of `_debtReserve` so the debt is covered.
        require(IERC20(_debtReserve).approve(_lendingPoolAddress, _purchaseAmount), "Approval error");
        
        // Liquidate
        ILendingPool lendingPool = ILendingPool(_lendingPoolAddress);
        lendingPool.liquidationCall(_collateral, _debtReserve, _user, -1 /*_purchaseAmount*/, 
                                    _receiveaToken);
        
        return true;
    }

    function liquidate(
        address memory _lendingPoolAddressProvider,
        address memory _collateral, 
        address memory _debtReserve,
        address memory _user,
        uint256 memory _purchaseAmount,
        bool memory _receiveaToken
    )
        external
        returns (bool)
    {
        // Get lending pool
        ILendingPoolAddressesProvider addressProvider = ILendingPoolAddressesProvider(_lendingPoolAddressProvider);
        ILendingPool lendingPool = ILendingPool(addressProvider.getLendingPool());
        
        // Approve the liquidated amount
        require(IERC20(_debtReserve).approve(address(lendingPool), _purchaseAmount), "Approval error");

        // Assumes this contract already has `_purchaseAmount` of `_reserve`.
        lendingPool.liquidationCall(_collateral, _debtReserve, _user, -1 /*_purchaseAmount*/, 
                                    _receiveaToken);
        
        return true;
    }
}