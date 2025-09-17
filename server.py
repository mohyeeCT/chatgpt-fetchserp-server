#!/usr/bin/env python3
"""
MCP Protocol Server for ChatGPT Deep Research
Implements proper MCP JSON-RPC protocol
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uvicorn
from typing import List, Dict, Any, Union
from pydantic import BaseModel
import json

# Environment configuration
FETCHSERP_API_TOKEN = os.getenv("FETCHSERP_API_TOKEN")
PORT = int(os.getenv("PORT", 8000))

if not FETCHSERP_API_TOKEN:
    print("❌ Error: FETCHSERP_API_TOKEN environment variable is required")
    exit(1)

FETCHSERP_BASE_URL = "https://api.fetchserp.com/api/v1"

# Create FastAPI app
app = FastAPI(title="ChatGPT FetchSERP MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP Protocol Models
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    result: Dict[str, Any] = {}
    error: Dict[str, Any] = None

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
    return {"status": "ChatGPT FetchSERP MCP Server", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "ChatGPT FetchSERP MCP Server",
        "api_connected": bool(FETCHSERP_API_TOKEN)
    }

@app.get("/mcp/")
async def mcp_info():
    """GET endpoint for server info"""
    return {
        "jsonrpc": "2.0",
        "result": {
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "ChatGPT FetchSERP Server",
                "version": "1.0.0"
            }
        }
    }

@app.post("/mcp/")
async def mcp_handler(request: Request):
    """Main MCP protocol handler"""
    try:
        body = await request.json()
        method = body.get("method", "")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "ChatGPT FetchSERP Server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "notifications/initialized":
            # Just acknowledge
            return {"jsonrpc": "2.0"}
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "search",
                            "description": "Search for SEO insights and web intelligence data. Returns analysis IDs that can be fetched for detailed results.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query for SEO analysis capabilities"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "fetch",
                            "description": "Retrieve detailed SEO analysis and web intelligence data by ID.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "Analysis ID to fetch detailed information for"
                                    }
                                },
                                "required": ["id"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            
            if tool_name == "search":
                query = tool_args.get("query", "").lower()
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
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Found SEO analysis capabilities. Available analysis IDs: {', '.join(analysis_ids)}. Use the fetch tool with any of these IDs to get detailed information."
                            }
                        ]
                    }
                }
            
            elif tool_name == "fetch":
                fetch_id = tool_args.get("id", "")
                
                analysis_data = {
                    "seo_analysis": {
                        "id": "seo_analysis",
                        "type": "SEO Analysis & Website Audit",
                        "description": "Comprehensive technical SEO analysis and optimization recommendations using FetchSERP API",
                        "capabilities": [
                            "Technical SEO audit (meta tags, headers, structure)",
                            "On-page optimization analysis", 
                            "Core Web Vitals and page speed assessment",
                            "Mobile-friendliness evaluation",
                            "Schema markup validation",
                            "Internal linking structure analysis",
                            "Content optimization recommendations"
                        ],
                        "api_endpoints": [
                            "web_page_seo_analysis - Complete SEO audit",
                            "web_page_ai_analysis - AI-powered content analysis"
                        ],
                        "real_time_data": True,
                        "example_usage": "Get comprehensive SEO analysis for any website to identify optimization opportunities"
                    },
                    "keyword_research": {
                        "id": "keyword_research",
                        "type": "Keyword Research & Search Intelligence",
                        "description": "Advanced keyword research with search volume and competition data from FetchSERP",
                        "capabilities": [
                            "Monthly search volume for any keyword",
                            "Keyword difficulty and competition metrics",
                            "Long-tail keyword generation and discovery",
                            "Related keyword suggestions and variations",
                            "Search trends and seasonal patterns",
                            "Keyword opportunity identification"
                        ],
                        "api_endpoints": [
                            "keywords_search_volume - Get monthly search volumes",
                            "keywords_suggestions - Find related keywords", 
                            "long_tail_keywords_generator - Generate long-tail variations"
                        ],
                        "real_time_data": True,
                        "example_usage": "Research high-value keywords for content strategy and SEO optimization"
                    },
                    "domain_analysis": {
                        "id": "domain_analysis",
                        "type": "Domain Intelligence & Backlink Analysis", 
                        "description": "Complete domain profiling with backlink and authority analysis via FetchSERP",
                        "capabilities": [
                            "Comprehensive backlink discovery and analysis",
                            "Domain authority and trust metrics (Moz integration)",
                            "DNS, WHOIS, and technical domain information",
                            "Technology stack detection and analysis",
                            "SSL certificate and security assessment",
                            "Email discovery and contact information"
                        ],
                        "api_endpoints": [
                            "backlinks - Discover and analyze backlinks",
                            "moz - Get domain authority metrics",
                            "domain_infos - Technical domain intelligence",
                            "domain_emails - Extract contact information"
                        ],
                        "real_time_data": True,
                        "example_usage": "Analyze competitor domains and backlink strategies for competitive intelligence"
                    },
                    "serp_analysis": {
                        "id": "serp_analysis",
                        "type": "SERP Intelligence & Ranking Analysis",
                        "description": "Search engine results analysis and ranking intelligence from FetchSERP",
                        "capabilities": [
                            "Multi-engine SERP results (Google, Bing, Yahoo, DuckDuckGo)",
                            "AI Overview and featured snippets analysis",
                            "Domain ranking tracking for specific keywords",
                            "Page indexation status verification",
                            "SERP feature analysis (videos, images, local results)",
                            "Competitive ranking intelligence"
                        ],
                        "api_endpoints": [
                            "serp - Get structured SERP results",
                            "serp_ai - AI Overview and enhanced results",
                            "ranking - Domain ranking for keywords",
                            "page_indexation - Check indexation status"
                        ],
                        "real_time_data": True,
                        "example_usage": "Track keyword rankings and analyze search engine results for SEO strategy"
                    },
                    "web_scraping": {
                        "id": "web_scraping",
                        "type": "Web Scraping & Data Extraction",
                        "description": "Advanced web scraping and structured data extraction using FetchSERP",
                        "capabilities": [
                            "Full webpage content extraction and parsing",
                            "JavaScript-rendered content scraping",
                            "Custom JavaScript execution on target pages",
                            "Proxy-based scraping for geo-targeted data",
                            "Bulk domain crawling and site mapping",
                            "Structured data extraction and formatting"
                        ],
                        "api_endpoints": [
                            "scrape - Basic webpage content extraction",
                            "scrape_js - JavaScript-rendered content scraping",
                            "scrape_js_with_proxy - Geo-targeted proxy scraping",
                            "domain_scraping - Bulk site crawling"
                        ],
                        "real_time_data": True,
                        "example_usage": "Extract data from websites for competitive analysis and market research"
                    },
                    "competitor_analysis": {
                        "id": "competitor_analysis",
                        "type": "Competitive Intelligence & Market Analysis",
                        "description": "Comprehensive competitor research combining multiple FetchSERP APIs",
                        "capabilities": [
                            "Competitor backlink profile analysis",
                            "Competitive keyword research and gap analysis",
                            "Market share and ranking comparisons",
                            "Technology stack competitive analysis",
                            "Content strategy and SEO comparison",
                            "Market opportunity identification"
                        ],
                        "combination_analysis": "Uses multiple FetchSERP APIs for comprehensive insights",
                        "real_time_data": True,
                        "example_usage": "Compare your SEO strategy against top competitors for strategic advantage"
                    },
                    "general_seo": {
                        "id": "general_seo",
                        "type": "Complete SEO & Web Intelligence Toolkit",
                        "description": "Full-featured SEO analysis and web intelligence platform powered by FetchSERP",
                        "available_capabilities": [
                            "Website SEO Analysis & Auditing",
                            "Keyword Research & Intelligence", 
                            "Domain Analysis & Backlink Research",
                            "SERP Analysis & Ranking Tracking",
                            "Web Scraping & Data Extraction",
                            "Competitive Intelligence & Market Analysis"
                        ],
                        "powered_by": "FetchSERP All-in-One SEO API with 25+ tools",
                        "getting_started": "Ask specific questions about websites, keywords, domains, or competitors",
                        "example_queries": [
                            "Analyze the SEO performance of my website",
                            "Find high-value keywords for my business niche",
                            "Research my competitor's backlink strategy", 
                            "Check how I rank for important keywords",
                            "Extract data from competitor websites",
                            "Compare my domain authority to competitors"
                        ],
                        "comprehensive_analysis": True,
                        "real_time_data": True
                    }
                }
                
                data = analysis_data.get(fetch_id)
                if not data:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Unknown analysis ID: {fetch_id}. Available IDs: {', '.join(analysis_data.keys())}"
                                }
                            ]
                        }
                    }
                
                # Format the response nicely
                formatted_response = f"""# {data['type']}

**Description:** {data['description']}

**Capabilities:**
"""
                for capability in data.get('capabilities', []):
                    formatted_response += f"• {capability}\n"
                
                if 'api_endpoints' in data:
                    formatted_response += f"\n**Available API Endpoints:**\n"
                    for endpoint in data['api_endpoints']:
                        formatted_response += f"• {endpoint}\n"
                
                formatted_response += f"\n**Real-time Data:** {'Yes' if data.get('real_time_data', False) else 'No'}"
                
                if 'example_usage' in data:
                    formatted_response += f"\n\n**Example Usage:** {data['example_usage']}"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": formatted_response
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

if __name__ == "__main__":
    print("🚀 Starting ChatGPT-Compatible FetchSERP MCP Server...")
    print(f"📍 Server URL: http://0.0.0.0:{PORT}/")
    print("🔗 For ChatGPT: Use /mcp/ endpoint")
    print("📊 Powered by FetchSERP API")
    print("✅ MCP JSON-RPC Protocol Compatible")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
