import asyncio
from aiohttp import ClientSession
from con_config import *
from con_endpoints import Endpoints


class MainAgent(Endpoints):
    """This class contains agent routines - multistep tasks."""

    def __init__(self, identity: str, label: str):
        super().__init__()
        self.identity = identity
        self.label = label
        self.process = None
        self.connection_id = None

    async def create_wallet(self, overwrite=False, wallet_key=None, wallet_type='indy', wallet_name='My Wallet'):
        """Provisions a wallet.  No support for askar type at this time."""
        seed_for_wallet = self.generate_seed(bytestring=False, label=self.label, length=32)
        logging.info(f"Seed Value: {seed_for_wallet}")
        wallet_types = {"indy", "basic"}
        wallet_name = input("Wallet Name: ")
        wallet_type = input(f"Wallet Type:\nChoose {' or '.join(wallet_types)}.").lower()
        if wallet_type not in wallet_types:
            logging.warning(f"Invalid entry. Default will be selected: {wallet_type}")
            wallet_type = "indy"
        if not wallet_key:
            wallet_key = self.generate_seed(bytestring=False, label=self.label)
        print(f"Wallet Key: {wallet_key}")
        try:
            await self.provision_agent(process=self.process,
                                       endpoint=ADMIN_ENDPOINT,
                                       recreate_wallet=overwrite,
                                       genesis_url=GENESIS_ENDPOINT,
                                       wallet_name=wallet_name,
                                       wallet_type=wallet_type,
                                       wallet_key=wallet_key,
                                       seed=seed_for_wallet,
                                       profile_endpoint=PROFILE_ENDPOINT,
                                       )
            did, ver_key = await self.register_did(alias=self.label, seed=seed_for_wallet, local_scope=False)
            if did is None and ver_key is None:
                logging.error("Error: Could not register wallet.")
                return None
            wallet_info = {
                "Wallet Name": wallet_name,
                "Wallet Type": wallet_type,
                "Wallet Key": wallet_key,
                "Wallet DID": did,
                "Wallet VerKey": ver_key,
                "Wallet Seed": seed_for_wallet,
            }
            logging.info(wallet_info)
            return wallet_info
        except Exception as e:
            logging.error(f"Error creating wallet: {str(e)}")
            return None

    async def schema_query_second_menu(self):
        schema_name = None
        schema_id = None
        schema_version = None
        schema_issuer_did = None
        selection = int(
            input("Which parameter would you like to query?\n1.Name\n2.ID\n3.Version\n4.Issuer DID"))
        match selection:
            case 1:
                schema_name = input("Schema Name?")
            case 2:
                schema_id = input("Schema Id?")
            case 3:
                schema_version = input("Schema Version?")
            case 4:
                schema_issuer_did = input("Schema Issuer Did?")
        response = await self.search_schema(schema_id=schema_id,
                                            schema_version=schema_version,
                                            schema_issuer_did=schema_issuer_did,
                                            schema_name=schema_name)
        return response

    async def schema_query_primary_menu(self):
        schema_menu = True
        print("SCHEMA MENU")
        options = {
            1: {
                "text": "Use the Config Parameters",
                "action": self.search_schema,
                "args": {'schema_id': SCHEMA_ID,
                         'schema_name': SCHEMA_NAME,
                         'schema_version': SCHEMA_VERSION,
                         'schema_issuer_did': SCHEMA_ISSUER_DID}
            },
            2: {
                "text": "Enter Manually",
                "action": self.schema_query_second_menu,
                "args": {},
            },
        }
        while schema_menu:
            for num, opt in options.items():
                print(f"{num}. {opt['text']}")
            try:
                option_choice = int(input("Enter option number: "))
            except ValueError:
                print("Invalid input. Please enter a number.\n")
                continue

            if option_choice in options:
                option = options[option_choice]
                print(f"Performing action: {option['text']}")
                schema_menu = False
                await option['action'](**option['args'])
            else:
                print("Invalid option. Please choose a valid option.\n")


async def debug_menu(base):
    debug = True
    debug_options = {
        1: {
            "text": "is agent running",
            "action": base.config_ports_in_use,
            "args": {}
        },
        2: {
            "text": "get_genesis",
            "action": base.get_genesis,
            "args": {"genesis_url": GENESIS_ENDPOINT,
                     }
        }
    }
    print("DEBUG MENU OPTIONS:")
    while debug:
        for num, opt in debug_options.items():
            print(f"{num}. {opt['text']}")
        try:
            option_choice = int(input("Enter option number: "))
        except ValueError:
            print("Invalid input. Please enter a number.\n")
            continue
        if option_choice in debug_options:
            option = debug_options[option_choice]
            print(f"Performing action: {option['text']}")
            debug = False
            try:
                await option['action'](**option['args'])
            except Exception as e:
                option['action'](**option['args'])
        else:
            print("Invalid option. Please choose a valid option.\n")


async def main():
    base = MainAgent(identity="Julie", label="Julie")
    is_agent_running = base.config_ports_in_use()
    get_genesis = await base.get_genesis(GENESIS_ENDPOINT)
    options = {
        1: {
            'text': "Start Agent",
            'action': base.start_agent,
            'args': {
                'process': base.process,
                'endpoint': INBOUND_TRANSPORT,
                'label': base.label,
                'inbound_transport': (OUTBOUND, INTERNAL, str(INBOUND_PORT)),
                'outbound_transport': OUTBOUND,
                'admin_url': (INTERNAL, str(ADMIN_PORT)),
                'wallet_name': DEFAULT_WALLET_NAME,
                'wallet_type': DEFAULT_WALLET_TYPE,
                'wallet_key': DEFAULT_KEY,
                'genesis_url': GENESIS_ENDPOINT,
                'genesis_transactions': get_genesis,
                'debug': True,
                'debug_automate': True,
                'public_invites': True,
            }
        },
        2: {
            'text': "Stop Agent",
            'action': base.terminate_agent,
            'args': {}
        },
        3: {
            'text': "Create Wallet",
            'action': base.create_wallet,
            'args': {
                'prompt': True,
                'key': DEFAULT_KEY
            },
        },
        4: {
            'text': "Register Schema",
            'action': base.create_schema,
            'args': {
                'attr': SCHEMA_ATTR,
                'name': SCHEMA_NAME,
                'version': SCHEMA_VERSION
            }
        },
        5: {
            'text': "Schema Search",
            'action': base.schema_query_primary_menu,
            'args': {

            }
        },
        6: {
            'text': "Create Invitation",
            'action': base.generate_invite,
            'args': {
                'auto_accept': True,
            },
        },
        7: {
            'text': "Debug Menu",
            'action': debug_menu,
            'args': {
                'base': base,
            },
        }
    }
    while True:
        await asyncio.sleep(2.0)
        print("OPTIONS:")
        for num, opt in options.items():
            print(f"{num}. {opt['text']}")

        try:
            option_choice = int(input("Enter option number: "))
        except ValueError:
            print("Invalid input. Please enter a number.\n")
            continue

        if option_choice in options:
            option = options[option_choice]
            print(f"Performing action: {option['text']}")
            try:
                await option['action'](**option['args'])
            except Exception as e:
                option['action'](**option['args'])
        else:
            print("Invalid option. Please choose a valid option.\n")


asyncio.run(main())
