import json
import time
import asyncio
from typing import Callable, Awaitable
from fnmatch import fnmatch
from toolbox.utils import debug, hr

try:
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import Response, StreamingResponse
    from starlette.routing import Route
    from scalar_fastapi import get_scalar_api_reference
except ImportError as e:
    raise ImportError(
        "api tools requires optional dependencies. "
        "Install with: pip install toolbox[api]"
    ) from e


def logger_middleware(
    app: FastAPI,
    env: str,
    log_requests: bool = False,
    log_response: bool = False,
    skip_paths: list[str] | None = None,
    tarpit_max_concurrent: int = 20,
    tarpit_delay: int = 300,
) -> None:
    """Register HTTP middleware that logs req/resp and tarpits unknown routes."""
    skip = set(["/", "/docs", "/openapi.json", "/favicon.ico"] + (skip_paths or []))
    tarpit_sem = asyncio.Semaphore(tarpit_max_concurrent)

    def get_valid_routes() -> list[Route]:
        return [route for route in app.routes if isinstance(route, Route)]

    @app.middleware("http")
    async def log_api_io(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        url = request.url.path
        is_valid_route = any(
            route.path_regex.match(url) for route in get_valid_routes()
        )
        if any(fnmatch(url, p) for p in skip):
            return await call_next(request)
        if not is_valid_route:
            if tarpit_sem.locked():
                return Response(status_code=403)
            async with tarpit_sem:
                await asyncio.sleep(tarpit_delay)
            return Response(status_code=403)

        start_time = time.perf_counter()

        if env == "DEV" or log_requests:
            hr("←", color="bright_magenta", no_nl=True)
            try:
                debug(dict(request.headers), f"[REQ:headers] {url}", no_nl=True)
            except Exception:
                debug(str(request.headers), f"[REQ:headers] {url}", no_nl=True)
            body = await request.body()
            if body:
                print()
                try:
                    debug(json.loads(body), f"[REQ:body] {url}", no_nl=True)
                except json.JSONDecodeError:
                    debug(
                        body.decode(errors="ignore")[:1000],
                        f"[REQ:body] {url}",
                        no_nl=True,
                    )
            hr("←", color="bright_magenta", no_leading_nl=True)

            async def receive():
                return {"type": "http.request", "body": body, "more_body": False}

            request = Request(request.scope, receive)

        response: StreamingResponse = await call_next(request)  # type: ignore
        process_time = (time.perf_counter() - start_time) * 1000
        log_tag = f"[RESP:{response.status_code}] {url} ({process_time:.2f}ms)"

        if env == "DEV" or log_response:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += (
                    chunk
                    if isinstance(chunk, bytes)
                    else bytes(chunk) if not isinstance(chunk, str) else chunk.encode()
                )

            hr("→", color="yellow", no_nl=True)
            if response_body:
                content_type = response.media_type or response.headers.get(
                    "content-type", ""
                )
                if "json" in content_type:
                    try:
                        debug(json.loads(response_body), log_tag, no_nl=True)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        debug(
                            response_body.decode(errors="ignore"), log_tag, no_nl=True
                        )
                else:
                    debug(
                        url,
                        f"[RESP:{response.status_code}] binary ({process_time:.2f}ms)",
                        no_nl=True,
                    )
            else:
                debug({response.status_code}, log_tag, no_nl=True)
            hr("→", color="yellow", no_leading_nl=True)

            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
                background=response.background,
            )

        debug(
            f"response took {process_time:.2f}ms",
            f"[RESP:{response.status_code}] {url}",
        )
        return response


def init_scalar_docs(
    app: FastAPI,
    title: str,
    favicon_url: str = "",
    dark_mode: bool = True,
    targets: list[str] | None = None,
    default_http_client: dict | None = None,
    **kwargs,
) -> None:
    """Register a /docs route serving Scalar API reference for the app."""

    @app.get("/docs", include_in_schema=False)
    async def scalar_html():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=title,
            scalar_favicon_url=favicon_url,
            dark_mode=dark_mode,
            force_dark_mode_state="dark" if dark_mode else "light",
            overrides={
                "targets": targets or ["shell", "python3", "node"],
                "defaultHttpClient": default_http_client
                or {"targetKey": "python", "clientKey": "httpx_async"},
            },
            **kwargs,
        )


def run_server(
    module: str,
    env: str,
    port: int = 8080,
    hot_reload: bool = False,
    use_ssl: bool = False,
    ssl_keyfile: str | None = None,
    ssl_certfile: str | None = None,
) -> None:
    """Start a uvicorn server for the given ASGI module string."""
    ssl_mode = "SSL" if ssl_keyfile and ssl_certfile else "no SSL"
    print(f"\n{'=' * 80}\n[FastAPI] Running in {env} Mode ({ssl_mode})\n{'=' * 80}\n")
    uvicorn.run(
        module,
        port=port,
        host="0.0.0.0",
        ssl_keyfile=ssl_keyfile if use_ssl else None,
        ssl_certfile=ssl_certfile if use_ssl else None,
        reload=hot_reload,
        log_level="info",
    )
