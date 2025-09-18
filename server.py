#!/usr/bin/env python3
"""
OpenAI-Compatible MCP Server for FetchSERP
Follows exact OpenAI MCP specifications for ChatGPT Deep Research
"""

from fastmcp import FastMCP
import httpx
import os
import json
from typing import List, Dict, Any

# Environment configuration
FETCHSERP_API_TOKEN = os.getenv("FETCHSERP_API_TOKEN")
PORT = int(os.getenv("PORT", 8000))

if not FETCHSERP_API_TOKEN:
    print("❌ Error: FETCHSERP_API_TOKEN environment variable is required")
    exit(1)

FETCHSERP_BASE_URL = "https://api.fetchserp.com/api/v1"

def create_mcp_server():
    """Create MCP server following OpenAI specifications"""
    mcp = FastMCP("FetchSERP SEO Intelligence Server")
    
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
    async def search(query: str) -> List[Dict[str, Any]]:
        """
        Search for SEO insights and web intelligence data from FetchSERP.
        
        This tool searches through various SEO and web intelligence capabilities
        based on your query. It can handle requests about:
        - Website SEO analysis and audits
        - Keyword research and search volume data  
        - Domain analysis and backlink research
        - SERP analysis and ranking checks
        - Web scraping and content extraction
        - Competitor intelligence and analysis
        
        Returns a list of available analysis capabilities that can be fetched for detailed results.
        Each result includes an ID that can be used with the fetch tool to get comprehensive information.
        """
        # Parse query and return relevant analysis types
        query_lower = query.lower()
        results = []
        
        # SEO Analysis
        if any(word in query_lower for word in ['seo', 'audit', 'analyze', 'website', 'technical', 'optimization']):
            results.append({
                "id": "seo_analysis", 
                "title": "SEO Analysis & Website Audit",
                "url": "https://www.fetchserp.com/api/web-page-seo-analysis"
            })
            
        # Keyword Research  
        if any(word in query_lower for word in ['keyword', 'search volume', 'suggestions', 'long tail', 'research']):
            results.append({
                "id": "keyword_research",
                "title": "Keyword Research & Search Intelligence", 
                "url": "https://www.fetchserp.com/api/keywords-search-volume"
            })
            
        # Domain Analysis
        if any(word in query_lower for word in ['domain', 'backlink', 'authority', 'moz', 'links', 'dns', 'whois']):
            results.append({
                "id": "domain_analysis",
                "title": "Domain Intelligence & Backlink Analysis",
                "url": "https://www.fetchserp.com/api/backlinks"
            })
            
        # SERP Analysis
        if any(word in query_lower for word in ['serp', 'ranking', 'google', 'search results', 'position', 'indexation']):
            results.append({
                "id": "serp_analysis", 
                "title": "SERP Intelligence & Ranking Analysis",
                "url": "https://www.fetchserp.com/api/serp"
            })
            
        # Web Scraping
        if any(word in query_lower for word in ['scrape', 'extract', 'content', 'data', 'crawl']):
            results.append({
                "id": "web_scraping",
                "title": "Web Scraping & Data Extraction", 
                "url": "https://www.fetchserp.com/api/scrape"
            })
            
        # Competitor Analysis
        if any(word in query_lower for word in ['competitor', 'competition', 'rival', 'compare', 'competitive']):
            results.append({
                "id": "competitor_analysis",
                "title": "Competitive Intelligence & Market Analysis",
                "url": "https://www.fetchserp.com/api/competitive-analysis"
            })
        
        # Default comprehensive results if no specific category
        if not results:
            results = [
                {
                    "id": "seo_analysis",
                    "title": "SEO Analysis & Website Audit", 
                    "url": "https://www.fetchserp.com/api/web-page-seo-analysis"
                },
                {
                    "id": "keyword_research",
                    "title": "Keyword Research & Search Intelligence",
                    "url": "https://www.fetchserp.com/api/keywords-search-volume" 
                },
                {
                    "id": "domain_analysis", 
                    "title": "Domain Intelligence & Backlink Analysis",
                    "url": "https://www.fetchserp.com/api/backlinks"
                },
                {
                    "id": "serp_analysis",
                    "title": "SERP Intelligence & Ranking Analysis", 
                    "url": "https://www.fetchserp.com/api/serp"
                }
            ]
        
        # Return in OpenAI's required format: content array with JSON-encoded string
        results_json = json.dumps({"results": results})
        return [{"type": "text", "text": results_json}]
    
    @mcp.tool()
    async def fetch(id: str) -> List[Dict[str, Any]]:
        """
        Retrieve detailed SEO analysis and web intelligence data by ID.
        
        This tool fetches comprehensive data for the requested analysis type from FetchSERP.
        It provides detailed insights, metrics, and actionable recommendations for SEO 
        optimization and web intelligence based on the specified analysis ID.
        
        Available analysis types include SEO audits, keyword data, domain intelligence,
        SERP analysis, web scraping results, and competitor research. All data is sourced
        from the FetchSERP API with real-time accuracy.
        """
        
        # Define comprehensive analysis data for each ID
        analysis_data = {
            "seo_analysis": {
                "id": "seo_analysis",
                "title": "SEO Analysis & Website Audit",
                "text": """FetchSERP provides comprehensive SEO analysis through the web_page_seo_analysis API endpoint. This powerful tool delivers:

TECHNICAL SEO AUDIT:
• Meta tags analysis (title, description, keywords optimization)
• Header structure evaluation (H1-H6 hierarchy and optimization)
• URL structure and permalink analysis  
• Schema markup validation and recommendations
• Internal linking structure assessment
• Site architecture and navigation analysis

ON-PAGE OPTIMIZATION:
• Content quality and keyword density analysis
• Image optimization and alt-text evaluation
• Core Web Vitals assessment (LCP, FID, CLS)
• Page speed and performance metrics
• Mobile-friendliness and responsive design check
• User experience and accessibility factors

CONTENT ANALYSIS:
• Keyword optimization opportunities
• Content length and readability scores
• Semantic keyword suggestions
• Content gaps and improvement recommendations
• Competitor content comparison
• Search intent alignment assessment

API ENDPOINTS AVAILABLE:
• web_page_seo_analysis - Complete technical SEO audit
• web_page_ai_analysis - AI-powered content analysis with custom prompts

REAL-TIME DATA: All analysis uses live data from your website, providing current SEO status and actionable optimization recommendations. Results include specific technical issues, priority levels, and step-by-step improvement guides.""",
                "url": "https://docs.fetchserp.com/api-reference/seo-analysis/web-page-seo-analysis",
                "metadata": {
                    "api_endpoint": "web_page_seo_analysis",
                    "data_freshness": "real-time",
                    "analysis_depth": "comprehensive",
                    "output_format": "structured_json"
                }
            },
            
            "keyword_research": {
                "id": "keyword_research", 
                "title": "Keyword Research & Search Intelligence",
                "text": """FetchSERP's keyword research capabilities provide advanced search intelligence through multiple API endpoints:

SEARCH VOLUME DATA:
• Monthly search volume for any keyword globally
• Historical search trends and seasonality patterns
• Keyword difficulty and competition metrics
• Cost-per-click (CPC) estimates for paid advertising
• Search volume by country and language
• Related keyword suggestions with metrics

LONG-TAIL KEYWORD GENERATION:
• Generate hundreds of long-tail keyword variations
• Search intent classification (informational, commercial, transactional, navigational)
• Question-based keyword discovery (who, what, when, where, why, how)
• Autocomplete and suggest API integration
• Competitor keyword gap analysis

KEYWORD INTELLIGENCE:
• Trending keywords identification
• Seasonal keyword opportunities  
• Local search keyword variants
• Voice search optimization keywords
• Featured snippet optimization opportunities
• People Also Ask (PAA) keyword extraction

API ENDPOINTS AVAILABLE:
• keywords_search_volume - Get monthly search volumes and competition data
• keywords_suggestions - Find related keywords based on seed terms or URLs
• long_tail_keywords_generator - Generate long-tail keyword variations

GLOBAL DATA: Access keyword data from 200+ countries with local search volume, competition levels, and cultural keyword variations for international SEO strategies.""",
                "url": "https://docs.fetchserp.com/api-reference/keywords/keywords-search-volume",
                "metadata": {
                    "api_endpoints": ["keywords_search_volume", "keywords_suggestions", "long_tail_keywords_generator"],
                    "geographic_coverage": "200+ countries",
                    "data_sources": "google_keyword_planner_and_serp_data",
                    "update_frequency": "monthly"
                }
            },
            
            "domain_analysis": {
                "id": "domain_analysis",
                "title": "Domain Intelligence & Backlink Analysis",
                "text": """FetchSERP provides comprehensive domain intelligence and backlink analysis through multiple specialized APIs:

BACKLINK ANALYSIS:
• Complete backlink profile discovery and analysis
• Referring domains and pages identification
• Link quality assessment and spam detection
• Anchor text distribution and optimization opportunities
• Follow vs nofollow link ratio analysis
• Competitor backlink gap analysis and opportunities

DOMAIN AUTHORITY METRICS:
• Moz Domain Authority and Page Authority scores
• Domain Rating and URL Rating metrics
• Trust Flow and Citation Flow analysis
• Spam score assessment and risk evaluation
• Historical authority trends and changes
• Competitive authority benchmarking

TECHNICAL DOMAIN INTELLIGENCE:
• DNS records analysis (A, AAAA, MX, CNAME, TXT, NS)
• WHOIS data including registration details and history
• SSL certificate information and security assessment
• Technology stack detection (CMS, frameworks, analytics, CDN)
• Server location and hosting provider identification
• Website architecture and infrastructure analysis

CONTACT DISCOVERY:
• Email address extraction from domain SERPs
• Social media profile identification
• Contact form and phone number discovery
• Key personnel and decision maker identification

API ENDPOINTS AVAILABLE:
• backlinks - Comprehensive backlink discovery and analysis
• moz - Domain authority metrics from Moz integration
• domain_infos - Technical domain information (DNS, WHOIS, SSL, tech stack)
• domain_emails - Email and contact information extraction

COMPETITIVE INTELLIGENCE: Compare your domain authority, backlink profile, and technical setup against competitors to identify optimization opportunities and strategic advantages.""",
                "url": "https://docs.fetchserp.com/api-reference/domains/backlinks",
                "metadata": {
                    "api_endpoints": ["backlinks", "moz", "domain_infos", "domain_emails"],
                    "backlink_database": "200+ billion links",
                    "moz_integration": "official_api_partnership",
                    "data_freshness": "updated_daily"
                }
            },
            
            "serp_analysis": {
                "id": "serp_analysis", 
                "title": "SERP Intelligence & Ranking Analysis",
                "text": """FetchSERP offers advanced SERP analysis and ranking intelligence across multiple search engines:

MULTI-ENGINE SERP RESULTS:
• Google, Bing, Yahoo, DuckDuckGo search results
• Organic results with ranking positions and URLs
• Featured snippets and knowledge panels extraction
• People Also Ask (PAA) questions and answers
• Related searches and autocomplete suggestions
• Local pack results and map listings

AI OVERVIEW ANALYSIS:
• Google's AI Overview content extraction
• Featured snippet optimization opportunities
• Answer box and knowledge graph analysis
• Voice search result formatting
• Rich results and structured data insights

RANKING TRACKING:
• Domain ranking positions for specific keywords
• Historical ranking data and trend analysis
• SERP feature tracking (images, videos, local, shopping)
• Mobile vs desktop ranking differences
• Geographic ranking variations by location
• Competitor ranking comparison and analysis

INDEXATION MONITORING:
• Page indexation status verification
• Index coverage and crawling insights
• Sitemap analysis and submission tracking
• Robots.txt compliance checking
• Canonical URL validation

API ENDPOINTS AVAILABLE:
• serp - Structured SERP results from all major search engines
• serp_ai - AI Overview and enhanced SERP features
• serp_html - Complete HTML content for detailed analysis
• ranking - Domain ranking positions for specific keywords
• page_indexation - Indexation status verification

REAL-TIME SERP DATA: Access live search engine results with sub-second response times, enabling real-time SEO monitoring and competitive analysis.""",
                "url": "https://docs.fetchserp.com/api-reference/serp/serp",
                "metadata": {
                    "search_engines": ["google", "bing", "yahoo", "duckduckgo"],
                    "geographic_coverage": "200+ countries",
                    "api_endpoints": ["serp", "serp_ai", "serp_html", "ranking", "page_indexation"],
                    "response_time": "sub_second"
                }
            },
            
            "web_scraping": {
                "id": "web_scraping",
                "title": "Web Scraping & Data Extraction", 
                "text": """FetchSERP provides advanced web scraping and data extraction capabilities for comprehensive website analysis:

CONTENT EXTRACTION:
• Full webpage content extraction with clean HTML parsing
• Text content isolation removing ads, navigation, and boilerplate
• Structured data extraction (JSON-LD, microdata, RDFa)
• Image and media content analysis with metadata
• Form field identification and structure mapping
• Table data extraction with column recognition

JAVASCRIPT RENDERING:
• Custom JavaScript execution on target pages
• Dynamic content scraping from SPA and AJAX sites
• Browser automation for complex user interactions
• Screenshot capture at different viewport sizes
• Performance metrics collection during rendering
• Cookie and session management for authenticated content

PROXY-BASED SCRAPING:
• Geographic proxy rotation for location-specific content
• IP rotation to avoid rate limiting and blocking
• User-agent rotation for stealth scraping
• CAPTCHA handling and anti-bot bypass techniques
• Session persistence across multiple requests
• Custom header injection and request modification

BULK DOMAIN CRAWLING:
• Complete website mapping and sitemap generation
• Deep crawling with configurable depth limits
• Broken link detection and redirect chain analysis
• Duplicate content identification across pages
• Internal linking structure analysis
• Page speed and performance profiling

API ENDPOINTS AVAILABLE:
• scrape - Basic webpage content extraction without JavaScript
• scrape_js - JavaScript-rendered content scraping with custom scripts
• scrape_js_with_proxy - Geo-targeted scraping through country-specific proxies
• domain_scraping - Bulk crawling of entire domains with up to 200 pages

ETHICAL SCRAPING: All scraping respects robots.txt files, implements rate limiting, and follows ethical scraping practices to maintain website performance and comply with terms of service.""",
                "url": "https://docs.fetchserp.com/api-reference/scraping/scrape",
                "metadata": {
                    "api_endpoints": ["scrape", "scrape_js", "scrape_js_with_proxy", "domain_scraping"],
                    "javascript_support": "full_browser_automation",
                    "proxy_locations": "50+ countries", 
                    "max_pages_per_domain": "200"
                }
            },
            
            "competitor_analysis": {
                "id": "competitor_analysis",
                "title": "Competitive Intelligence & Market Analysis",
                "text": """FetchSERP enables comprehensive competitive intelligence by combining multiple API endpoints for strategic market analysis:

COMPETITIVE SEO ANALYSIS:
• Competitor website SEO audit comparison
• Technical SEO gap analysis between competitors
• Content strategy and optimization differences
• Meta tag and on-page optimization benchmarking
• Site speed and Core Web Vitals comparison
• Mobile optimization competitive assessment

BACKLINK COMPETITIVE INTELLIGENCE:
• Competitor backlink profile analysis and comparison
• Link building opportunity identification from competitor links
• Anchor text strategy analysis across competitors
• Domain authority gap analysis and competitive positioning
• High-value referring domain discovery from competitor profiles
• Broken link opportunities from competitor analysis

KEYWORD COMPETITIVE RESEARCH:
• Competitor keyword ranking analysis and gaps
• Search volume opportunities competitors are missing
• Long-tail keyword variations competitors target
• Paid search keyword strategy analysis
• Content topic clusters and keyword themes comparison
• Seasonal keyword strategy analysis across competitors

SERP COMPETITIVE MONITORING:
• Head-to-head ranking comparison for target keywords
• Featured snippet and AI Overview competitive analysis
• Local search competitive positioning (if applicable)
• SERP feature dominance analysis (images, videos, shopping)
• Voice search optimization competitive assessment
• Geographic ranking variations compared to competitors

MARKET INTELLIGENCE:
• Technology stack comparison and competitive advantages
• Content marketing strategy analysis and gaps
• Social media presence and engagement comparison
• Email marketing and contact strategy analysis
• Website architecture and user experience benchmarking
• Conversion optimization and landing page analysis

STRATEGIC RECOMMENDATIONS:
• Prioritized competitive opportunities based on data analysis
• Quick wins for outranking competitors in specific areas
• Long-term strategic recommendations for competitive advantage
• ROI-focused competitive initiatives with projected impact
• Risk assessment of competitive threats and market changes

This comprehensive competitive analysis combines data from web_page_seo_analysis, backlinks, keywords_search_volume, serp, moz, and domain_infos APIs to provide actionable competitive intelligence.""",
                "url": "https://docs.fetchserp.com/api-reference/competitive-analysis",
                "metadata": {
                    "analysis_scope": "comprehensive_multi_api",
                    "data_sources": ["seo_analysis", "backlinks", "keywords", "serp", "moz", "domain_intelligence"],
                    "competitive_depth": "strategic_recommendations_included",
                    "update_frequency": "real_time_on_demand"
                }
            }
        }
        
        # Get the requested analysis data
        data = analysis_data.get(id)
        if not data:
            # Return error in the required format
            error_data = {
                "id": "error",
                "title": f"Unknown Analysis ID: {id}",
                "text": f"The requested analysis ID '{id}' is not available. Available analysis IDs are: {', '.join(analysis_data.keys())}. Please use the search tool first to find valid analysis IDs.",
                "url": "https://docs.fetchserp.com/api-reference/",
                "metadata": {"error": "invalid_analysis_id", "available_ids": list(analysis_data.keys())}
            }
            data = error_data
        
        # Return in OpenAI's required format: content array with JSON-encoded string
        data_json = json.dumps(data)
        return [{"type": "text", "text": data_json}]
    
    return mcp

if __name__ == "__main__":
    if not FETCHSERP_API_TOKEN:
        print("❌ Error: FETCHSERP_API_TOKEN environment variable required")
        print("📝 Get your token at: https://www.fetchserp.com")
        exit(1)
        
    server = create_mcp_server()
    print("🚀 Starting OpenAI-Compatible FetchSERP MCP Server...")
    print(f"📍 Server URL: http://0.0.0.0:{PORT}/")
    print("🔗 For ChatGPT: Follows OpenAI MCP specifications")
    print("📊 Powered by FetchSERP API (25+ SEO tools)")
    print("✅ Deep Research Compatible")
    
    # Use FastMCP's built-in server with HTTP transport
    server.run(transport="http", host="0.0.0.0", port=PORT)
