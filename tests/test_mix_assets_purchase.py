from brownie import Wei


def test_only_steth_purchase(steth_token,
                             steth_pool,
                             ldo_token,
                             unslashed_token,
                             deployer,
                             steth_whale,
                             purchase_helpers):

    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    steth_token.transfer(insurance_purchaser, Wei(
        "40.4 ether"), {"from": steth_whale})

    insurance_purchaser.purchase(Wei("40 ether"), {"from": deployer})

    assert unslashed_token.balanceOf(deployer) > 0

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) == 0
    assert unslashed_token.balanceOf(deployer) > 0


def test_only_ldo_purchase(steth_token,
                           steth_pool,
                           ldo_token,
                           unslashed_token,
                           deployer,
                           ldo_whale,
                           purchase_helpers):

    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    ldo_token.transfer(insurance_purchaser, Wei(
        "33260 ether"), {"from": ldo_whale})

    insurance_purchaser.purchase(Wei("40 ether"), {"from": deployer})

    assert unslashed_token.balanceOf(deployer) > 0

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) > 0
    assert unslashed_token.balanceOf(deployer) > 0


def test_mixed_steth_ldo_purchase(steth_token,
                                  steth_pool,
                                  ldo_token,
                                  unslashed_token,
                                  deployer,
                                  steth_whale,
                                  ldo_whale,
                                  purchase_helpers):

    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        100,
        500,
        deployer=deployer
    )

    steth_token.transfer(insurance_purchaser, Wei(
        "20.2 ether"), {"from": steth_whale})

    ldo_token.transfer(insurance_purchaser, Wei(
        "16630 ether"), {"from": ldo_whale})

    insurance_purchaser.purchase(Wei("40 ether"), {"from": deployer})

    assert unslashed_token.balanceOf(deployer) > 0

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) > 0
    assert unslashed_token.balanceOf(deployer) > 0
