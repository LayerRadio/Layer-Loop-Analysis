import aiohttp
import asyncio
from typing import Optional
from data.constants import REST_API, NFTINFOS_API

class LoopringApiServices:
    aiohttp_client: Optional[aiohttp.ClientSession] = None

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:

        asyncio.set_event_loop(asyncio.new_event_loop())
        timeout = aiohttp.ClientTimeout(total=4)
        cls.aiohttp_client = aiohttp.ClientSession()
        return cls.aiohttp_client

    @classmethod
    async def query_url(cls, url: str, tokenAddress: str):
        client = cls.get_aiohttp_client()
        try:
            address = NFTINFOS_API["NftInfosApi"] + "/" + str(tokenAddress)
            async with client.get(address) as response:
                json_result = await response.json()

        except Exception as err:
            print('Exception in LoopringApiService:', flush=True)
            print(tokenAddress, flush=True)
            print(err, flush=True)
            await client.close()
            return None

        await client.close()
        return json_result

    async def getCollectionsNftInfos(self, tokenAddress: str):
        params = {}
        headers = {}
        headers = {
            'accept': 'application/json',
            'User-Agent': 'Mozilla'
        }
        try:
            address = "/" + str(tokenAddress)
            response = await self.session.get(address, headers=headers)
            await asyncio.sleep(0)
        except Exception as err:
            print('Error in getCollectionsNftInfos: ' + str(err.errors[0]['message']), flush=True)
            print(tokenAddress)
            return None

        return response.json()

    async def getCollectionsByContract(self, tokenAddress: str, minterAddress: str, nftId: str, limit: int, offset: int):
        params = {"tokenAddress": tokenAddress,
                  "minter": minterAddress,
                  "nftId": nftId,
                  "limit": limit,
                  "offset": offset}
        headers = {}
        response = await self.session.get("/api/v3/nft/public/collection/items", params=params, headers=headers)
        parsed = await response.json()
        return parsed['nftData'], parsed # parsed is just there for debugging
