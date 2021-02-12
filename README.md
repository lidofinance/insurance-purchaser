# Insurance purchasing contract for Lido

Contains a proxy contract which takes LDO and stETH tokens from treasury and convert them to ETH (LDO -> stETH -> ETH) and than purchase insurance by Unslashed which covers eth2 validators slashing.

## Development

### Dependencies

* [python3](https://www.python.org/downloads/release/python-390/) from version 3.7 to 3.9
* [brownie](https://github.com/iamdefinitelyahuman/brownie) - version 1.13.1
* [ganache-cli](https://github.com/trufflesuite/ganache-cli) - version 6.12.1

### Dev and test

To get started, first create and initialize a Python [virtual environment](https://docs.python.org/3/library/venv.html). Next, clone the repo and install the developer dependencies:

```bash
git clone https://github.com/lidofinance/insurance-purchaser.git
cd insurance-purchaser
export WEB3_INFURA_PROJECT_ID=infura-token
brownie test
```

## Check aragon vote execution script

To validate that proposed vote for transferring tokens (LDO, stETH) to the InsurancePurchaser is correct, you need to do following steps:

1. Open Lido [`voting app`](https://etherscan.io/address/0x2e59A20f205bB85a89C53f1936454680651E618e#readProxyContract) in the etherscan and fetch the vote with the corresponding `id` and extract the `script` field content.

2. Ensure that the configuration settings of proposed purchase is correct [`scripts/generate_purchase_exec_script.py`](scripts/generate_purchase_exec_script.py).

3. Run the script and ensure that it match the extracted one from etherscan.

    ```bash
    brownie run generate_purchase_exec_script --network mainnet
    ```
    When the script completes it will print the generated exec script.


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
3. Set DEPLOYER env variable to the deployer account name first (from ~/.brownie/accounts). Important: DEPLOYER acc should have some LDO governance token to be able to submit new vote.

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

2. Deploy insurance purchaser with script from the console
    ```bash
    >>> run("deploy.py")
    >>> purchaser = InsurancePurchaser.at("0x602C71e4DAC47a042Ee7f46E0aee17F94A3bA0B6")
    ```

3. Edit the configuration settings within [`propose_insurance_purchase.py`](propose_insurance_purchase.py). Put right address for InsurancePurchaser.

4. Get some LDO tokens to be able to submit a vote
    ```bash
    >>> run("get_coins.py")
    >>> ldo_token = interface.ERC20("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32")
    >>> ldo_token.balanceOf(accounts[0])
    ```

5. Propose a vote and check the script
    ```bash
    >>> run("propose_insurance_purchase.py")
    >>> voting = interface.Voting("0x2e59A20f205bB85a89C53f1936454680651E618e")
    >>> voting.getVote(44)
    ```