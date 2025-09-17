#!/usr/bin/env python3
"""
Simple HTTP Server for ChatGPT Deep Research
Compatible with ChatGPT's MCP requirements
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uvicorn
from typing import List, Dict, Any
from pydantic import BaseModel

# Environment configuration
FETCHSERP_API_TOKEN = os.getenv("FETCHSERP_API_TOKEN")
PORT = int(os.getenv("PORT", 8000))

if not FETCHSERP_API_TOKEN:
    print("❌ Error: FETCHSERP_API_TOKEN environment variable is required")
    exit(1)

FETCHSERP_BASE_URL = "https://api.fetchserp.com/api/v1"

# Create FastAPI app
app = FastAPI(title="ChatGPT FetchSERP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SearchRequest(BaseModel):
    query: str

class FetchRequest(BaseModel):
    id: str

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

# Helper function for FetchSERP API calls
async def call_fetchserp(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make authenticated API call to FetchSERP"""
    url = f"{FETCHSERP_BASE_URL}/{endpoint}"
    headers = {"Authorization": f"Bearer {FETCHSERP_API_TOKEN}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"API call failed: {str(e)}"}

@app.get("/")
async def root():
    return {"status": "ChatGPT FetchSERP Server", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "ChatGPT FetchSERP Server",
        "api_connected": bool(FETCHSERP_API_TOKEN)
    }

@app.get("/mcp/")
async def mcp_info():
    return {
        "jsonrpc": "2.0",
        "result": {
            "capabilities": {
                "tools": {
                    "search": {
                        "description": "Search for SEO insights and web intelligence data"
                    },
                    "fetch": {
                        "description": "Retrieve detailed SEO analysis by ID"
                    }
                }
            },
            "serverInfo": {
                "name": "ChatGPT FetchSERP Server",
                "version": "1.0.0"
            }
        }
    }

@app.post("/mcp/tools/search")
async def search_tool(request: SearchRequest):
    """Search for SEO insights and web intelligence data"""
    query = request.query.lower()
    analysis_ids = []
    
    # Parse query and return relevant analysis types
    if any(word in query for word in ['seo', 'audit', 'analyze', 'website', 'technical']):
        analysis_ids.append("seo_analysis")
        
    if any(word in query for word in ['keyword', 'search volume', 'suggestions', 'long tail']):
        analysis_ids.append("keyword_research")
        
    if any(word in query for word in ['domain', 'backlink', 'authority', 'moz', 'links']):
        analysis_ids.append("domain_analysis")
        
    if any(word in query for word in ['serp', 'ranking', 'google', 'search results', 'position']):
        analysis_ids.append("serp_analysis")
        
    if any(word in query for word in ['scrape', 'extract', 'content', 'data']):
        analysis_ids.append("web_scraping")
        
    if any(word in query for word in ['competitor', 'competition', 'rival', 'compare']):
        analysis_ids.append("competitor_analysis")
    
    # Default to general SEO if no specific category
    if not analysis_ids:
        analysis_ids = ["general_seo", "seo_analysis"]
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(analysis_ids)} SEO analysis types: {', '.join(analysis_ids)}"
                }
            ],
            "isError": False
        }
    }

@app.post("/mcp/tools/fetch")
async def fetch_tool(request: FetchRequest):
    """Retrieve detailed SEO analysis data by ID"""
    
    analysis_data = {
        "seo_analysis": {
            "type": "SEO Analysis & Website Audit",
            "description": "Comprehensive technical SEO analysis and optimization recommendations",
            "capabilities": [
                "Technical SEO audit (meta tags, headers, structure)",
                "On-page optimization analysis", 
                "Core Web Vitals and page speed assessment",
                "Mobile-friendliness evaluation",
                "Schema markup validation",
                "Internal linking structure analysis"
            ],
            "data_source": "FetchSERP Web Page SEO Analysis API",
            "real_time": True,
            "example_usage": "Analyze example.com for SEO issues and optimization opportunities"
        },
        "keyword_research": {
            "type": "Keyword Research & Search Intelligence",
            "description": "Advanced keyword research with search volume and competition data",
            "capabilities": [
                "Monthly search volume for any keyword",
                "Keyword difficulty and competition metrics",
                "Long-tail keyword generation and discovery",
                "Related keyword suggestions and variations",
                "Search trends and seasonal patterns"
            ],
            "data_source": "FetchSERP Keywords API with global search data",
            "real_time": True,
            "example_usage": "Research high-value keywords for 'digital marketing' niche"
        },
        "domain_analysis": {
            "type": "Domain Intelligence & Backlink Analysis", 
            "description": "Complete domain profiling with backlink and authority analysis",
            "capabilities": [
                "Comprehensive backlink discovery and analysis",
                "Domain authority and trust metrics (Moz integration)",
                "DNS, WHOIS, and technical domain information",
                "Technology stack detection and analysis",
                "SSL certificate and security assessment"
            ],
            "data_source": "FetchSERP Domain APIs with Moz integration",
            "real_time": True,
            "example_usage": "Analyze competitor.com backlink profile and domain strength"
        },
        "serp_analysis": {
            "type": "SERP Intelligence & Ranking Analysis",
            "description": "Search engine results analysis and ranking intelligence",
            "capabilities": [
                "Multi-engine SERP results (Google, Bing, Yahoo, DuckDuckGo)",
                "AI Overview and featured snippets analysis",
                "Domain ranking tracking for specific keywords",
                "Page indexation status verification",
                "SERP feature analysis (videos, images, local results)"
            ],
            "data_source": "FetchSERP SERP APIs with AI Overview support",
            "real_time": True,
            "example_usage": "Check how example.com ranks for 'best CRM software'"
        },
        "web_scraping": {
            "type": "Web Scraping & Data Extraction",
            "description": "Advanced web scraping and structured data extraction",
            "capabilities": [
                "Full webpage content extraction and parsing",
                "JavaScript-rendered content scraping",
                "Custom JavaScript execution on target pages",
                "Proxy-based scraping for geo-targeted data",
                "Bulk domain crawling and site mapping"
            ],
            "data_source": "FetchSERP Scraping APIs with proxy support",
            "real_time": True,
            "example_usage": "Extract product data and pricing from e-commerce websites"
        },
        "competitor_analysis": {
            "type": "Competitive Intelligence & Market Analysis",
            "description": "Comprehensive competitor research and market intelligence", 
            "capabilities": [
                "Competitor backlink profile analysis",
                "Competitive keyword research and gaps",
                "Market share and ranking comparisons",
                "Technology stack competitive analysis",
                "Content strategy and SEO comparison"
            ],
            "data_source": "Combined FetchSERP APIs for competitive intelligence",
            "real_time": True,
            "example_usage": "Compare SEO strategies of top competitors"
        },
        "general_seo": {
            "type": "Complete SEO & Web Intelligence Toolkit",
            "description": "Full-featured SEO analysis and web intelligence platform",
            "available_capabilities": [
                "Website SEO Analysis & Auditing",
                "Keyword Research & Intelligence", 
                "Domain Analysis & Backlink Research",
                "SERP Analysis & Ranking Tracking",
                "Web Scraping & Data Extraction",
                "Competitive Intelligence & Market Analysis"
            ],
            "powered_by": "FetchSERP All-in-One SEO API",
            "getting_started": "Ask specific questions about websites, keywords, domains, or competitors",
            "example_queries": [
                "Analyze the SEO performance of my website",
                "Find high-value keywords for my business niche",
                "Research my competitor's backlink strategy", 
                "Check how I rank for important keywords"
            ]
        }
    }
    
    data = analysis_data.get(request.id, {
        "error": f"Unknown analysis ID: {request.id}",
        "available_ids": list(analysis_data.keys())
    })
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "content": [
                {
                    "type": "text", 
                    "text": f"Analysis ID: {request.id}\n\nData: {data}"
                }
            ],
            "isError": False
        }
    }

@app.post("/mcp/call_tool")
async def call_tool(tool_call: ToolCall):
    """Generic tool calling endpoint"""
    
    if tool_call.name == "search":
        query = tool_call.arguments.get("query", "")
        request = SearchRequest(query=query)
        return await search_tool(request)
    
    elif tool_call.name == "fetch":
        id_value = tool_call.arguments.get("id", "")
        request = FetchRequest(id=id_value)
        return await fetch_tool(request)
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_call.name}")

if __name__ == "__main__":
    print("🚀 Starting ChatGPT-Compatible FetchSERP Server...")
    print(f"📍 Server URL: http://0.0.0.0:{PORT}/")
    print("🔗 For ChatGPT: Use /mcp/ endpoints")
    print("📊 Powered by FetchSERP API")
    print("✅ HTTP JSON Transport (ChatGPT Compatible)")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
