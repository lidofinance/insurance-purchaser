from brownie import Wei


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

    tx = insurance_purchaser.purchase(Wei("56.25 ether"), {"from": deployer})

    assert unslashed_token.balanceOf(deployer) > 0

    assert tx.events["TokenExchange"]["tokens_sold"] - \
        tx.events["TokenExchange"]["tokens_bought"] <= tx.events["TokenExchange"]["tokens_sold"] * \
        (steth_eth_slippage) / 10000

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

    assert tx.events["TokenExchange"]["tokens_sold"] - \
        tx.events["TokenExchange"]["tokens_bought"] <= tx.events["TokenExchange"]["tokens_sold"] * \
        (steth_eth_slippage+ldo_steth_slippage) / 10000

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

    tx = insurance_purchaser.purchase(Wei("56.25 ether"), {"from": deployer})

    assert unslashed_token.balanceOf(deployer) > 0

    assert tx.events["TokenExchange"]["tokens_sold"] - \
        tx.events["TokenExchange"]["tokens_bought"] <= tx.events["TokenExchange"]["tokens_sold"] * \
        (steth_eth_slippage+ldo_steth_slippage / 2) / 10000

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) > 0
    assert unslashed_token.balanceOf(deployer) > 0
