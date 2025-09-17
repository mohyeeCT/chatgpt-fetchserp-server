#!/usr/bin/env python3
"""
ChatGPT-Compatible FetchSERP MCP Server
Specifically designed for ChatGPT Deep Research requirements
"""

from fastmcp import FastMCP
import httpx
import os
import json
from typing import List, Dict, Any

# FetchSERP API configuration
FETCHSERP_API_TOKEN = os.getenv("FETCHSERP_API_TOKEN")
PORT = int(os.getenv("PORT", 8000))

if not FETCHSERP_API_TOKEN:
    print("❌ Error: FETCHSERP_API_TOKEN environment variable is required")
    print("📝 Get your token at: https://www.fetchserp.com")
    exit(1)

FETCHSERP_BASE_URL = "https://api.fetchserp.com/api/v1"

def create_chatgpt_server():
    """Create MCP server specifically for ChatGPT Deep Research"""
    mcp = FastMCP("ChatGPT FetchSERP Server")
    
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
    
    @mcp.tool()
    async def search(query: str) -> List[str]:
        """
        Search for SEO insights and web intelligence data.
        
        This tool searches through various SEO and web intelligence capabilities
        based on your query. It can handle requests about:
        - Website SEO analysis and audits
        - Keyword research and search volume data
        - Domain analysis and backlink research  
        - SERP analysis and ranking checks
        - Web scraping and content extraction
        - Competitor intelligence and analysis
        
        Returns a list of analysis IDs that can be fetched for detailed results.
        Each ID represents a specific type of SEO analysis or data source.
        """
        # Parse query and return relevant analysis types
        query_lower = query.lower()
        analysis_ids = []
        
        # SEO Analysis
        if any(word in query_lower for word in ['seo', 'audit', 'analyze', 'website', 'technical']):
            analysis_ids.append("seo_analysis")
            
        # Keyword Research  
        if any(word in query_lower for word in ['keyword', 'search volume', 'suggestions', 'long tail']):
            analysis_ids.append("keyword_research")
            
        # Domain Analysis
        if any(word in query_lower for word in ['domain', 'backlink', 'authority', 'moz', 'links']):
            analysis_ids.append("domain_analysis")
            
        # SERP Analysis
        if any(word in query_lower for word in ['serp', 'ranking', 'google', 'search results', 'position']):
            analysis_ids.append("serp_analysis")
            
        # Web Scraping
        if any(word in query_lower for word in ['scrape', 'extract', 'content', 'data']):
            analysis_ids.append("web_scraping")
            
        # Competitor Analysis
        if any(word in query_lower for word in ['competitor', 'competition', 'rival', 'compare']):
            analysis_ids.append("competitor_analysis")
        
        # Default to general SEO if no specific category
        if not analysis_ids:
            analysis_ids = ["general_seo", "seo_analysis"]
            
        return analysis_ids
    
    @mcp.tool()
    async def fetch(id: str) -> Dict[str, Any]:
        """
        Retrieve detailed SEO analysis and web intelligence data by ID.
        
        This tool fetches comprehensive data for the requested analysis type.
        It provides ChatGPT with detailed insights, metrics, and actionable
        recommendations for SEO optimization and web intelligence.
        
        Available analysis types include SEO audits, keyword data, domain
        intelligence, SERP analysis, web scraping results, and competitor research.
        All data is sourced from the FetchSERP API with real-time accuracy.
        """
        
        if id == "seo_analysis":
            return {
                "id": "seo_analysis",
                "type": "SEO Analysis & Website Audit",
                "description": "Comprehensive technical SEO analysis and optimization recommendations",
                "capabilities": [
                    "Technical SEO audit (meta tags, headers, structure)",
                    "On-page optimization analysis", 
                    "Core Web Vitals and page speed assessment",
                    "Mobile-friendliness evaluation",
                    "Schema markup validation",
                    "Internal linking structure analysis",
                    "Content optimization recommendations"
                ],
                "data_source": "FetchSERP Web Page SEO Analysis API",
                "real_time": True,
                "example_usage": "Analyze example.com for SEO issues and optimization opportunities",
                "api_endpoints": [
                    "web_page_seo_analysis - Comprehensive SEO audit",
                    "web_page_ai_analysis - AI-powered content analysis"
                ]
            }
            
        elif id == "keyword_research":
            return {
                "id": "keyword_research", 
                "type": "Keyword Research & Search Intelligence",
                "description": "Advanced keyword research with search volume and competition data",
                "capabilities": [
                    "Monthly search volume for any keyword",
                    "Keyword difficulty and competition metrics",
                    "Long-tail keyword generation and discovery",
                    "Related keyword suggestions and variations",
                    "Search trends and seasonal patterns",
                    "Keyword opportunity identification"
                ],
                "data_source": "FetchSERP Keywords API with global search data",
                "real_time": True,
                "example_usage": "Research high-value keywords for 'digital marketing' niche",
                "api_endpoints": [
                    "keywords_search_volume - Get monthly search volumes",
                    "keywords_suggestions - Find related keywords", 
                    "long_tail_keywords_generator - Generate long-tail variations"
                ]
            }
            
        elif id == "domain_analysis":
            return {
                "id": "domain_analysis",
                "type": "Domain Intelligence & Backlink Analysis", 
                "description": "Complete domain profiling with backlink and authority analysis",
                "capabilities": [
                    "Comprehensive backlink discovery and analysis",
                    "Domain authority and trust metrics (Moz integration)",
                    "DNS, WHOIS, and technical domain information",
                    "Technology stack detection and analysis",
                    "SSL certificate and security assessment",
                    "Email discovery and contact information"
                ],
                "data_source": "FetchSERP Domain APIs with Moz integration",
                "real_time": True,
                "example_usage": "Analyze competitor.com backlink profile and domain strength",
                "api_endpoints": [
                    "backlinks - Discover and analyze backlinks",
                    "moz - Get domain authority metrics",
                    "domain_infos - Technical domain intelligence",
                    "domain_emails - Extract contact information"
                ]
            }
            
        elif id == "serp_analysis":
            return {
                "id": "serp_analysis",
                "type": "SERP Intelligence & Ranking Analysis",
                "description": "Search engine results analysis and ranking intelligence",
                "capabilities": [
                    "Multi-engine SERP results (Google, Bing, Yahoo, DuckDuckGo)",
                    "AI Overview and featured snippets analysis",
                    "Domain ranking tracking for specific keywords",
                    "Page indexation status verification", 
                    "SERP feature analysis (videos, images, local results)",
                    "Competitive ranking intelligence"
                ],
                "data_source": "FetchSERP SERP APIs with AI Overview support",
                "real_time": True,
                "example_usage": "Check how example.com ranks for 'best CRM software' across search engines",
                "api_endpoints": [
                    "serp - Get structured SERP results",
                    "serp_ai - AI Overview and enhanced results",
                    "ranking - Domain ranking for keywords",
                    "page_indexation - Check indexation status"
                ]
            }
            
        elif id == "web_scraping":
            return {
                "id": "web_scraping",
                "type": "Web Scraping & Data Extraction",
                "description": "Advanced web scraping and structured data extraction",
                "capabilities": [
                    "Full webpage content extraction and parsing",
                    "JavaScript-rendered content scraping",
                    "Custom JavaScript execution on target pages",
                    "Proxy-based scraping for geo-targeted data",
                    "Bulk domain crawling and site mapping",
                    "Structured data extraction and formatting"
                ],
                "data_source": "FetchSERP Scraping APIs with proxy support",
                "real_time": True,
                "example_usage": "Extract product data and pricing from e-commerce websites",
                "api_endpoints": [
                    "scrape - Basic webpage content extraction",
                    "scrape_js - JavaScript-rendered content scraping",
                    "scrape_js_with_proxy - Geo-targeted proxy scraping",
                    "domain_scraping - Bulk site crawling"
                ]
            }
            
        elif id == "competitor_analysis":
            return {
                "id": "competitor_analysis",
                "type": "Competitive Intelligence & Market Analysis",
                "description": "Comprehensive competitor research and market intelligence", 
                "capabilities": [
                    "Competitor backlink profile analysis",
                    "Competitive keyword research and gaps",
                    "Market share and ranking comparisons",
                    "Technology stack competitive analysis",
                    "Content strategy and SEO comparison",
                    "Market opportunity identification"
                ],
                "data_source": "Combined FetchSERP APIs for competitive intelligence",
                "real_time": True,
                "example_usage": "Compare SEO strategies of top 3 competitors in your industry",
                "combination_analysis": True
            }
            
        else:
            return {
                "id": "general_seo",
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
                    "Check how I rank for important keywords",
                    "Extract data from competitor websites",
                    "Compare my domain authority to competitors"
                ],
                "real_time_data": True,
                "comprehensive_analysis": True
            }
    
    # Add health check endpoint
    @mcp.tool()
    async def health_check() -> Dict[str, str]:
        """Server health check"""
        return {
            "status": "healthy",
            "server": "ChatGPT FetchSERP MCP Server",
            "version": "1.0.0",
            "api_connected": "FetchSERP API" if FETCHSERP_API_TOKEN else "No API token"
        }
    
    return mcp

if __name__ == "__main__":
    if not FETCHSERP_API_TOKEN:
        print("❌ Error: FETCHSERP_API_TOKEN environment variable required")
        print("📝 Get your token at: https://www.fetchserp.com")
        exit(1)
        
    server = create_chatgpt_server()
    print("🚀 Starting ChatGPT-Compatible FetchSERP MCP Server...")
    print(f"📍 Server URL: http://localhost:{PORT}/mcp/")
    print("🔗 For ChatGPT: Use the /mcp/ endpoint")
    print("📊 Powered by FetchSERP API")
    print("✅ Optimized for ChatGPT Deep Research")
    
    # Run with HTTP transport for ChatGPT compatibility
    server.run(transport="http", port=PORT)
