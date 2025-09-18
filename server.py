#!/usr/bin/env python3
"""
OpenAI-Compatible FastAPI MCP Server for FetchSERP
Implements exact OpenAI MCP specifications for ChatGPT Deep Research
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uvicorn
import json
from typing import List, Dict, Any, Union
from pydantic import BaseModel

# Environment configuration
FETCHSERP_API_TOKEN = os.getenv("FETCHSERP_API_TOKEN")
PORT = int(os.getenv("PORT", 8000))

if not FETCHSERP_API_TOKEN:
    print("❌ Error: FETCHSERP_API_TOKEN environment variable is required")
    exit(1)

FETCHSERP_BASE_URL = "https://api.fetchserp.com/api/v1"

# Create FastAPI app
app = FastAPI(title="FetchSERP MCP Server", version="1.0.0")

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
    return {"status": "FetchSERP MCP Server", "version": "1.0.0", "protocol": "OpenAI-Compatible"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "FetchSERP MCP Server",
        "api_connected": bool(FETCHSERP_API_TOKEN),
        "mcp_protocol": "OpenAI-Compatible"
    }

@app.get("/mcp/")
async def mcp_info():
    """GET endpoint for server info"""
    return {
        "jsonrpc": "2.0",
        "result": {
            "capabilities": {
                "tools": {
                    "search": {
                        "description": "Search for SEO insights and web intelligence data from FetchSERP"
                    },
                    "fetch": {
                        "description": "Retrieve detailed SEO analysis and intelligence by ID"
                    }
                }
            },
            "serverInfo": {
                "name": "FetchSERP MCP Server",
                "version": "1.0.0"
            }
        }
    }

@app.post("/mcp/")
async def mcp_handler(request: Request):
    """Main MCP protocol handler following OpenAI specifications"""
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
                        "name": "FetchSERP MCP Server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "notifications/initialized":
            return {"jsonrpc": "2.0"}
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0", 
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "search",
                            "description": "Search for SEO insights and web intelligence data from FetchSERP. Returns analysis IDs that can be fetched for detailed results covering website audits, keyword research, domain analysis, SERP intelligence, web scraping, and competitive analysis.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query for SEO analysis capabilities (e.g., 'SEO analysis', 'keyword research', 'domain analysis', 'competitor analysis')"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "fetch",
                            "description": "Retrieve detailed SEO analysis and web intelligence data by ID. Provides comprehensive information about specific FetchSERP capabilities including technical details, API endpoints, and usage examples.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "Analysis ID to fetch detailed information for (e.g., 'seo_analysis', 'keyword_research', 'domain_analysis')"
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
                
                # Build results array following OpenAI format
                results = []
                
                # SEO Analysis
                if any(word in query for word in ['seo', 'audit', 'analyze', 'website', 'technical', 'optimization']):
                    results.append({
                        "id": "seo_analysis", 
                        "title": "SEO Analysis & Website Audit",
                        "url": "https://docs.fetchserp.com/api-reference/seo-analysis/web-page-seo-analysis"
                    })
                    
                # Keyword Research  
                if any(word in query for word in ['keyword', 'search volume', 'suggestions', 'long tail', 'research']):
                    results.append({
                        "id": "keyword_research",
                        "title": "Keyword Research & Search Intelligence", 
                        "url": "https://docs.fetchserp.com/api-reference/keywords/keywords-search-volume"
                    })
                    
                # Domain Analysis
                if any(word in query for word in ['domain', 'backlink', 'authority', 'moz', 'links', 'dns', 'whois']):
                    results.append({
                        "id": "domain_analysis",
                        "title": "Domain Intelligence & Backlink Analysis",
                        "url": "https://docs.fetchserp.com/api-reference/domains/backlinks"
                    })
                    
                # SERP Analysis
                if any(word in query for word in ['serp', 'ranking', 'google', 'search results', 'position', 'indexation']):
                    results.append({
                        "id": "serp_analysis", 
                        "title": "SERP Intelligence & Ranking Analysis",
                        "url": "https://docs.fetchserp.com/api-reference/serp/serp"
                    })
                    
                # Web Scraping
                if any(word in query for word in ['scrape', 'extract', 'content', 'data', 'crawl']):
                    results.append({
                        "id": "web_scraping",
                        "title": "Web Scraping & Data Extraction", 
                        "url": "https://docs.fetchserp.com/api-reference/scraping/scrape"
                    })
                    
                # Competitor Analysis
                if any(word in query for word in ['competitor', 'competition', 'rival', 'compare', 'competitive']):
                    results.append({
                        "id": "competitor_analysis",
                        "title": "Competitive Intelligence & Market Analysis",
                        "url": "https://docs.fetchserp.com/api-reference/competitive-analysis"
                    })
                
                # Default comprehensive results if no specific category
                if not results:
                    results = [
                        {
                            "id": "seo_analysis",
                            "title": "SEO Analysis & Website Audit", 
                            "url": "https://docs.fetchserp.com/api-reference/seo-analysis/web-page-seo-analysis"
                        },
                        {
                            "id": "keyword_research",
                            "title": "Keyword Research & Search Intelligence",
                            "url": "https://docs.fetchserp.com/api-reference/keywords/keywords-search-volume" 
                        },
                        {
                            "id": "domain_analysis", 
                            "title": "Domain Intelligence & Backlink Analysis",
                            "url": "https://docs.fetchserp.com/api-reference/domains/backlinks"
                        },
                        {
                            "id": "serp_analysis",
                            "title": "SERP Intelligence & Ranking Analysis", 
                            "url": "https://docs.fetchserp.com/api-reference/serp/serp"
                        }
                    ]
                
                # Return in OpenAI's required format: content array with JSON-encoded string
                results_json = json.dumps({"results": results})
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": results_json
                            }
                        ]
                    }
                }
            
            elif tool_name == "fetch":
                fetch_id = tool_args.get("id", "")
                
                # Define comprehensive analysis data
                analysis_data = {
                    "seo_analysis": {
                        "id": "seo_analysis",
                        "title": "SEO Analysis & Website Audit",
                        "text": "FetchSERP provides comprehensive SEO analysis through the web_page_seo_analysis API endpoint. This powerful tool delivers technical SEO audits including meta tags analysis, header structure evaluation, URL optimization, schema markup validation, internal linking assessment, on-page optimization analysis, content quality evaluation, Core Web Vitals metrics, mobile-friendliness checks, and performance optimization recommendations. The API provides real-time analysis with actionable insights for improving search engine rankings and website performance.",
                        "url": "https://docs.fetchserp.com/api-reference/seo-analysis/web-page-seo-analysis",
                        "metadata": {
                            "api_endpoint": "web_page_seo_analysis",
                            "data_freshness": "real-time",
                            "analysis_depth": "comprehensive"
                        }
                    },
                    "keyword_research": {
                        "id": "keyword_research", 
                        "title": "Keyword Research & Search Intelligence",
                        "text": "FetchSERP's keyword research capabilities provide advanced search intelligence through multiple API endpoints including monthly search volume data, keyword difficulty metrics, long-tail keyword generation, related keyword suggestions, search trends analysis, and competitive keyword research. The platform accesses global keyword data from 200+ countries with historical trends, seasonality patterns, and search intent classification for comprehensive SEO strategy development.",
                        "url": "https://docs.fetchserp.com/api-reference/keywords/keywords-search-volume",
                        "metadata": {
                            "api_endpoints": ["keywords_search_volume", "keywords_suggestions", "long_tail_keywords_generator"],
                            "geographic_coverage": "200+ countries",
                            "data_sources": "google_keyword_planner_and_serp_data"
                        }
                    },
                    "domain_analysis": {
                        "id": "domain_analysis",
                        "title": "Domain Intelligence & Backlink Analysis",
                        "text": "FetchSERP provides comprehensive domain intelligence including complete backlink profile analysis, domain authority metrics from Moz integration, technical domain information (DNS, WHOIS, SSL certificates), technology stack detection, competitive backlink analysis, and contact discovery. The platform analyzes over 200 billion backlinks and provides detailed insights into link quality, anchor text distribution, referring domains, and competitive opportunities for link building strategies.",
                        "url": "https://docs.fetchserp.com/api-reference/domains/backlinks",
                        "metadata": {
                            "api_endpoints": ["backlinks", "moz", "domain_infos", "domain_emails"],
                            "backlink_database": "200+ billion links",
                            "moz_integration": "official_api_partnership"
                        }
                    },
                    "serp_analysis": {
                        "id": "serp_analysis", 
                        "title": "SERP Intelligence & Ranking Analysis",
                        "text": "FetchSERP offers advanced SERP analysis across Google, Bing, Yahoo, and DuckDuckGo with real-time search results, AI Overview extraction, featured snippets analysis, ranking position tracking, SERP feature monitoring, and indexation verification. The platform provides sub-second response times for live SERP data collection, geographic ranking variations, mobile vs desktop differences, and comprehensive competitive ranking intelligence for strategic SEO planning.",
                        "url": "https://docs.fetchserp.com/api-reference/serp/serp",
                        "metadata": {
                            "search_engines": ["google", "bing", "yahoo", "duckduckgo"],
                            "geographic_coverage": "200+ countries",
                            "response_time": "sub_second"
                        }
                    },
                    "web_scraping": {
                        "id": "web_scraping",
                        "title": "Web Scraping & Data Extraction", 
                        "text": "FetchSERP provides advanced web scraping capabilities including full webpage content extraction, JavaScript-rendered content scraping, custom script execution, proxy-based geographic scraping, bulk domain crawling, structured data extraction, and performance monitoring. The platform supports ethical scraping practices with rate limiting, robots.txt compliance, and anti-detection techniques for reliable data collection from websites worldwide.",
                        "url": "https://docs.fetchserp.com/api-reference/scraping/scrape",
                        "metadata": {
                            "api_endpoints": ["scrape", "scrape_js", "scrape_js_with_proxy", "domain_scraping"],
                            "javascript_support": "full_browser_automation",
                            "proxy_locations": "50+ countries"
                        }
                    },
                    "competitor_analysis": {
                        "id": "competitor_analysis",
                        "title": "Competitive Intelligence & Market Analysis",
                        "text": "FetchSERP enables comprehensive competitive intelligence by combining SEO analysis, backlink research, keyword tracking, SERP monitoring, and technical analysis across multiple competitors. The platform provides strategic recommendations for outranking competitors, identifies market opportunities, analyzes competitive gaps, and delivers actionable insights for gaining competitive advantages in search engine rankings and digital marketing strategies.",
                        "url": "https://docs.fetchserp.com/api-reference/competitive-analysis",
                        "metadata": {
                            "analysis_scope": "comprehensive_multi_api",
                            "data_sources": ["seo_analysis", "backlinks", "keywords", "serp", "domain_intelligence"],
                            "competitive_depth": "strategic_recommendations_included"
                        }
                    }
                }
                
                # Get the requested analysis data
                data = analysis_data.get(fetch_id)
                if not data:
                    data = {
                        "id": "error",
                        "title": f"Unknown Analysis ID: {fetch_id}",
                        "text": f"The requested analysis ID '{fetch_id}' is not available. Available analysis IDs are: {', '.join(analysis_data.keys())}. Please use the search tool first to find valid analysis IDs.",
                        "url": "https://docs.fetchserp.com/api-reference/",
                        "metadata": {"error": "invalid_analysis_id", "available_ids": list(analysis_data.keys())}
                    }
                
                # Return in OpenAI's required format: content array with JSON-encoded string
                data_json = json.dumps(data)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": data_json
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
    if not FETCHSERP_API_TOKEN:
        print("❌ Error: FETCHSERP_API_TOKEN environment variable required")
        print("📝 Get your token at: https://www.fetchserp.com")
        exit(1)
        
    print("🚀 Starting OpenAI-Compatible FetchSERP MCP Server...")
    print(f"📍 Server URL: http://0.0.0.0:{PORT}/")
    print("🔗 For ChatGPT: Follows exact OpenAI MCP specifications")
    print("📊 Powered by FetchSERP API (25+ SEO tools)")
    print("✅ Deep Research Compatible")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
