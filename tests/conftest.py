import pytest
from brownie import Wei, ZERO_ADDRESS


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]


@pytest.fixture()
def steth_whale(accounts, steth_token, lido):
    acct = accounts[1]
    lido.submit(ZERO_ADDRESS, {"from": acct, "value": "10 ether"})
    assert steth_token.balanceOf(acct) > 0
    return acct


@pytest.fixture(scope='module')
def stranger(accounts):
    return accounts[9]


# Lido DAO Voting app
@pytest.fixture(scope='module')
def dao_voting(accounts):
    return accounts.at("0x2e59A20f205bB85a89C53f1936454680651E618e", force=True)


@pytest.fixture(scope='module')
def lido(interface):
    return interface.Lido("0xae7ab96520de3a18e5e111b5eaab095312d7fe84")


@pytest.fixture(scope='module')
def steth_token(interface, lido):
    return interface.ERC20(lido.address)


# Lido DAO Agent app
@pytest.fixture(scope='module')
def dao_agent(interface):
    return interface.Agent("0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c")


@pytest.fixture(scope='module')
def steth_pool(interface):
    return interface.StableSwapSTETH("0xDC24316b9AE028F1497c275EB9192a3Ea0f67022")


@pytest.fixture(scope='module')
def ldo_token(interface):
    return interface.ERC20("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32")



@pytest.fixture()
def ldo_whale(accounts, ldo_token):
    acct = accounts.at("0x454f11d58e27858926d7a4ece8bfea2c33e97b13", force=True)
    assert ldo_token.balanceOf(acct) > 0
    return acct


@pytest.fixture(scope='module')
def unslashed_token(interface):
    return interface.ERC20("0x2B76f72BFFcBE386EE6BD5F801f24f472dc9f633")


class PurchaseHelpers:
    InsurancePurchaser = None

    @staticmethod
    def deploy_purchaser(insurance, deployer):
        purchaser = PurchaseHelpers.InsurancePurchaser.deploy(insurance, {"from": deployer})

        return purchaser


@pytest.fixture(scope='module')
def purchase_helpers(InsurancePurchaser):
    PurchaseHelpers.InsurancePurchaser = InsurancePurchaser
    return PurchaseHelpers


class Helpers:
    @staticmethod
    def filter_events_from(addr, events):
      return list(filter(lambda evt: evt.address == addr, events))

    @staticmethod
    def assert_single_event_named(evt_name, tx, evt_keys_dict):
      receiver_events = Helpers.filter_events_from(tx.receiver, tx.events[evt_name])
      assert len(receiver_events) == 1
      assert dict(receiver_events[0]) == evt_keys_dict


@pytest.fixture(scope='module')
def helpers():
    return Helpers
