pragma solidity ^0.6.6;

import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/FlashLoanReceiverBase.sol";
import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPoolAddressesProvider.sol";
import "https://github.com/aave/flashloan-box/blob/Remix/contracts/aave/ILendingPool.sol";

import "./Liquidator.sol";

contract FlashLiquidator is FlashLoanReceiverBase {
    ILendingPoolAddressesProvider public addressProvider;
    ILiquidator public liquidatorContract;

    constructor(address _addressProvider, address _liquidator) FlashLoanReceiverBase(_addressProvider) public {
        addressProvider = ILendingPoolAddressesProvider(_addressProvider);
        liquidatorContract = _liquidator;
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
        // Verify funds received
        require(_amount <= getBalanceInternal(address(this), _reserve), "Invalid balance, was the flashLoan successful?");

        // Get LendingPool instance
        lendingPool = ILendingPool(addressProvider.getLendingPool());
        // Liquidator theLiquidator = Liquidator(lendingPool);
        // theLiquidator.flashLiquidate(address(lendingPool));
        liquidatorContract.flashLiquidate(address(lendingPool));
    
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
        uint256 mode = 0;
        address onBehalfOf = address(this);
        bytes memory params = "";
        uint16 referralCode = 0;

        ILendingPool lendingPool = ILendingPool(addressProvider.getLendingPool());
        lendingPool.flashLoan(address(this), _asset, amount, mode, onBehalfOf, params, referralCode);
    }

    /*
    * Rugpull all ERC20 tokens from the contract
    */
    function rugPull() public payable onlyOwner {
        
        // withdraw all ETH
        msg.sender.call{ value: address(this).balance }("");
        
        // withdraw all x ERC20 tokens
        IERC20(kovanAave).transfer(msg.sender, IERC20(kovanAave).balanceOf(address(this)));
        IERC20(kovanDai).transfer(msg.sender, IERC20(kovanDai).balanceOf(address(this)));
        // IERC20(kovanLink).transfer(msg.sender, IERC20(kovanLink).balanceOf(address(this)));
    }

    /*
    * Deposits the flashed AAVE, DAI and LINK liquidity onto the lending pool as collateral
    */
    // function flashDeposit(ILendingPool _lendingPool) public {
        
    //     // approve lending pool
    //     IERC20(kovanDai).approve(lendingPoolAddr, flashDaiAmt1);
    //     IERC20(kovanAave).approve(lendingPoolAddr, flashAaveAmt0);
    //     IERC20(kovanLink).approve(lendingPoolAddr, flashLinkAmt2);
        
    //     // deposit the flashed AAVE, DAI and LINK as collateral
    //     _lendingPool.deposit(kovanDai, flashDaiAmt1, address(this), uint16(0));
    //     _lendingPool.deposit(kovanAave, flashAaveAmt0, address(this), uint16(0));
    //     _lendingPool.deposit(kovanLink, flashLinkAmt2, address(this), uint16(0));
        
    // }
}