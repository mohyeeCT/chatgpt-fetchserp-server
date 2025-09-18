#!/usr/bin/env python3
"""
Minimal FetchSERP MCP server:
- Only two tools exposed to ChatGPT: `search` and `fetch`.
- `search` returns keyword search volume using GET /api/v1/keywords_search_volume.
- `fetch` scrapes a URL using GET /api/v1/scrape.
- Compatible with MCP over HTTP as used by ChatGPT connectors:
  * POST JSON-RPC 2.0 at /mcp and /mcp/
  * initialize -> tools/list -> tools/call
  * Version negotiation and MCP-Protocol-Version header per spec.

Env:
- FETCHSERP_API_TOKEN required
- FETCHSERP_BASE_URL optional. Defaults to https://www.fetchserp.com

Run:
uvicorn server_min_kv_fetch:app --host 0.0.0.0 --port $PORT
"""
import os
import json
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

APP_NAME = "FetchSERP MCP Server - Minimal KV+Fetch"
APP_VERSION = "0.2.0"

# MCP protocol
LATEST_PROTOCOL = "2025-06-18"
SUPPORTED_PROTOCOLS = {LATEST_PROTOCOL, "2025-03-26", "2024-11-05"}

# Config
FETCHSERP_API_TOKEN = os.getenv("FETCHSERP_API_TOKEN")
FETCHSERP_BASE_URL = os.getenv("FETCHSERP_BASE_URL", "https://www.fetchserp.com")

# FastAPI app
app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_protocol_header(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["MCP-Protocol-Version"] = LATEST_PROTOCOL
    return resp

# -------------- Health and banners --------------
@app.get("/")
async def root():
    return {
        "ok": True,
        "app": APP_NAME,
        "version": APP_VERSION,
        "mcp": {"protocolRevision": LATEST_PROTOCOL, "endpoints": ["/mcp", "/mcp/"]},
    }

@app.head("/")
async def head_root():
    return Response(status_code=204)

@app.get("/mcp")
@app.get("/mcp/")
async def mcp_banner():
    return {"ok": True, "message": "MCP JSON-RPC endpoint. Use POST to call JSON-RPC.", "methods": ["POST"]}

@app.head("/mcp")
@app.head("/mcp/")
async def mcp_head():
    return Response(status_code=204)

# -------------- Helpers --------------
def _client() -> httpx.AsyncClient:
    headers = {}
    if FETCHSERP_API_TOKEN:
        headers["Authorization"] = f"Bearer {FETCHSERP_API_TOKEN}"
    return httpx.AsyncClient(base_url=FETCHSERP_BASE_URL, headers=headers, timeout=60.0)

def _jsonrpc_result(id_value: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id_value, "result": result}

def _jsonrpc_error(id_value: Any, code: int, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    err = {"jsonrpc": "2.0", "id": id_value, "error": {"code": code, "message": message}}
    if data is not None:
        err["error"]["data"] = data
    return err

def _tools_list_result() -> Dict[str, Any]:
    def obj(props, required=None, additional=True):
        return {"type": "object", "properties": props, "required": required or [], "additionalProperties": additional}

    return {
        "tools": [
            {
                "name": "search",
                "description": "Get keyword search volume. Wraps GET /api/v1/keywords_search_volume.",
                "inputSchema": obj(
                    {
                        "keyword": {"type": "string", "description": "Keyword to look up"},
                        "country": {"type": "string", "default": "us", "description": "Country code, for example us"},
                        "language": {"type": "string", "default": "en", "description": "Language code"},
                    },
                    ["keyword"],
                    additional=False,
                ),
            },
            {
                "name": "fetch",
                "description": "Scrape a URL and return raw HTML using GET /api/v1/scrape.",
                "inputSchema": obj(
                    {
                        "url": {"type": "string", "description": "Absolute URL to scrape"},
                    },
                    ["url"],
                    additional=False,
                ),
            },
        ]
    }

async def _call_fetchserp(path: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    async with _client() as client:
        if method == "GET":
            r = await client.get(path, params=params)
        else:
            r = await client.post(path, json=params)
        r.raise_for_status()
        return r.json()

# -------------- Tool execution --------------
async def _handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if not FETCHSERP_API_TOKEN:
        raise RuntimeError("FETCHSERP_API_TOKEN is not set")

    if name == "search":
        # Keyword volume
        keyword = arguments.get("keyword")
        if not keyword:
            return {"content": [{"type": "text", "text": json.dumps({"error": "missing keyword"}, ensure_ascii=False)}]}

        params = {
            "keyword": keyword,
            "country": arguments.get("country", "us"),
            "language": arguments.get("language", "en"),
        }
        data = await _call_fetchserp("/api/v1/keywords_search_volume", "GET", params)
        # Pass through upstream response
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}

    if name == "fetch":
        url = arguments.get("url")
        if not url:
            return {"content": [{"type": "text", "text": json.dumps({"error": "missing url"}, ensure_ascii=False)}]}
        data = await _call_fetchserp("/api/v1/scrape", "GET", {"url": url})
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}

    return {"content": [{"type": "text", "text": json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)}]}

# -------------- JSON-RPC dispatch --------------
def _negotiate_protocol(client_ver: Optional[str]) -> str:
    return client_ver if client_ver in SUPPORTED_PROTOCOLS else LATEST_PROTOCOL

async def _dispatch(body: Dict[str, Any]) -> Dict[str, Any]:
    method = body.get("method")
    rid = body.get("id")
    params = body.get("params") or {}

    if method == "initialize":
        client_ver = None
        if isinstance(params, dict):
            client_ver = params.get("protocolVersion") or params.get("protocol_version")
        version = _negotiate_protocol(client_ver)
        return _jsonrpc_result(
            rid,
            {
                "protocolVersion": version,
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {},
                },
                "serverInfo": {"name": APP_NAME, "version": APP_VERSION},
            },
        )

    if method in ("tools/list", "tools.list"):
        return _jsonrpc_result(rid, _tools_list_result())

    # Optional features: return empty lists instead of method not found
    if method in ("resources/list", "resources.list"):
        return _jsonrpc_result(rid, {"resources": []})
    if method in ("prompts/list", "prompts.list"):
        return _jsonrpc_result(rid, {"prompts": []})

    if method in ("tools/call", "tools.call"):
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            result = await _handle_tool_call(name, arguments)
            return _jsonrpc_result(rid, result)
        except httpx.HTTPStatusError as e:
            return _jsonrpc_error(rid, -32001, "Upstream FetchSERP error", {"status": e.response.status_code, "body": e.response.text})
        except Exception as e:
            return _jsonrpc_error(rid, -32000, f"Server error: {str(e)}")

    return _jsonrpc_error(rid, -32601, f"Method not found: {method}")

# -------------- HTTP handlers --------------
@app.post("/mcp")
@app.post("/mcp/")
async def mcp_handler(request: Request) -> Response:
    try:
        body = await request.json()
    except Exception:
        return Response(
            content=json.dumps(_jsonrpc_error(None, -32700, "Parse error")),
            media_type="application/json",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    result = await _dispatch(body)
    return Response(content=json.dumps(result), media_type="application/json")

# For clients that post to root
@app.post("/")
async def mcp_root(request: Request) -> Response:
    return await mcp_handler(request)

if __name__ == "__main__":
    import uvicorn
    if not FETCHSERP_API_TOKEN:
        print("Warning: set FETCHSERP_API_TOKEN or search and fetch will fail at runtime")
    print(f"Starting {APP_NAME} on 0.0.0.0:{os.getenv('PORT', '8000')}")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
