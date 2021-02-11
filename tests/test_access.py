from brownie import reverts


def test_owner_changes_owner(deployer, stranger, purchase_helpers):
    # deploying and purhchase
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    insurance_purchaser.transfer_ownership(stranger, {"from": deployer})


def test_stranger_does_not_change_owner(deployer, stranger, purchase_helpers):
    # deploying and purhchase
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    with reverts("not permitted"):
        insurance_purchaser.transfer_ownership(stranger, {"from": stranger})


def test_owner_changes_slippages(deployer, stranger, purchase_helpers):
    # deploying and purhchase
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    insurance_purchaser.set_est_slippages(100, 200, {"from": deployer})


def test_stranger_does_not_change_slippages(deployer, stranger, purchase_helpers):
    # deploying and purhchase
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    with reverts("not permitted"):
        insurance_purchaser.set_est_slippages(100, 200, {"from": stranger})


def test_owner_recovers_erc20(deployer, stranger, purchase_helpers, steth_token):
    # deploying and purhchase
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    insurance_purchaser.recover_erc20(steth_token.address, {"from": deployer})


def test_stranger_does_not_recover_erc20(deployer, stranger, purchase_helpers, steth_token):
    # deploying and purhchase
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    with reverts("not permitted"):
        insurance_purchaser.recover_erc20(
            steth_token.address, {"from": stranger})
