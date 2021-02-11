INSURANCE_ETH_PRICE = Wei("56.25 ether")
MIN_INSURANCE_TOKENS_TO_GET = Wei("55.5 ether")



def test_only_steth_purchase(steth_token,
                             steth_pool,
                             ldo_token,
                             unslashed_token,
                             deployer,
                             steth_whale,
                             purchase_helpers):
    steth_eth_slippage = 100
    ldo_steth_slippage = 500
    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        steth_eth_slippage,
        ldo_steth_slippage,
        deployer=deployer
    )

    steth_token.transfer(insurance_purchaser, Wei(
        "56.8125 ether"), {"from": steth_whale})

    tx = insurance_purchaser.purchase(
        INSURANCE_ETH_PRICE, MIN_INSURANCE_TOKENS_TO_GET, {"from": deployer})

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) == 0
    assert unslashed_token.balanceOf(deployer) > MIN_INSURANCE_TOKENS_TO_GET


def test_only_ldo_purchase(steth_token,
                           steth_pool,
                           ldo_token,
                           unslashed_token,
                           deployer,
                           ldo_whale,
                           purchase_helpers):

    steth_eth_slippage = 100
    ldo_steth_slippage = 500
    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        steth_eth_slippage,
        ldo_steth_slippage,
        deployer=deployer
    )

    ldo_token.transfer(insurance_purchaser, Wei(
        "46660 ether"), {"from": ldo_whale})

    tx = insurance_purchaser.purchase(Wei("56.25 ether"), {"from": deployer})

    assert unslashed_token.balanceOf(deployer) > 0

    tx = insurance_purchaser.purchase(
        INSURANCE_ETH_PRICE, MIN_INSURANCE_TOKENS_TO_GET, {"from": deployer})

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) > 0
    assert unslashed_token.balanceOf(
        deployer) > MIN_INSURANCE_TOKENS_TO_GET


def test_mixed_steth_ldo_purchase(steth_token,
                                  steth_pool,
                                  ldo_token,
                                  unslashed_token,
                                  deployer,
                                  steth_whale,
                                  ldo_whale,
                                  purchase_helpers):
    steth_eth_slippage = 100
    ldo_steth_slippage = 500
    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        steth_eth_slippage,
        ldo_steth_slippage,
        deployer=deployer
    )

    steth_token.transfer(insurance_purchaser, Wei(
        "28.40625 ether"), {"from": steth_whale})

    ldo_token.transfer(insurance_purchaser, Wei(
        "23330 ether"), {"from": ldo_whale})

    tx = insurance_purchaser.purchase(
        INSURANCE_ETH_PRICE, MIN_INSURANCE_TOKENS_TO_GET, {"from": deployer})

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) > 0
    assert unslashed_token.balanceOf(deployer) > MIN_INSURANCE_TOKENS_TO_GET
