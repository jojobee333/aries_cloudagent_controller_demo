import asyncio
import json
from enum import Enum
from pprint import pprint

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
        json_response = None
        try:
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
            json_response = json.loads(response)
        except Exception as e:
            logging.warning(e, exc_info=True)
        if json_response is not None:
            print(f"Schema has been successfully registered.\nSchema ID: {json_response}")
            return json_response
        else:
            return "There was an error in creating a schema."

    async def get_registered_schema(self):
        url = f"{ADMIN_ENDPOINT}/schemas/created"

    async def generate_invite(self, auto_accept: bool, did_exchange=False, mediation=False, mediation_id=None):
        # specify a connection id to ensure it has been reset to None.
        params = {"auto_accept": json.dumps(auto_accept)}
        if did_exchange:
            suffix = "/out-of-band/create-invitation"
            payload = {"handshake_protocols": ["rfc23"]}
            invite = await self.admin_request(method="POST",
                                              suffix=suffix, payload=payload,
                                              params=params,
                                              )
        else:
            suffix = "/connections/create-invitation"
            if mediation:
                if not mediation_id:
                    mediation_id = input(f"Please provide a mediation id.\n Mediation is set to {mediation}:")
                    payload = {"mediation_id", mediation_id}
                    invite = await self.admin_request(
                        method="POST", suffix=suffix,
                        payload={"mediation_id": mediation_id},
                        params={"auto_accept": json.dumps(auto_accept)},)
            else:
                suffix = "/connections/create-invitation"
                invite = await self.admin_request(method="POST", suffix=suffix, payload=None, params=None)
        pprint(invite)
        return invite
        # endpoint = f"{ADMIN_ENDPOINT}/connections/create-invitation"
        # headers = "application/json"
        # payload = {
        #     "handshake_protocols": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/1.0",
        #     "auto_accept": auto_accept,
        #     "public": public,
        # }


key = "EXI6rzZH9xuMR7b5zo8gRjPkvCKeEQqLJsLvgsJ/iWpwTu9+XEI2NhPcooDxkVS5"
