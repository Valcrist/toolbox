import json
import asyncio
import aiohttp
from toolbox.runner import run_async_tasks
from toolbox.utils import debug, err, warn, exc


async def async_get_url(
    url: str | list[str],
    headers: dict = {},
    payload: dict = {},
    response_type: str = "text",
):

    async def decode_response(resp: aiohttp.ClientResponse, response_type: str):
        if response_type == "json":
            try:
                return await resp.json()
            except:
                pass  # fallback to text if it's not json
        return (await resp.text()).strip()

    async def prep_response(resp: aiohttp.ClientResponse, url: str, response_type: str):
        response = {
            "url": url,
            "code": resp.status,
            "resp": await decode_response(resp, response_type),
        }
        debug(response, url, lvl=3)
        return response

    async def fetch_url(url: str) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                if payload:
                    async with session.get(
                        url, headers=headers, data=json.dumps(payload)
                    ) as resp:
                        return await prep_response(
                            resp, url, response_type=response_type
                        )
                else:
                    async with session.get(url, headers=headers) as resp:
                        return await prep_response(
                            resp, url, response_type=response_type
                        )
        except Exception as e:
            err(f"{url}: {e}")
            warn(f"{url}:\n{exc()}")
            return {"code": -1, "resp": None}

    result = (
        await asyncio.gather(*[fetch_url(u) for u in url])
        if isinstance(url, list)
        else [await fetch_url(url)]
    )
    debug(result, "result", lvl=3)
    response = {r["url"]: {"code": r["code"], "resp": r["resp"]} for r in result}
    return (
        response[url[0] if isinstance(url, list) else url]
        if len(response) == 1
        else response
    )


def get_url(
    url: str | list[str],
    headers: dict = {},
    payload: dict = {},
    response_type: str = "text",
):
    return run_async_tasks(
        async_get_url(
            url, headers=headers, payload=payload, response_type=response_type
        )
    )
