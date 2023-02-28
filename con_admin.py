import asyncio
import os
from urllib.error import HTTPError
import subprocess
from aiohttp import ClientSession, ClientConnectorError
from con_endpoints import *
from con_utils import *


class Admin(Utilities):
    def __init__(self):
        super().__init__()

    async def provision_agent(
            self,
            process,
            wallet_name,
            wallet_key,
            wallet_type,
            endpoint,
            profile_endpoint=None,
            recreate_wallet=None,
            seed=None,
            genesis_url=None,
            genesis_file=None,
            endorser_public_did=None,
    ):
        provision_args = [
            ("--endpoint", endpoint),
            ("--wallet-type", wallet_type),
            ("--wallet-name", wallet_name),
            ("--wallet-key", wallet_key),
            ("--seed", seed) if seed else ("--seed", self.generate_seed(length=32, bytestring=False))
        ]
        if profile_endpoint:
            provision_args.append(("--profile-endpoint", profile_endpoint))
        if recreate_wallet:
            provision_args.append("--recreate-wallet")
        if genesis_url:
            provision_args.append(("--genesis-url", genesis_url))
            provision_args.append(("--genesis-transactions", await self.get_genesis(genesis_url)))
        elif genesis_file:
            provision_args.append(("--genesis-file", genesis_file))
        else:
            provision_args.append(("--genesis-url", "http://localhost:9000"))

        if self.config_ports_in_use:
            await self.terminate_agent()
        command = ["aca-py", "provision"] + list(self.flatten(provision_args))
        print(command)
        await self.run_process(process=process, args=command)
        # pprint(command)

    async def start_agent(self,
                          process,
                          endpoint=None,
                          label=None,
                          inbound_transport=None,
                          outbound_transport=None,
                          admin_url=None,
                          wallet_name=None,
                          wallet_type=None,
                          wallet_key=None,
                          wallet_storage_type="default",
                          genesis_url=None,
                          genesis_transactions=None,
                          debug=True,
                          debug_automate=True,
                          public_invites=True,
                          preserve_exchange_records=True,
                          trace_target="log",
                          trace_tag="acapy.trace",
                          trace_label="acapy.event",
                          # endorser_public_did=None

                          ):
        agent_args = [
            ("--endpoint", endpoint),
            ("--label", label),
            ("--inbound-transport", inbound_transport),
            ("--outbound-transport", outbound_transport),
            ("--admin", admin_url),
            ("--wallet-type", wallet_type),
            ("--wallet-name", wallet_name),
            ("--wallet-storage-type", wallet_storage_type),
            ("--wallet-key", wallet_key),
            ("--genesis-url", genesis_url),
            ("--genesis-transactions", genesis_transactions),
            "--auto-provision"
        ]
        if debug:
            agent_args.append(["--admin-insecure-mode",
                               "--debug-connections",
                               "--debug-credentials",
                               "--trace",
                               ("--trace-target", trace_target),
                               ("--trace-tag", trace_tag),
                               ("--trace-label", trace_label)],
                              )
        # if endorser_public_did:
        #     agent_args.append(("--endorser-public-did", endorser_public_did))
        if debug_automate:
            agent_args.append([
                "--auto-ping-connection",
                "--auto-respond-messages"
            ])
        if public_invites:
            agent_args.append("--public-invites")
        if preserve_exchange_records:
            agent_args.append("--preserve-exchange-records")
        # check if agent is already running.
        if self.config_ports_in_use:
            await self.terminate_agent()
        await asyncio.sleep(2.0)
        flattened = list(self.flatten(agent_args))
        command = ["aca-py", "start"] + flattened
        logging.debug(command)
        try:
            await self.run_process(process=process, args=command)
        except Exception as e:
            print("Error")


    def config_ports_in_use(self):
        occupied_ports = [port for port in PORTS if self.is_port_in_use(INTERNAL, port)]
        if occupied_ports:
            print(f"The following ports are occupied:{occupied_ports}.")
            return occupied_ports
        else:
            print("All ports are available.")
            return []

    async def get_genesis(self, genesis_url: str) -> str:
        """Configures an Aries Cloud Agent to use a genesis URL."""
        # logging.debug(genesis_url)
        # os.environ["GENESIS_URL"] = genesis_url
        headers = {
            "content-type": "application/json",
            "accept": "application/json"
        }
        async with ClientSession() as session:
            try:
                async with session.get(genesis_url, headers=headers) as response:
                    logging.debug(f"Received response: {response.status}")
                    if response.status != 200:
                        logging.warning("Error loading genesis.", exc_info=True)
                    result = await response.text()
                    # logging.debug(f"Received text: {result}")
            except ClientConnectorError as e:
                logging.critical("Error: ", e, exc_info=True)
            else:
                logging.info("Got an OK response for retrieving genesis transactions.")
                return result

    async def register_did(self, alias, seed=None, local_scope: bool = True, did=None,
                           non_local_role: str = "TRUST_ANCHOR"):
        json_response = None
        headers = {'Content-Type': 'application/json'}
        session = ClientSession()
        if local_scope:
            # for a local did to be added to a wallet
            endpoint = f"{ADMIN_ENDPOINT}/wallet/did/create"
            payload = {
                "method": "sov",
                "options": {"key_type": "ed25519"}
            }
        else:
            # for an issuer agent to register did to a ledger
            endpoint = f"{LEDGER_URL}/register"
            if not seed:
                seed = self.generate_seed(bytestring=False, length=32)
            payload = {"seed": seed,
                       "role": non_local_role,
                       "alias": alias}
            if did:
                payload["did"] = did
        try:
            response = await session.post(url=endpoint, json=payload, headers=headers)
            # status = response.status
            json_response = await response.json()
        except Exception as e:
            logging.warning("Error:", exc_info=True)
        await session.close()
        if json_response:
            print("DID registered to Ledger", json_response)
            return (json_response["result"]["did"], json_response["result"]["verkey"]) if local_scope else (
                json_response["did"], json_response["verkey"])
        else:
            return "None", "None"

    async def admin_request(self, method, suffix, headers=None, payload=None, params=None):
        admin_url = ADMIN_ENDPOINT + suffix
        logging.debug(admin_url)
        async with ClientSession() as session:
            try:
                async with session.request(method=method, url=admin_url, data=payload, headers=headers, params=params) as response:
                    response = await response.text()
            except Exception as ConnectionError:
                logging.critical(f"{ConnectionError}\nError occurred during admin {method}.")
            else:
                return response


    async def run_process(self, args, process):
        try:
            process = subprocess.Popen(args, shell=False)
        except Exception as e:
            logging.warning(f"Error running command {args}: {e}")

    async def terminate_agent(self):
        try:
            response = await self.admin_request(method="GET", suffix="/shutdown")
        except Exception as e:
            return "Agent may already be closed."
        else:
            print(f"Agent has been closed successfully: {response}")
        # except Exception as e:
        #     logging.warning("Ran into issue terminating agent. Agent may already be closed.")
