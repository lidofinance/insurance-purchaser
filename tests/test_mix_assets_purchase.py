from brownie import Wei, reverts

STETH_ETH_SLIPPAGE = 100
LDO_STETH_SLIPPAGE = 500
INSURANCE_ETH_PRICE = Wei("56.25 ether")
MIN_INSURANCE_TOKENS_TO_GET = Wei("55.5 ether")


def test_not_enought_ldo_purchase_reverts(ldo_token,
                                          deployer,
                                          ldo_whale,
                                          purchase_helpers):

    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        STETH_ETH_SLIPPAGE,
        LDO_STETH_SLIPPAGE,
        deployer=deployer
    )

    ldo_token.transfer(insurance_purchaser, Wei(
        "1 ether"), {"from": ldo_whale})

    with reverts("should have enough ldo"):
        insurance_purchaser.purchase(
            INSURANCE_ETH_PRICE, MIN_INSURANCE_TOKENS_TO_GET, {"from": deployer})


def test_only_steth_purchase(steth_token,
                             steth_pool,
                             ldo_token,
                             unslashed_token,
                             deployer,
                             steth_whale,
                             stable_swap_steth_eth,
                             purchase_helpers):

    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        STETH_ETH_SLIPPAGE,
        LDO_STETH_SLIPPAGE,
        deployer=deployer
    )

    steth_spot_price = stable_swap_steth_eth.get_dy(1, 0, Wei("1 ether"))

    steth_token.transfer(insurance_purchaser, Wei(
        "56.8125 ether"), {"from": steth_whale})

    tx = insurance_purchaser.purchase(
        INSURANCE_ETH_PRICE, MIN_INSURANCE_TOKENS_TO_GET, {"from": deployer})

    bought = tx.events["TokenExchange"]["tokens_bought"]
    sold = tx.events["TokenExchange"]["tokens_sold"]
    spot_price_buy_volume = steth_spot_price * sold / 1e18
    slipped_max_amount = spot_price_buy_volume * STETH_ETH_SLIPPAGE / 10000

    assert bought - spot_price_buy_volume <= slipped_max_amount
    assert bought >= INSURANCE_ETH_PRICE
    assert bought - INSURANCE_ETH_PRICE <= INSURANCE_ETH_PRICE * STETH_ETH_SLIPPAGE / 10000

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) == 0
    assert unslashed_token.balanceOf(deployer) > MIN_INSURANCE_TOKENS_TO_GET


def test_only_ldo_purchase(steth_token,
                           steth_pool,
                           ldo_token,
                           unslashed_token,
                           deployer,
                           ldo_whale,
                           mooniswap_steth_ldo,
                           stable_swap_steth_eth,
                           purchase_helpers):

    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        STETH_ETH_SLIPPAGE,
        LDO_STETH_SLIPPAGE,
        deployer=deployer
    )

    ldo_amount_on_agent = Wei("56660 ether")

    ldo_token.transfer(insurance_purchaser,
                       ldo_amount_on_agent, {"from": ldo_whale})

    ldo_spot_price = mooniswap_steth_ldo.getReturn(
        ldo_token.address, steth_token.address, Wei("1 ether"))
    steth_spot_price = stable_swap_steth_eth.get_dy(1, 0, Wei("1 ether"))

    tx = insurance_purchaser.purchase(
        INSURANCE_ETH_PRICE, MIN_INSURANCE_TOKENS_TO_GET, {"from": deployer})

    bought = tx.events["TokenExchange"]["tokens_bought"]
    sold = tx.events["TokenExchange"]["tokens_sold"]
    spot_price_buy_volume = steth_spot_price * sold / 1e18
    slipped_max_amount = spot_price_buy_volume * STETH_ETH_SLIPPAGE / 10000

    assert bought - spot_price_buy_volume <= slipped_max_amount
    assert bought >= INSURANCE_ETH_PRICE
    assert bought <= INSURANCE_ETH_PRICE * \
        (10000 + LDO_STETH_SLIPPAGE) / 10000 * \
        (10000 + STETH_ETH_SLIPPAGE) / 10000

    max_ldo_sold = sold / (ldo_spot_price / 1e18) + \
        sold * LDO_STETH_SLIPPAGE / 10000 / (ldo_spot_price / 1e18)

    ldo_sold = ldo_amount_on_agent - ldo_token.balanceOf(deployer)

    assert ldo_sold <= max_ldo_sold

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
                                  mooniswap_steth_ldo,
                                  stable_swap_steth_eth,
                                  purchase_helpers):

    # deploying
    insurance_purchaser = purchase_helpers.deploy_purchaser(
        STETH_ETH_SLIPPAGE,
        LDO_STETH_SLIPPAGE,
        deployer=deployer
    )

    steth_token.transfer(insurance_purchaser, Wei(
        "28.40625 ether"), {"from": steth_whale})

    ldo_amount_on_agent = Wei("23330 ether")

    ldo_token.transfer(insurance_purchaser,
                       ldo_amount_on_agent, {"from": ldo_whale})

    ldo_spot_price = mooniswap_steth_ldo.getReturn(
        ldo_token.address, steth_token.address, Wei("1 ether"))

    steth_spot_price = stable_swap_steth_eth.get_dy(1, 0, Wei("1 ether"))

    tx = insurance_purchaser.purchase(
        INSURANCE_ETH_PRICE, MIN_INSURANCE_TOKENS_TO_GET, {"from": deployer})

    bought = tx.events["TokenExchange"]["tokens_bought"]
    sold = tx.events["TokenExchange"]["tokens_sold"]
    spot_price_buy_volume = steth_spot_price * sold / 1e18
    slipped_max_amount = spot_price_buy_volume * STETH_ETH_SLIPPAGE / 10000

    assert bought - spot_price_buy_volume <= slipped_max_amount
    assert bought >= INSURANCE_ETH_PRICE
    assert bought <= INSURANCE_ETH_PRICE * \
        (10000 + LDO_STETH_SLIPPAGE / 2) / 10000 * \
        (10000 + STETH_ETH_SLIPPAGE) / 10000

    max_ldo_sold = sold / (ldo_spot_price / 1e18) + \
        sold * LDO_STETH_SLIPPAGE / 2 / 10000 / (ldo_spot_price / 1e18)

    ldo_sold = ldo_amount_on_agent - ldo_token.balanceOf(deployer)

    assert ldo_sold <= max_ldo_sold

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) > 0
    assert unslashed_token.balanceOf(deployer) > MIN_INSURANCE_TOKENS_TO_GET
