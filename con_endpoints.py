import asyncio
import json
from enum import Enum
from pprint import pprint

from aiohttp import ClientSession, ClientError, ClientTimeout
from con_config import *
from con_utils import Utilities
from con_admin import Admin





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

    async def search_schema(self, schema_id=None, schema_issuer_did=None, schema_name=None, schema_version=None):
        suffix = "/schemas/created"
        payload = {}
        if schema_id:
            payload["schema_id"] = schema_id
        if schema_issuer_did:
            payload["schema_issuer_did"] = schema_issuer_did
        if schema_name:
            payload["schema_name"] = schema_name
        if schema_version:
            payload["schema_version"] = schema_version
        response = await self.admin_request(method="GET", suffix=suffix, payload=payload)
        pprint(response)
        # print(payload)

    async def register_creddef(self, schema_id):
        # Get schema id.
        pass

    async def generate_invite(self, auto_accept: bool, did_exchange=False, mediation=False, mediation_id=None):
        invite = None
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

