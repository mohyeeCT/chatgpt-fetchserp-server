#!/usr/bin/env python3
"""
FastAPI MCP server for fetchSERP
- Serves JSON-RPC MCP at "/" and "/mcp/"
- Uses MCP protocol revision 2025-06-18
- Exposes two tools backed by fetchSERP:
    1) serp: call /api/v1/serp
    2) ranking: call /api/v1/ranking
"""

import os
import json
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

APP_NAME = "FetchSERP MCP Server"
APP_VERSION = "1.0.1"
MCP_PROTOCOL_REV = "2025-06-18"

# Environment
FETCHSERP_API_TOKEN = os.getenv("FETCHSERP_API_TOKEN")
FETCHSERP_BASE_URL = os.getenv("FETCHSERP_BASE_URL", "https://www.fetchserp.com")
PORT = int(os.getenv("PORT", "8000"))

app = FastAPI(title=APP_NAME)

# CORS: keep wide open while testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health endpoints
@app.get("/")
async def health_root():
    return {
        "ok": True,
        "app": APP_NAME,
        "version": APP_VERSION,
        "mcp": {"protocolRevision": MCP_PROTOCOL_REV, "endpoints": ["/", "/mcp/"]},
    }

@app.get("/health")
async def health():
    return {"ok": True}

# HTTP client helper
def _client() -> httpx.AsyncClient:
    headers = {"Authorization": f"Bearer {FETCHSERP_API_TOKEN}"}
    return httpx.AsyncClient(base_url=FETCHSERP_BASE_URL, headers=headers, timeout=60.0)

# JSON-RPC helpers
def _jsonrpc_result(id_value: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id_value, "result": result}

def _jsonrpc_error(id_value: Any, code: int, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    err: Dict[str, Any] = {"jsonrpc": "2.0", "id": id_value, "error": {"code": code, "message": message}}
    if data is not None:
        err["error"]["data"] = data
    return err

# Tool definitions for tools/list
def _tools_list_result() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "serp",
                "description": "Get structured SERP results from Google, Bing, Yahoo, or DuckDuckGo.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query. Example: 'best seo tools'"},
                        "search_engine": {
                            "type": "string",
                            "enum": ["google", "bing", "yahoo", "duckduckgo"],
                            "default": "google",
                        },
                        "country": {"type": "string", "description": "Two letter country code, default us", "default": "us"},
                        "pages_number": {"type": "integer", "minimum": 1, "maximum": 5, "default": 1},
                    },
                    "required": ["query"],
                    "additionalProperties": True,
                },
            },
            {
                "name": "ranking",
                "description": "Check domain ranking for a keyword.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Domain name without protocol"},
                        "keyword": {"type": "string", "description": "Target keyword"},
                        "country": {"type": "string", "description": "Two letter country code", "default": "us"},
                        "search_engine": {
                            "type": "string",
                            "enum": ["google", "bing", "yahoo", "duckduckgo"],
                            "default": "google",
                        },
                    },
                    "required": ["domain", "keyword"],
                    "additionalProperties": True,
                },
            },
        ]
    }

async def _handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if not FETCHSERP_API_TOKEN:
        raise RuntimeError("FETCHSERP_API_TOKEN is not set")

    # Map tool to REST endpoint and HTTP method
    if name == "serp":
        endpoint = "/api/v1/serp"
        params = {
            "query": arguments.get("query", ""),
            "search_engine": arguments.get("search_engine", "google"),
            "country": arguments.get("country", "us"),
            "pages_number": arguments.get("pages_number", 1),
        }
        # pass through any extra params
        for k, v in arguments.items():
            if k not in params:
                params[k] = v
        async with _client() as client:
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()

    elif name == "ranking":
        endpoint = "/api/v1/ranking"
        params = {
            "domain": arguments.get("domain", ""),
            "keyword": arguments.get("keyword", ""),
            "country": arguments.get("country", "us"),
            "search_engine": arguments.get("search_engine", "google"),
        }
        for k, v in arguments.items():
            if k not in params:
                params[k] = v
        async with _client() as client:
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()
    else:
        return {
            "content": [
                {"type": "text", "text": json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)}
            ]
        }

    # MCP tool result uses content list
    return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}

async def _mcp_dispatch(request_body: Dict[str, Any]) -> Dict[str, Any]:
    method = request_body.get("method")
    rid = request_body.get("id")
    params = request_body.get("params") or {}

    # Initialize
    if method == "initialize":
        result = {
            "protocolVersion": MCP_PROTOCOL_REV,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": APP_NAME, "version": APP_VERSION},
        }
        return _jsonrpc_result(rid, result)

    # tools/list
    if method in ("tools/list", "tools.list"):
        return _jsonrpc_result(rid, _tools_list_result())

    # tools/call
    if method in ("tools/call", "tools.call"):
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            result = await _handle_tool_call(name, arguments)
            return _jsonrpc_result(rid, result)
        except httpx.HTTPStatusError as e:
            data = {"status": e.response.status_code, "body": e.response.text}
            return _jsonrpc_error(rid, -32001, f"Upstream FetchSERP error", data)
        except Exception as e:
            return _jsonrpc_error(rid, -32000, f"Server error: {str(e)}")

    # Unknown method
    return _jsonrpc_error(rid, -32601, f"Method not found: {method}")

# MCP JSON-RPC handlers at both "/" and "/mcp/"
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
    result = await _mcp_dispatch(body)
    headers = {"MCP-Protocol-Version": MCP_PROTOCOL_REV}
    return Response(content=json.dumps(result), media_type="application/json", headers=headers)

@app.post("/")
async def mcp_handler_root(request: Request) -> Response:
    return await mcp_handler(request)

if __name__ == "__main__":
    if not FETCHSERP_API_TOKEN:
        print("Error: set FETCHSERP_API_TOKEN")
        raise SystemExit(1)
    import uvicorn
    print(f"Starting {APP_NAME} on 0.0.0.0:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
