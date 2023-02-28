import asyncio
import json
from enum import Enum
from aiohttp import ClientSession, ClientError, ClientTimeout
from con_config import *
from con_utils import Utilities
from con_admin import Admin


class Provision(Enum):
    CREATE_WALLET = 1
    CREATE_SCHEMA = 2


class Endpoints(Admin):
    def __init__(self):
        super().__init__()
        pass

    async def create_schema(self, attr: list, name, version):
        method = "POST"
        suffix = "/schemas"
        url = f"http://0.0.0.0:{str(ADMIN_PORT)}/schemas"
        payload = json.dumps({
            "attributes": attr,
            "schema_name": name,
            "schema_version": version
        })
        headers = {
            "content-type": "application/json"
        }
        response = await self.admin_request(method=method, suffix=suffix, payload=payload, headers=headers)
        print(response)
        return response

    async def get_registered_schema(self):
        url = f"{ADMIN_ENDPOINT}/schemas/created"

    async def create_invite(self, public: bool, multi_use: bool, auto_accept: bool):
        endpoint = f"{ADMIN_ENDPOINT}/connections/create-invitation"
        headers = "application/json"
        payload = {
            "handshake_protocols": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/1.0",
            "auto_accept": auto_accept,
            "multi_use": multi_use,
            "public": public,
        }


key = "EXI6rzZH9xuMR7b5zo8gRjPkvCKeEQqLJsLvgsJ/iWpwTu9+XEI2NhPcooDxkVS5"
