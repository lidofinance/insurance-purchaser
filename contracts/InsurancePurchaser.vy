# @version 0.2.8
# @notice A proxy contract for purchase insurance.
# @author ujenjt
# @license MIT
from vyper.interfaces import ERC20


interface CurveLike:
    def get_dy(i: int128, j: int128, dx: uint256) -> uint256: view
    def exchange(i: int128, j: int128, dx: uint256, min_dy: uint256) -> uint256: payable


interface MooniswapLike:
    def tokens(i: uint256) -> address: view
    def getReturn(src: address, dst: address, amount: uint256) -> uint256: view
    def swap(src: address, dst: address, amount: uint256, minReturn: uint256, referral: address): payable


interface UnslashedMarketLike:
    def depositPremium(): payable


owner: public(address)
steth_to_eth_est_slippage: public(uint256)
ldo_to_steth_est_slippage: public(uint256)


# unslashed contract
UNSLASHED_MARKET: constant(address) = 0x746d94f1161C991675Ede99aBCDb0412a4fEE43E

# token addresses
STETH_TOKEN: constant(address) = 0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84
LDO_TOKEN: constant(address) = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32
UNSLASHED_PREMIUM_TOKEN: constant(address) = 0x2B76f72BFFcBE386EE6BD5F801f24f472dc9f633

# pool addresses
STETH_LDO_POOL: constant(address) = 0x1f629794B34FFb3B29FF206Be5478A52678b47ae
STETH_ETH_POOL: constant(address) = 0xDC24316b9AE028F1497c275EB9192a3Ea0f67022

# curve STETH/ETH pool indexes
ETH_INDEX: constant(int128) = 0
STETH_INDEX: constant(int128) = 1


@external
def __init__(_steth_to_eth_est_slippage: uint256, _ldo_to_steth_est_slippage: uint256):
    """
    @notice Contract constructor
    @param _steth_to_eth_est_slippage percentage of addition to the steth amount to compensate the slippage during stETH -> ETH swap
    @param _ldo_to_steth_est_slippage percentage of addition to the ldo amount to compensate the slippage during LDO -> stETH swap
    """
    self.owner = msg.sender

    assert _steth_to_eth_est_slippage <= 10000, "curve pool est slippage is over 100 percent"
    assert _ldo_to_steth_est_slippage <= 10000, "1inch pool est slippage is over 100 percent"

    # percentage is defined in basis points: 1 basis point is equal to 0.01%, 10000 is 100%
    self.steth_to_eth_est_slippage = _steth_to_eth_est_slippage
    self.ldo_to_steth_est_slippage = _ldo_to_steth_est_slippage


@external
@payable
def __default__():
    assert msg.value > 0 # dev: unexpected call


@view
@internal
def get_ldo_amount_to_swap(expected_eth_amount:uint256) -> uint256:
    steth_balance:uint256 = ERC20(STETH_TOKEN).balanceOf(self)

    eth_after_initial_steth_swap:uint256 = 0
    if steth_balance > 0:
        eth_after_initial_steth_swap = CurveLike(STETH_ETH_POOL).get_dy(
            STETH_INDEX,
            ETH_INDEX,
            steth_balance
        )

    if eth_after_initial_steth_swap >= expected_eth_amount:
        return 0

    eth_for_ldo: uint256 = expected_eth_amount - eth_after_initial_steth_swap
    steth_eth_spot_price:uint256 = CurveLike(STETH_ETH_POOL).get_dy(
        STETH_INDEX,
        ETH_INDEX,
        10 ** 18
    )

    steth_for_ldo:uint256 = 10 ** 18 * (eth_for_ldo / steth_eth_spot_price)
    steth_for_ldo += (steth_for_ldo * self.steth_to_eth_est_slippage) / 10000

    ldo_balance:uint256 = ERC20(LDO_TOKEN).balanceOf(self)
    ldo_steth_spot_price:uint256 = MooniswapLike(STETH_LDO_POOL).getReturn(
        LDO_TOKEN,
        STETH_TOKEN,
        10 ** 18
    )

    ldo_to_swap:uint256 = 10 ** 18 * steth_for_ldo / ldo_steth_spot_price
    ldo_to_swap += (ldo_to_swap * self.ldo_to_steth_est_slippage) / 10000

    return ldo_to_swap


@external
def purchase(_insurance_price_in_eth: uint256):
    steth_balance:uint256 = ERC20(STETH_TOKEN).balanceOf(self)
    ldo_balance:uint256 = ERC20(LDO_TOKEN).balanceOf(self)

    assert steth_balance + ldo_balance != 0, "contract should have ldo or steth tokens"
    assert _insurance_price_in_eth != 0, "_insurance_price_in_eth should be greater than 0"

    ldo_to_swap: uint256 = self.get_ldo_amount_to_swap(_insurance_price_in_eth)

    # swap LDO -> stETH if needed
    if ldo_to_swap > 0:
        ERC20(LDO_TOKEN).approve(STETH_LDO_POOL, ldo_to_swap)
        MooniswapLike(STETH_LDO_POOL).swap(
            LDO_TOKEN,
            STETH_TOKEN,
            ldo_to_swap,
            0,
            ZERO_ADDRESS
        )

    # swap stETH -> ETH
    steth_balance = ERC20(STETH_TOKEN).balanceOf(self)
    ERC20(STETH_TOKEN).approve(STETH_ETH_POOL, steth_balance)
    eth_amount: uint256 = CurveLike(STETH_ETH_POOL).exchange(
        STETH_INDEX,
        ETH_INDEX,
        steth_balance,
        _insurance_price_in_eth
    )

    # purchase insurance tokens and transfer them back to the agent
    UnslashedMarketLike(UNSLASHED_MARKET).depositPremium(value=_insurance_price_in_eth)
    ERC20(UNSLASHED_PREMIUM_TOKEN).transfer(self.owner, ERC20(UNSLASHED_PREMIUM_TOKEN).balanceOf(self))

    # transfer the rest ETH and tokens to the agent
    if self.balance != 0:
        send(self.owner, self.balance)

    if ERC20(STETH_TOKEN).balanceOf(self) > 0:
        ERC20(STETH_TOKEN).transfer(self.owner, ERC20(STETH_TOKEN).balanceOf(self))

    if ERC20(LDO_TOKEN).balanceOf(self) > 0:
        ERC20(LDO_TOKEN).transfer(self.owner, ERC20(LDO_TOKEN).balanceOf(self))


@external
def transfer_ownership(_to: address):
    """
    @notice Changes the contract owner. Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "not permitted"
    self.owner = _to


@external
def set_est_slippages(_steth_to_eth_est_slippage: uint256, _ldo_to_steth_est_slippage: uint256):
    """
    @notice Changes the slippage. Can only be called by the current owner.
    @param _steth_to_eth_est_slippage percentage of addition to the steth amount to compensate the slippage during stETH -> ETH swap
    @param _ldo_to_steth_est_slippage percentage of addition to the ldo amount to compensate the slippage during LDO -> stETH swap
    """
    assert msg.sender == self.owner, "not permitted"
    assert _steth_to_eth_est_slippage <= 10000, "curve pool est slippage is over 100 percent"
    assert _ldo_to_steth_est_slippage <= 10000, "1inch pool est slippage is over 100 percent"

    # percentage is defined in basis points: 1 basis point is equal to 0.01%, 10000 is 100%
    self.steth_to_eth_est_slippage = _steth_to_eth_est_slippage
    self.ldo_to_steth_est_slippage = _ldo_to_steth_est_slippage


@external
def recover_erc20(_token: address, _recipient: address = msg.sender):
    """
    @notice
        Transfers the whole balance of the given ERC20 token from self
        to the recipient. Can only be called by the owner.
    """
    assert msg.sender == self.owner, "not permitted"
    token_balance: uint256 = ERC20(_token).balanceOf(self)
    if token_balance != 0:
        assert ERC20(_token).transfer(_recipient, token_balance), "token transfer failed"

    if self.balance != 0:
        send(_recipient, self.balance)

