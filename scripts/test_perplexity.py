#!/usr/bin/env python3
"""
Test script for Perplexity API integration.

This script demonstrates how to use the Perplexity service for India-based searches.
Make sure to set PERPLEXITY_API_KEY environment variable before running.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.perplexity_service import PerplexityService


def print_separator():
    """Print a separator line"""
    print("\n" + "=" * 80 + "\n")


def test_basic_search():
    """Test basic search functionality"""
    print("🔍 Testing Basic India Search...")
    print_separator()

    try:
        # Initialize service
        service = PerplexityService()
        print("✅ Perplexity service initialized successfully")

        # Test search
        query = "Latest election results in India 2025"
        print(f"\n📝 Query: {query}")

        results = service.search(query, max_results=5)

        if "error" in results and results["error"]:
            print(f"❌ Error: {results['error']}")
            return False

        print(f"\n✅ Search completed successfully!")
        print(f"Model used: {results.get('model', 'N/A')}")
        print(f"Location filter: {results.get('location', {})}")
        print(f"\n📄 Answer:\n{results.get('answer', 'No answer')[:500]}...")

        if results.get("citations"):
            print(f"\n📚 Citations ({len(results['citations'])}):")
            for i, citation in enumerate(results["citations"][:3], 1):
                print(f"  {i}. {citation}")

        return True

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print(
            "\n💡 Make sure to set PERPLEXITY_API_KEY environment variable or create .env file"
        )
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


def test_region_specific_search():
    """Test region-specific search"""
    print("🔍 Testing Region-Specific Search (Delhi)...")
    print_separator()

    try:
        service = PerplexityService()

        query = "political news today"
        print(f"📝 Query: {query}")
        print(f"📍 Location: Delhi, India")

        results = service.search_india(query, region="Delhi", city="New Delhi")

        if "error" in results and results["error"]:
            print(f"❌ Error: {results['error']}")
            return False

        print(f"\n✅ Search completed successfully!")
        print(f"\n📄 Answer:\n{results.get('answer', 'No answer')[:500]}...")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_multiple_queries():
    """Test multiple queries in batch"""
    print("🔍 Testing Multiple Queries...")
    print_separator()

    try:
        service = PerplexityService()

        queries = [
            "Lok Sabha election 2024 results",
            "Delhi Assembly election 2025 results",
        ]

        print(f"📝 Queries: {len(queries)}")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")

        results = service.search_multiple_queries(queries)

        print(f"\n✅ Batch search completed!")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Query: {result.get('query', 'N/A')}")
            if "error" in result and result["error"]:
                print(f"Error: {result['error']}")
            else:
                print(f"Answer preview: {result.get('answer', 'No answer')[:200]}...")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀" * 40)
    print("Perplexity API Integration Test")
    print("🚀" * 40 + "\n")

    # Check if API key is set
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("⚠️  WARNING: PERPLEXITY_API_KEY environment variable not set")
        print("\n📋 To set it:")
        print("   export PERPLEXITY_API_KEY='your-api-key-here'")
        print("\n   OR create a .env file with:")
        print("   PERPLEXITY_API_KEY=your-api-key-here")
        print_separator()
        print("Attempting to run tests anyway (will fail if key not found)...\n")

    tests = [
        ("Basic Search", test_basic_search),
        ("Region-Specific Search", test_region_specific_search),
        ("Multiple Queries", test_multiple_queries),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

        print_separator()

    # Summary
    print("\n📊 Test Summary:")
    print_separator()
    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(
            f"\n⚠️  {total - passed} test(s) failed. Check errors above for details."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
