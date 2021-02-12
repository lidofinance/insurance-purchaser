# Insurance purchasing contract for Lido

Contains a proxy contract which takes LDO and stETH tokens from the treasury, converts them to ETH (LDO -> stETH -> ETH), and then purchases insurance by Unslashed to cover eth2 validators slashing.

## Development

### Dependencies

* [python3](https://www.python.org/downloads/release/python-390/) from version 3.7 to 3.9
* [brownie](https://github.com/iamdefinitelyahuman/brownie) - version 1.13.1
* [ganache-cli](https://github.com/trufflesuite/ganache-cli) - version 6.12.1

### Dev and test

To get started, first create and initialize a Python [virtual environment](https://docs.python.org/3/library/venv.html). Next, clone the repo and install the dependencies. Run the tests:

```bash
git clone https://github.com/lidofinance/insurance-purchaser.git
cd insurance-purchaser
export WEB3_INFURA_PROJECT_ID=infura-token
brownie test
```

## Check aragon vote execution script

To validate that a proposed vote for transferring tokens (LDO, stETH) to the InsurancePurchaser is correct, you need to do the following steps:

1. Open Lido [`voting app`](https://etherscan.io/address/0x2e59A20f205bB85a89C53f1936454680651E618e#readProxyContract) in etherscan, fetch the vote with the corresponding `id`, and extract the `script` field content.

2. Check the configuration of the proposed purchase in [`scripts/generate_purchase_exec_script.py`](scripts/generate_purchase_exec_script.py) (`ldo_amount`, `steth_amount`, `insurance_amount`, `reference`).

3. Run `scripts/generate_purchase_exec_script.py` and check that the exec script it generates matches the one extracted from the vote.

    ```bash
    brownie run generate_purchase_exec_script --network mainnet
    ```


## Deployment

To deploy the purchaser contract:

1. Edit the configuration settings within [`scripts/deploy.py`](scripts/deploy.py). Check aragon agent mainnet address.
2. Test it locally.

    ```bash
    brownie run deploy --network development
    ```
3. Set DEPLOYER env variable to the deployer account name first (from ~/.brownie/accounts).

    ```bash
    export DEPLOYER=ldo_holder
    ```
4. Deploy to the mainnet and transfer ownership to the agent address.

    ```bash
    brownie run deploy --network mainnet
    ```

To propose a new purchase:

1. Edit the configuration settings within [`propose_insurance_purchase.py`](propose_insurance_purchase.py).
2. Test it locally.

    ```bash
    brownie run propose_insurance_purchase --network development
    ```
3. Set DEPLOYER env variable to the deployer account name first (from `~/.brownie/accounts`). Important: DEPLOYER acc should have some LDO governance token to be able to submit new vote.

    ```bash
    export DEPLOYER=ldo_holder
    ```
4. Submit the vote.

    ```bash
    brownie run propose_insurance_purchase --network mainnet
    ```
    When the script completes it will print the `vote_id`.


## Playground


1. Set WEB3_INFURA_PROJECT_ID and open brownie console.
    ```bash
    export WEB3_INFURA_PROJECT_ID=infura-token
    brownie console --network development
    ```

2. Deploy insurance purchaser by running deploy script from the console.
    ```bash
    >>> run("deploy.py")
    >>> purchaser = InsurancePurchaser.at("0x602C71e4DAC47a042Ee7f46E0aee17F94A3bA0B6")
    ```

3. Edit the configuration settings within [`propose_insurance_purchase.py`](propose_insurance_purchase.py). Put the actual address for `InsurancePurchaser`.

4. Get some LDO tokens to be able to submit a vote.
    ```bash
    >>> run("get_coins.py")
    >>> ldo_token = interface.ERC20("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32")
    >>> ldo_token.balanceOf(accounts[0])
    ```

5. Propose a vote and check the script.
    ```bash
    >>> run("propose_insurance_purchase.py")
    >>> voting = interface.Voting("0x2e59A20f205bB85a89C53f1936454680651E618e")
    >>> voting.getVote(44)
    ```
