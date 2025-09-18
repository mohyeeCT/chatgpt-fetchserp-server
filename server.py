#!/usr/bin/env python3
"""
FetchSERP MCP server exposing core endpoints as MCP tools.
- JSON-RPC at "/" and "/mcp/"
- Includes search/fetch pair and all core endpoints
- Adds aliases: keyword_volume -> keywords_search_volume, keyword_suggestions -> keywords_suggestions
"""
import os
import json
import time
import hashlib
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

APP_NAME = "FetchSERP MCP Server"
APP_VERSION = "1.2.1"
MCP_PROTOCOL_REV = "2025-06-18"

FETCHSERP_API_TOKEN = os.getenv("FETCHSERP_API_TOKEN")
FETCHSERP_BASE_URL = os.getenv("FETCHSERP_BASE_URL", "https://www.fetchserp.com")
PORT = int(os.getenv("PORT", "8000"))

SEARCH_TTL_SEC = 20 * 60
SEARCH_INDEX: Dict[str, Dict[str, Any]] = {}

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def _client() -> httpx.AsyncClient:
    headers = {"Authorization": f"Bearer {FETCHSERP_API_TOKEN}"}
    return httpx.AsyncClient(base_url=FETCHSERP_BASE_URL, headers=headers, timeout=90.0)

def _jsonrpc_result(id_value: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id_value, "result": result}

def _jsonrpc_error(id_value: Any, code: int, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    err: Dict[str, Any] = {"jsonrpc": "2.0", "id": id_value, "error": {"code": code, "message": message}}
    if data is not None:
        err["error"]["data"] = data
    return err

# Map MCP tool name -> FetchSERP endpoint path and HTTP method
ENDPOINTS = {
    # meta-tools
    "search": {"path": "/api/v1/serp", "method": "GET"},
    "fetch": {"path": "/api/v1/scrape", "method": "GET"},

    # core endpoints (based on public SDK/docs)
    "serp": {"path": "/api/v1/serp", "method": "GET"},
    "ranking": {"path": "/api/v1/ranking", "method": "GET"},
    "serp_html": {"path": "/api/v1/serp_html", "method": "GET"},
    "serp_text": {"path": "/api/v1/serp_text", "method": "GET"},
    "serp_js": {"path": "/api/v1/serp_js", "method": "GET"},  # returns UUID in some flows
    "serp_ai": {"path": "/api/v1/serp_ai", "method": "GET"},
    "serp_ai_mode": {"path": "/api/v1/serp_ai_mode", "method": "GET"},
    "page_indexation": {"path": "/api/v1/page_indexation", "method": "GET"},
    "backlinks": {"path": "/api/v1/backlinks", "method": "GET"},
    "keywords_search_volume": {"path": "/api/v1/keywords_search_volume", "method": "GET"},
    "keywords_suggestions": {"path": "/api/v1/keywords_suggestions", "method": "GET"},
    "long_tail_keywords_generator": {"path": "/api/v1/long_tail_keywords_generator", "method": "GET"},
    "scrape": {"path": "/api/v1/scrape", "method": "GET"},
    "scrape_js": {"path": "/api/v1/scrape_js", "method": "POST"},  # POST per SDK
    "scrape_js_with_proxy": {"path": "/api/v1/scrape_js_with_proxy", "method": "POST"},  # POST per SDK
    "domain_scraping": {"path": "/api/v1/scrape_domain", "method": "GET"},  # path per SDK
    "web_page_seo_analysis": {"path": "/api/v1/web_page_seo_analysis", "method": "GET"},
    "web_page_ai_analysis": {"path": "/api/v1/web_page_ai_analysis", "method": "GET"},
    "domain_infos": {"path": "/api/v1/domain_infos", "method": "GET"},
    "domain_emails": {"path": "/api/v1/domain_emails", "method": "GET"},
    "moz": {"path": "/api/v1/moz", "method": "GET"},

    # aliases
    "keyword_volume": {"path": "/api/v1/keywords_search_volume", "method": "GET"},
    "keyword_suggestions": {"path": "/api/v1/keywords_suggestions", "method": "GET"},
}

def _stable_id(url: str, position: int, query: str) -> str:
    h = hashlib.sha1(f"{url}|{position}|{query}".encode("utf-8")).hexdigest()
    return f"fsrp_{h[:24]}"

def _purge_expired():
    now = time.time()
    expired = [k for k, v in SEARCH_INDEX.items() if now - v.get("ts", 0) > SEARCH_TTL_SEC]
    for k in expired:
        SEARCH_INDEX.pop(k, None)

def _tools_list_result() -> Dict[str, Any]:
    def obj(props, required=None, additional=True):
        return {"type": "object", "properties": props, "required": required or [], "additionalProperties": additional}

    common_search_props = {
        "query": {"type": "string"},
        "search_engine": {"type": "string", "enum": ["google", "bing", "yahoo", "duckduckgo"], "default": "google"},
        "country": {"type": "string", "default": "us"},
        "pages_number": {"type": "integer", "minimum": 1, "maximum": 30, "default": 1},
    }

    tools = []

    # search + fetch
    tools.append({
        "name": "search",
        "description": "Search and return top result IDs. Wraps /api/v1/serp.",
        "inputSchema": obj({**common_search_props, "top_k": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10}}, ["query"]),
    })
    tools.append({
        "name": "fetch",
        "description": "Fetch full documents by IDs returned from search. Uses /api/v1/scrape.",
        "inputSchema": obj({"ids": {"type": "array", "items": {"type": "string"}}}, ["ids"], additional=False),
    })

    # core endpoints
    tools += [
        {"name": "serp", "description": "Structured SERP results.", "inputSchema": obj(common_search_props, ["query"])},
        {"name": "ranking", "description": "Domain ranking for a keyword.", "inputSchema": obj({
            "domain": {"type": "string"},
            "keyword": {"type": "string"},
            "country": {"type": "string", "default": "us"},
            "search_engine": {"type": "string", "enum": ["google", "bing", "yahoo", "duckduckgo"], "default": "google"},
            "pages_number": {"type": "integer", "minimum": 1, "maximum": 30, "default": 10},
        }, ["domain", "keyword"])},
        {"name": "serp_html", "description": "SERP with full HTML.", "inputSchema": obj(common_search_props, ["query"])},
        {"name": "serp_text", "description": "SERP as extracted text.", "inputSchema": obj(common_search_props, ["query"])},
        {"name": "serp_js", "description": "JS-rendered SERP job.", "inputSchema": obj(common_search_props, ["query"])},
        {"name": "serp_ai", "description": "AI Overview + AI Mode.", "inputSchema": obj(common_search_props, ["query"])},
        {"name": "serp_ai_mode", "description": "Cached US-only AI Mode.", "inputSchema": obj({"query": {"type": "string"}}, ["query"])},
        {"name": "page_indexation", "description": "Check page indexation status.", "inputSchema": obj({"url": {"type": "string"}}, ["url"])},
        {"name": "backlinks", "description": "Backlink data for a domain.", "inputSchema": obj({"domain": {"type": "string"}}, ["domain"])},
        {"name": "keywords_search_volume", "description": "Monthly search volume for a keyword.", "inputSchema": obj({"keyword": {"type": "string"}}, ["keyword"])},
        {"name": "keywords_suggestions", "description": "Keyword suggestions with metrics.", "inputSchema": obj({"keyword": {"type": "string"}}, ["keyword"])},
        {"name": "long_tail_keywords_generator", "description": "Generate long-tail keywords.", "inputSchema": obj({"keyword": {"type": "string"}}, ["keyword"])},
        {"name": "scrape", "description": "Scrape raw HTML.", "inputSchema": obj({"url": {"type": "string"}}, ["url"])},
        {"name": "scrape_js", "description": "Scrape with custom JS.", "inputSchema": obj({"url": {"type": "string"}, "script": {"type": "string"}}, ["url"])},
        {"name": "scrape_js_with_proxy", "description": "JS scrape via proxy.", "inputSchema": obj({"url": {"type": "string"}, "script": {"type": "string"}}, ["url"])},
        {"name": "domain_scraping", "description": "Crawl a domain.", "inputSchema": obj({"domain": {"type": "string"}}, ["domain"])},
        {"name": "web_page_seo_analysis", "description": "Technical and on-page SEO audit.", "inputSchema": obj({"url": {"type": "string"}}, ["url"])},
        {"name": "web_page_ai_analysis", "description": "AI-powered content analysis.", "inputSchema": obj({"url": {"type": "string"}}, ["url"])},
        {"name": "domain_infos", "description": "DNS, WHOIS, tech stack.", "inputSchema": obj({"domain": {"type": "string"}}, ["domain"])},
        {"name": "domain_emails", "description": "Extract emails from a domain.", "inputSchema": obj({"domain": {"type": "string"}}, ["domain"])},
        {"name": "moz", "description": "Moz authority and metrics.", "inputSchema": obj({"domain": {"type": "string"}}, ["domain"])},
        {"name": "keyword_volume", "description": "Alias of keywords_search_volume.", "inputSchema": obj({"keyword": {"type": "string"}}, ["keyword"])},
        {"name": "keyword_suggestions", "description": "Alias of keywords_suggestions.", "inputSchema": obj({"keyword": {"type": "string"}}, ["keyword"])},
    ]

    return {"tools": tools}

async def _call_fetchserp(endpoint: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    async with _client() as client:
        if method == "GET":
            r = await client.get(endpoint, params=params)
        else:
            r = await client.post(endpoint, json=params)
        r.raise_for_status()
        return r.json()

async def _handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if not FETCHSERP_API_TOKEN:
        raise RuntimeError("FETCHSERP_API_TOKEN is not set")

    if name == "search":
        query = arguments.get("query", "")
        params = {
            "query": query,
            "search_engine": arguments.get("search_engine", "google"),
            "country": arguments.get("country", "us"),
            "pages_number": int(arguments.get("pages_number", 1)),
        }
        top_k = int(arguments.get("top_k", 10))
        data = await _call_fetchserp("/api/v1/serp", "GET", params)
        results = data.get("results", [])[:top_k]
        now = time.time()
        items = []
        for r in results:
            url = r.get("url") or ""
            pos = int(r.get("position") or 0)
            _id = _stable_id(url, pos, query)
            SEARCH_INDEX[_id] = {
                "url": url,
                "title": r.get("title"),
                "snippet": r.get("snippet"),
                "position": pos,
                "query": query,
                "ts": now,
            }
            items.append({"id": _id, "title": r.get("title"), "url": url, "snippet": r.get("snippet"), "position": pos})
        _purge_expired()
        return {"content": [{"type": "text", "text": json.dumps({"items": items}, ensure_ascii=False)}]}

    if name == "fetch":
        ids: List[str] = list(arguments.get("ids") or [])
        docs, missing = [], []
        for _id in ids:
            meta = SEARCH_INDEX.get(_id)
            if not meta:
                missing.append(_id)
                continue
            try:
                res = await _call_fetchserp("/api/v1/scrape", "GET", {"url": meta["url"]})
                html = res.get("html", "")
            except httpx.HTTPStatusError:
                html = ""
            docs.append({"id": _id, "url": meta["url"], "title": meta.get("title"), "snippet": meta.get("snippet"), "html": html})
        _purge_expired()
        return {"content": [{"type": "text", "text": json.dumps({"docs": docs, "missing": missing}, ensure_ascii=False)}]}

    if name in ENDPOINTS:
        ep = ENDPOINTS[name]
        params = {k: v for k, v in arguments.items()}
        data = await _call_fetchserp(ep["path"], ep["method"], params)
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}

    return {"content": [{"type": "text", "text": json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)}]}

async def _mcp_dispatch(request_body: Dict[str, Any]) -> Dict[str, Any]:
    method = request_body.get("method")
    rid = request_body.get("id")
    params = request_body.get("params") or {}

    if method == "initialize":
        result = {
            "protocolVersion": MCP_PROTOCOL_REV,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": APP_NAME, "version": APP_VERSION},
        }
        return _jsonrpc_result(rid, result)

    if method in ("tools/list", "tools.list"):
        return _jsonrpc_result(rid, _tools_list_result())

    if method in ("tools/call", "tools.call"):
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            result = await _handle_tool_call(name, arguments)
            return _jsonrpc_result(rid, result)
        except httpx.HTTPStatusError as e:
            data = {"status": e.response.status_code, "body": e.response.text}
            return _jsonrpc_error(rid, -32001, "Upstream FetchSERP error", data)
        except Exception as e:
            return _jsonrpc_error(rid, -32000, f"Server error: {str(e)}")

    return _jsonrpc_error(rid, -32601, f"Method not found: {method}")

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
