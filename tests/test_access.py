from brownie import (
    InsurancePurchaser,
    reverts,
    Wei
)


steth_to_eth_max_slippage = 100 # 1%
ldo_to_steth_max_slippage = 400 # 4%


def test_owner_changes_owner(deployer, stranger):
    insurance_purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    insurance_purchaser.transfer_ownership(stranger, {"from": deployer})


def test_stranger_does_not_change_owner(deployer, stranger):
    insurance_purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    with reverts("not permitted"):
        insurance_purchaser.transfer_ownership(stranger, {"from": stranger})


def test_owner_changes_slippages(deployer, stranger):
    insurance_purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    insurance_purchaser.set_est_slippages(steth_to_eth_max_slippage, 200, {"from": deployer})


def test_stranger_does_not_change_slippages(deployer, stranger):
    insurance_purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    with reverts("not permitted"):
        insurance_purchaser.set_est_slippages(
            steth_to_eth_max_slippage,
            ldo_to_steth_max_slippage - 100,
            {"from": stranger}
        )


def test_owner_recovers_erc20(deployer, stranger, steth_token, steth_whale):
    insurance_purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    STETH_DUST_DELTA = 2 # 2 wei

    steth_token.transfer(insurance_purchaser.address, Wei("1 ether"), {"from": steth_whale})
    stranger.transfer(insurance_purchaser.address, "1 ether")

    deployer_steth_before = steth_token.balanceOf(deployer)
    deployer_eth_before = deployer.balance()

    # recover erc20 and ether
    insurance_purchaser.recover_erc20(steth_token.address, {"from": deployer})

    assert insurance_purchaser.balance() == 0
    assert steth_token.balanceOf(insurance_purchaser.address) <= STETH_DUST_DELTA

    assert steth_token.balanceOf(deployer) - deployer_steth_before >= Wei("1 ether") - STETH_DUST_DELTA
    assert deployer.balance() - deployer_eth_before == Wei("1 ether")


def test_owner_recovers_only_eth(deployer, stranger, steth_token):
    insurance_purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    stranger.transfer(insurance_purchaser.address, "1 ether")
    deployer_eth_before = deployer.balance()

    # you can pass here any token
    insurance_purchaser.recover_erc20(steth_token.address, {"from": deployer})

    assert insurance_purchaser.balance() == 0
    assert deployer.balance() - deployer_eth_before == Wei("1 ether")


def test_stranger_does_not_recover_erc20(deployer, stranger, steth_token):
    insurance_purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    with reverts("not permitted"):
        insurance_purchaser.recover_erc20(steth_token.address, {"from": stranger})
