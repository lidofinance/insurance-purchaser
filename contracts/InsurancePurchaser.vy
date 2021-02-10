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
def __init__(_insurance_address: address):
    self.owner = msg.sender
    ERC20(STETH_TOKEN).approve(STETH_ETH_POOL, MAX_UINT256)


@payable
@external
def fail():
    CurveLike(STETH_ETH_POOL).exchange(STETH_INDEX, ETH_INDEX, 10000000, 0)

@external
def purchase(_insurance_price_in_eth: uint256):
    steth_balance_before:uint256 = ERC20(STETH_TOKEN).balanceOf(self)
    ldo_balance_before:uint256 = ERC20(LDO_TOKEN).balanceOf(self)

    assert steth_balance_before + ldo_balance_before != 0, "contract should have ldo or steth tokens"
    assert _insurance_price_in_eth != 0, "_insurance_price_in_eth should be greater than 0"

    steth_for_ldo_spot_price:uint256 = MooniswapLike(STETH_LDO_POOL).getReturn(LDO_TOKEN, STETH_TOKEN, 1000000000000000000)

    expected_steth:uint256 = 0
    if _insurance_price_in_eth > steth_balance_before:
        expected_steth = _insurance_price_in_eth - steth_balance_before

    ldo_to_swap:uint256 = expected_steth / steth_for_ldo_spot_price
    ldo_to_swap = ldo_to_swap + ldo_to_swap / 5 # add 5%

    assert ldo_balance_before >= ldo_to_swap, "contract should have enough LDO balance"

    # TODO: check ldo_to_swap > 0

    # approve and swap LDO -> stETH
    ERC20(LDO_TOKEN).approve(STETH_LDO_POOL, ldo_to_swap)
    min_steth_return: uint256 = 0 #because this is not the last swap in tx
    MooniswapLike(STETH_LDO_POOL).swap(LDO_TOKEN, STETH_TOKEN, ldo_to_swap, 10, ZERO_ADDRESS)

    # approve and swap stETH -> ETH
    steth_balance_before = ERC20(STETH_TOKEN).balanceOf(self)
    token_balance: uint256 = ERC20(STETH_TOKEN).balanceOf(self)
    ERC20(STETH_TOKEN).approve(STETH_ETH_POOL, steth_balance_before)
    eth_amount: uint256 = CurveLike(STETH_ETH_POOL).exchange(STETH_INDEX, ETH_INDEX, steth_balance_before, _insurance_price_in_eth)

    # purchase insurance tokens and transfer them back to the agent
    UnslashedMarketLike(UNSLASHED_MARKET).depositPremium(value=eth_amount)
    ERC20(UNSLASHED_PREMIUM_TOKEN).transfer(self.owner, ERC20(UNSLASHED_PREMIUM_TOKEN).balanceOf(self))

    # transfer the rest of the ETH back to the agent
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
