import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
OUTBOUND = None
ENDPOINT_PORT: int = 0
INBOUND_PORT: int = 0
PROFILE_PORT: int = 0
GENESIS_PORT: int = 0
ADMIN_PORT: int = 0
PORTS = [INBOUND_PORT, ADMIN_PORT]
INTERNAL = "0.0.0.0"
EXTERNAL = "localhost"
LOCAL_IP = "your_local_ip"

LEDGER_URL = f"{OUTBOUND}://{EXTERNAL}:{str(GENESIS_PORT)}"
GENESIS_ENDPOINT = f"{OUTBOUND}://{EXTERNAL}:{str(GENESIS_PORT)}/genesis"
ADMIN_ENDPOINT = f"{OUTBOUND}://{INTERNAL}:{str(ADMIN_PORT)}"
PROFILE_ENDPOINT = f"{OUTBOUND}://{INTERNAL}:{str(PROFILE_PORT)}"
INBOUND_TRANSPORT = f"{OUTBOUND}://{INTERNAL}:{str(INBOUND_PORT)}"
ENDPOINT = f'{OUTBOUND}://{LOCAL_IP}:{str(INBOUND_PORT)}'

DEFAULT_KEY = "Your key"
DEFAULT_WALLET_NAME = "Alice"
DEFAULT_WALLET_TYPE = "indy"
VER_KEY = None
SEED = "Your seed"

SCHEMA_ID = None
SCHEMA_ISSUER_DID = None
SCHEMA_ATTR = ["name", "age", "DOB"]
SCHEMA_NAME = "example_schema"
SCHEMA_VERSION = "1.0"





