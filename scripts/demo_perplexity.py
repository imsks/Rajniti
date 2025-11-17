#!/usr/bin/env python3
"""
Demo script showing Perplexity API integration structure.

This demonstrates how the code is structured without making actual API calls.
For real testing, use test_perplexity.py with a valid API key.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def demo_service_structure():
    """Demonstrate the service structure and usage patterns"""

    print("\n" + "🎯" * 35)
    print("Perplexity API Integration - Code Structure Demo")
    print("🎯" * 35 + "\n")

    print("📦 Package Information:")
    print("=" * 70)
    print("   Package: perplexityai (installed via pip)")
    print("   Import: from perplexity import Perplexity")
    print("   Service: app.services.perplexity_service.PerplexityService")
    print()

    print("🔧 Configuration:")
    print("=" * 70)
    print("   Environment variable: PERPLEXITY_API_KEY")
    print("   Config file: .env (copied from .env.example)")
    print("   Get your key at: https://www.perplexity.ai/")
    print()

    print("💻 Usage Example 1: Basic Search")
    print("=" * 70)
    print("""
from app.services.perplexity_service import PerplexityService

# Initialize service (reads PERPLEXITY_API_KEY from environment)
service = PerplexityService()

# Simple search with automatic India filter
results = service.search("Latest election results in India 2025")

# Access results
print(results['answer'])      # AI-generated answer
print(results['citations'])   # List of source URLs
print(results['model'])       # Model used (e.g., 'sonar')
print(results['location'])    # Location filter applied
""")

    print("💻 Usage Example 2: Region-Specific Search")
    print("=" * 70)
    print("""
# Search with specific region and city
results = service.search_india(
    query="political news today",
    region="Delhi",
    city="New Delhi"
)

# Results will be filtered for Delhi region
print(f"Answer: {results['answer']}")
""")

    print("💻 Usage Example 3: Multiple Queries")
    print("=" * 70)
    print("""
# Batch search multiple queries
queries = [
    "Lok Sabha election 2024 results",
    "Delhi Assembly election 2025 results",
    "Maharashtra Assembly election 2024 results"
]

results = service.search_multiple_queries(queries)

# Process all results
for result in results:
    print(f"Query: {result['query']}")
    print(f"Answer: {result['answer'][:100]}...")
    print()
""")

    print("💻 Usage Example 4: Custom Location")
    print("=" * 70)
    print("""
# Precise location with coordinates
location = {
    "country": "IN",
    "region": "Maharashtra",
    "city": "Mumbai",
    "latitude": 19.0760,
    "longitude": 72.8777
}

results = service.search(
    "local political events",
    location=location
)
""")

    print("📊 Response Format:")
    print("=" * 70)
    print("""
{
    "query": "Your search query",
    "answer": "AI-generated answer based on search results",
    "citations": [
        "https://source1.com",
        "https://source2.com",
        ...
    ],
    "model": "sonar",
    "location": {"country": "IN"}
}

# On error:
{
    "query": "Your search query",
    "error": "Error message",
    "answer": None,
    "citations": []
}
""")

    print("🔒 Security Best Practices:")
    print("=" * 70)
    print("   ✅ Use environment variables for API keys")
    print("   ✅ Never commit .env files to git")
    print("   ✅ Use .env.example as template (no real keys)")
    print("   ✅ Keep .env in .gitignore")
    print()

    print("🧪 Testing:")
    print("=" * 70)
    print("   1. Set your API key:")
    print("      export PERPLEXITY_API_KEY='your-api-key'")
    print()
    print("   2. Run test script:")
    print("      python scripts/test_perplexity.py")
    print()
    print("   3. Or use in your code:")
    print("      from app.services import PerplexityService")
    print("      service = PerplexityService()")
    print("      results = service.search('your query')")
    print()

    print("📚 Available Methods:")
    print("=" * 70)
    
    # Import and inspect the service
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "perplexity_service",
            Path(__file__).parent.parent / "app" / "services" / "perplexity_service.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        PerplexityService = module.PerplexityService
        
        import inspect
        methods = [m for m in dir(PerplexityService) if not m.startswith('_')]
        
        for method_name in methods:
            method = getattr(PerplexityService, method_name)
            if callable(method):
                sig = inspect.signature(method)
                doc = inspect.getdoc(method) or "No description"
                first_line = doc.split('\n')[0]
                print(f"   • {method_name}{sig}")
                print(f"     → {first_line}")
                print()
                
    except Exception as e:
        print(f"   (Could not load method details: {e})")
        print("   • search(query, max_results, location)")
        print("   • search_india(query, max_results, region, city)")
        print("   • search_multiple_queries(queries, location)")
        print()

    print("🌐 Features:")
    print("=" * 70)
    print("   ✅ India-focused search by default")
    print("   ✅ Region and city-level filtering")
    print("   ✅ Batch query support")
    print("   ✅ AI-powered answers with citations")
    print("   ✅ Automatic error handling")
    print("   ✅ Customizable location filters")
    print()

    print("🔗 Resources:")
    print("=" * 70)
    print("   • Perplexity Docs: https://docs.perplexity.ai/")
    print("   • API Guide: https://docs.perplexity.ai/guides/search-guide")
    print("   • Location Filters: https://docs.perplexity.ai/guides/user-location-filter-guide")
    print("   • Get API Key: https://www.perplexity.ai/")
    print()

    print("✅ Integration Complete!")
    print("=" * 70)
    print("   The Perplexity API is ready to use.")
    print("   Just add your API key and start searching!")
    print()


if __name__ == "__main__":
    demo_service_structure()
