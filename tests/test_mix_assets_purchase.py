from brownie import Wei, reverts, InsurancePurchaser


steth_to_eth_max_slippage = 100 # 1%
ldo_to_steth_max_slippage = 400 # 4%
insurance_total_in_eth = Wei("56.25 ether")
min_insurance_tokens = Wei("70 ether")


def test_not_enought_ldo_purchase_reverts(
    ldo_token,
    deployer,
    ldo_whale
):
    purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    ldo_token.transfer(purchaser, Wei("1 ether"), {"from": ldo_whale})

    with reverts("should have enough ldo"):
        purchaser.purchase(
            insurance_total_in_eth,
            min_insurance_tokens,
            {"from": deployer}
        )


def test_only_steth_purchase(
    steth_token,
    ldo_token,
    unslashed_token,
    deployer,
    steth_whale,
    stable_swap_steth_eth
):
    purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    steth_spot_price = stable_swap_steth_eth.get_dy(1, 0, Wei("1 ether"))

    steth_token.transfer(purchaser, Wei("56.8125 ether"), {"from": steth_whale})

    tx = purchaser.purchase(insurance_total_in_eth, min_insurance_tokens, {"from": deployer})

    bought = tx.events["TokenExchange"]["tokens_bought"]
    sold = tx.events["TokenExchange"]["tokens_sold"]
    spot_price_buy_volume = steth_spot_price * sold / 1e18
    slipped_max_amount = spot_price_buy_volume * steth_to_eth_max_slippage / 10000

    assert bought - spot_price_buy_volume <= slipped_max_amount
    assert bought >= insurance_total_in_eth
    assert bought - insurance_total_in_eth <= insurance_total_in_eth * steth_to_eth_max_slippage / 10000

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) == 0
    assert unslashed_token.balanceOf(deployer) > min_insurance_tokens


def test_only_ldo_purchase(
    steth_token,
    ldo_token,
    unslashed_token,
    deployer,
    ldo_whale,
    mooniswap_steth_ldo,
    stable_swap_steth_eth
):
    purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    ldo_amount_on_agent = Wei("56660 ether")

    ldo_token.transfer(purchaser, ldo_amount_on_agent, {"from": ldo_whale})

    ldo_spot_price = mooniswap_steth_ldo.getReturn(
        ldo_token.address,
        steth_token.address,
        Wei("1 ether")
    )
    steth_spot_price = stable_swap_steth_eth.get_dy(1, 0, Wei("1 ether"))

    tx = purchaser.purchase(
        insurance_total_in_eth,
        min_insurance_tokens,
        {"from": deployer}
    )

    bought = tx.events["TokenExchange"]["tokens_bought"]
    sold = tx.events["TokenExchange"]["tokens_sold"]
    spot_price_buy_volume = steth_spot_price * sold / 1e18
    slipped_max_amount = spot_price_buy_volume * steth_to_eth_max_slippage / 10000

    assert bought - spot_price_buy_volume <= slipped_max_amount
    assert bought >= insurance_total_in_eth
    assert bought <= insurance_total_in_eth * \
        (10000 + ldo_to_steth_max_slippage) / 10000 * \
        (10000 + steth_to_eth_max_slippage) / 10000

    max_ldo_sold = sold / (ldo_spot_price / 1e18) + \
        sold * ldo_to_steth_max_slippage / 10000 / (ldo_spot_price / 1e18)

    ldo_sold = ldo_amount_on_agent - ldo_token.balanceOf(deployer)

    assert ldo_sold <= max_ldo_sold

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) > 0
    assert unslashed_token.balanceOf(deployer) > min_insurance_tokens


def test_mixed_steth_ldo_purchase(
    steth_token,
    ldo_token,
    unslashed_token,
    deployer,
    steth_whale,
    ldo_whale,
    mooniswap_steth_ldo,
    stable_swap_steth_eth
):
    purchaser = InsurancePurchaser.deploy(
        steth_to_eth_max_slippage,
        ldo_to_steth_max_slippage,
        {"from": deployer}
    )

    steth_token.transfer(purchaser, Wei(
        "28.40625 ether"), {"from": steth_whale})

    ldo_amount_on_agent = Wei("50000 ether")

    ldo_token.transfer(purchaser,
                       ldo_amount_on_agent, {"from": ldo_whale})

    ldo_spot_price = mooniswap_steth_ldo.getReturn(
        ldo_token.address, steth_token.address, Wei("1 ether"))

    steth_spot_price = stable_swap_steth_eth.get_dy(1, 0, Wei("1 ether"))

    tx = purchaser.purchase(
        insurance_total_in_eth, min_insurance_tokens, {"from": deployer})

    bought = tx.events["TokenExchange"]["tokens_bought"]
    sold = tx.events["TokenExchange"]["tokens_sold"]
    spot_price_buy_volume = steth_spot_price * sold / 1e18
    slipped_max_amount = spot_price_buy_volume * steth_to_eth_max_slippage / 10000

    assert bought - spot_price_buy_volume <= slipped_max_amount
    assert bought >= insurance_total_in_eth
    assert bought <= insurance_total_in_eth * \
        (10000 + ldo_to_steth_max_slippage / 2) / 10000 * \
        (10000 + steth_to_eth_max_slippage) / 10000

    max_ldo_sold = sold / (ldo_spot_price / 1e18) + \
        sold * ldo_to_steth_max_slippage / 2 / 10000 / (ldo_spot_price / 1e18)

    ldo_sold = ldo_amount_on_agent - ldo_token.balanceOf(deployer)

    assert ldo_sold <= max_ldo_sold

    assert steth_token.balanceOf(deployer) == 0
    assert ldo_token.balanceOf(deployer) > 0
    assert unslashed_token.balanceOf(deployer) > min_insurance_tokens
