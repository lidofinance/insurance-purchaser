from brownie import accounts, interface, Wei

class bcolors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def print_value(text, value):
    value_to_print = 0 if value == 0 else Wei(value).to('ether')
    print(text, bcolors.OKCYAN, value_to_print, bcolors.ENDC)


def print_delta(text, value):
    if (value >= 0):
        print(text, bcolors.OKGREEN, f"+{Wei(value).to('ether')}", bcolors.ENDC)
    else:
        print(text, bcolors.FAIL, Wei(value).to('ether'), bcolors.ENDC)


dao_holders = [
    '0x3e40d73eb977dc6a537af587d48316fee66e9c8c',
    '0xb8d83908aab38a159f3da47a59d84db8e1838712',
    '0xa2dfc431297aee387c05beef507e5335e684fbcd',
    '0x1597d19659f3de52abd475f7d2314dcca29359bd',
    '0x695c388153bea0fbe3e1c049c149bad3bc917740',
    '0x945755de7eac99008c8c57bda96772d50872168b',
    '0xad4f7415407b83a081a0bee22d05a8fdc18b42da',
    '0xfea88380baff95e85305419eb97247981b1a8eee',
    '0x0f89d54b02ca570de82f770d33c7b7cf7b3c3394',
    '0x9bb75183646e2a0dc855498bacd72b769ae6ced3',
    '0x447f95026107aaed7472a0470931e689f51e0e42',
    '0x1f3813fe7ace2a33585f1438215c7f42832fb7b3',
    '0xc24da173a250e9ca5c54870639ebe5f88be5102d',
    '0xb842afd82d940ff5d8f6ef3399572592ebf182b0',
    '0x91715128a71c9c734cdc20e5edeeea02e72e428e',
    '0x8b1674a617f103897fb82ec6b8eb749ba0b9765b',
    '0x8d689476eb446a1fb0065bffac32398ed7f89165',
    '0x9849c2c1b73b41aee843a002c332a2d16aaab611'
]


def main():
    dao_voting = interface.Voting("0x2e59A20f205bB85a89C53f1936454680651E618e")
    dao_agent = interface.Agent("0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c")

    unslashed_token = interface.ERC20("0x2B76f72BFFcBE386EE6BD5F801f24f472dc9f633")
    steth_token = interface.ERC20("0xae7ab96520de3a18e5e111b5eaab095312d7fe84")
    ldo_token = interface.ERC20("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32")

    vote_id = 44

    eth_before = dao_agent.balance()
    unslashed_token_before = unslashed_token.balanceOf(dao_agent)
    steth_token_before = steth_token.balanceOf(dao_agent)
    ldo_token_before = ldo_token.balanceOf(dao_agent)

    print()
    print('Lido DAO agent balances before the vote execution')
    print_value('ETH:                          ', eth_before)
    print_value('Unslashed Lido Premium token: ', unslashed_token_before)
    print_value('stETH:                        ', steth_token_before)
    print_value('LDO:                          ', ldo_token_before)
    print()

    for holder_addr in dao_holders:
        print('voting from account:', holder_addr)
        accounts[0].transfer(holder_addr, '0.1 ether')
        account = accounts.at(holder_addr, force=True)
        dao_voting.vote(vote_id, True, False, {'from': account})

    dao_voting.executeVote(vote_id, {'from': accounts[0]})

    eth_after = dao_agent.balance()
    unslashed_token_after = unslashed_token.balanceOf(dao_agent)
    steth_token_after = steth_token.balanceOf(dao_agent)
    ldo_token_after = ldo_token.balanceOf(dao_agent)

    print()
    print('Lido DAO agent balances after the vote execution')
    print_value('ETH:                          ', eth_after)
    print_value('Unslashed Lido Premium token: ', unslashed_token_after)
    print_value('stETH:                        ', steth_token_after)
    print_value('LDO:                          ', ldo_token_after)
    print()

    eth_delta = eth_after - eth_before
    unslashed_token_delta = unslashed_token_after - unslashed_token_before
    steth_token_delta = steth_token_after - steth_token_before
    ldo_token_delta = ldo_token_after - ldo_token_before

    print()
    print('Lido DAO agent balances deltas')
    print_delta('ETH:                          ', eth_delta)
    print_delta('Unslashed Lido Premium token: ', unslashed_token_delta)
    print_delta('stETH:                        ', steth_token_delta)
    print_delta('LDO:                          ', ldo_token_delta)
    print()

