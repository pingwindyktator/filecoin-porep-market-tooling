# Filecoin PoRep Market Tooling
Python3 CLI tool for interacting with [Filecoin PoRep market](https://github.com/fidlabs/porep-market) smart contracts using [Click](https://click.palletsprojects.com/en/stable/#), [Web3](https://web3py.readthedocs.io/en/stable/) and [psycopg](https://www.psycopg.org/docs/). \
Developed for admins, clients, and SPs to **manage their market interactions** from command line.


## Installation
**Use python >= 3.10**
```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```


## Running the CLI
Make sure you have the required environment variables (see `.env`). \
Run the script: `python3 ./porep_tooling_cli.py` and follow help prompts.


## Important notes
- The app **does not store any state** locally - all state is retrieved from the blockchain by the design.
- The app writes all blockchain transaction logs to `logs/`.
- All write transactions **require manual user confirmation** before sending. There is no option to override this. \
If you decline the final confirmation, the command falls back to dry-run behavior without broadcasting the transaction.
- To avoid confusion, for all write transactions, the app expects the `--address` option to match `--private-key` option.
- Default behaviour is to wait for the previous transaction confirmation BEFORE sending the next one and NOT AFTER the transaction. \
This means that the app does not wait for the transaction receipt after sending it. \
This behaviour may change in the future.
- Read-only operations does not require confirmations.
- Read-only operations does not require `--private-key` set, though some of them require `--address`.
- The app operates on ETH 0x-addresses and **FEVM smart contract** and does not fully support Filecoin f-addresses.


## Security considerations
- The app runs locally and does not transmit any data to external servers.
- The app does not log any sensitive information.
- The only place where private keys should be stored is local `.env` file. \
**Be aware** that when using `--private-key` option, the private key may be visible in the command history or process list. \
This is a default system behavior and is not specific to this app.


## Developing new CLI commands
See files in `cli/commands` and follow the patterns! Also, see `./cli/test.sh`!
