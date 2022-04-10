pragma solidity ^0.6.6;

import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/FlashLoanReceiverBase.sol";
import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPoolAddressesProvider.sol";
import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPool.sol";

import "./Liquidator.sol"

contract FlashLiquidator is FlashLoanReceiverBase {
    ILendingPoolAddressesProvider public addressProvider;

    constructor(address _addressProvider) FlashLoanReceiverBase(_addressProvider) public {
        addressProvider = _addressProvider;
    }

    /**
        This function is called after your contract has received the flash loaned amount
     */
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    )
        external
        override
        returns (bool)
    {
        //
        // This contract now has the funds requested.
        //

        lendingPool = ILendingPool(addressProvider.getLendingPool());

        Liquidator theLiquidator = Liquidator(lendingPool);
        theLiquidator.flashLiquidate(address(lendingPool))
    
        // At the end of your logic above, this contract owes
        // the flashloaned amounts + premiums.
        // Therefore ensure your contract has enough to repay
        // these amounts.

        // Approve the LendingPool contract allowance to *pull* the owed amount
        // i.e. AAVE V2's way of repaying the flash loan
        for (uint i = 0; i < assets.length; i++) {
            uint amountOwing = amounts[i].add(premiums[i]);
            IERC20(assets[i]).approve(address(LENDING_POOL), amountOwing);
        }

        return true;
    }

    /**
        Flash loan 1000000000000000000 wei (1 ether) worth of `_asset`
     */
    function flashLoanCall(address _asset) public onlyOwner {
        bytes memory data = "";
        uint amount = 1 ether;

        ILendingPool lendingPool = ILendingPool(addressProvider.getLendingPool());
        lendingPool.flashLoan(address(this), _asset, amount, data);
    }

    /*
    * Deposits the flashed AAVE, DAI and LINK liquidity onto the lending pool as collateral
    */
    function flashDeposit(ILendingPool _lendingPool) public {
        
        // approve lending pool
        IERC20(kovanDai).approve(lendingPoolAddr, flashDaiAmt1);
        IERC20(kovanAave).approve(lendingPoolAddr, flashAaveAmt0);
        IERC20(kovanLink).approve(lendingPoolAddr, flashLinkAmt2);
        
        // deposit the flashed AAVE, DAI and LINK as collateral
        _lendingPool.deposit(kovanDai, flashDaiAmt1, address(this), uint16(0));
        _lendingPool.deposit(kovanAave, flashAaveAmt0, address(this), uint16(0));
        _lendingPool.deposit(kovanLink, flashLinkAmt2, address(this), uint16(0));
        
    }
}