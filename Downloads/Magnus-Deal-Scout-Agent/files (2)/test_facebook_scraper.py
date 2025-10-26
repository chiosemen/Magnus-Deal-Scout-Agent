#!/usr/bin/env python3
"""
Test script for Facebook Marketplace scraper
Run this to verify the scraper is working correctly

Usage:
    python test_facebook_scraper.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.facebook_scraper import FacebookMarketplaceScraper


async def test_url_monitoring():
    """Test URL monitoring mode"""
    print("=" * 60)
    print("TEST 1: URL Monitoring Mode")
    print("=" * 60)
    
    # Example Facebook Marketplace URL
    url = "https://www.facebook.com/marketplace/london/search?query=iphone"
    
    print(f"\n📡 Monitoring URL: {url}")
    print("This is the SAFER method - recommended for production\n")
    
    try:
        async with FacebookMarketplaceScraper(headless=True) as scraper:
            listings = await scraper.monitor_url(url)
            
            print(f"✅ SUCCESS! Found {len(listings)} listings\n")
            
            # Display first 3 listings
            for i, listing in enumerate(listings[:3], 1):
                print(f"{i}. {listing['title']}")
                print(f"   💰 Price: £{listing['price']}")
                print(f"   📍 Location: {listing.get('location', 'N/A')}")
                print(f"   🔗 URL: {listing['url']}")
                print()
            
            if len(listings) > 3:
                print(f"... and {len(listings) - 3} more listings")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_automated_search():
    """Test automated search mode"""
    print("\n" + "=" * 60)
    print("TEST 2: Automated Search Mode")
    print("=" * 60)
    
    print("\n🤖 Automated search for 'iPhone 13' in London")
    print("This is MORE POWERFUL but against Facebook TOS\n")
    
    try:
        async with FacebookMarketplaceScraper(headless=True) as scraper:
            listings = await scraper.search(
                keywords='iPhone 13',
                location='london',
                max_price=500,
                max_results=5
            )
            
            print(f"✅ SUCCESS! Found {len(listings)} listings under £500\n")
            
            for i, listing in enumerate(listings, 1):
                print(f"{i}. {listing['title']}")
                print(f"   💰 Price: £{listing['price']}")
                print(f"   📍 Location: {listing.get('location', 'N/A')}")
                print(f"   🔗 URL: {listing['url']}")
                print()
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_visible_browser():
    """Test with visible browser (for debugging)"""
    print("\n" + "=" * 60)
    print("TEST 3: Visible Browser (Watch It Work!)")
    print("=" * 60)
    
    print("\n👀 This will open a real browser window")
    print("You can watch the scraper work in real-time")
    print("Press Ctrl+C to skip this test\n")
    
    try:
        # Give user time to read
        await asyncio.sleep(3)
        
        print("🌐 Opening browser...")
        
        async with FacebookMarketplaceScraper(headless=False) as scraper:  # Visible!
            listings = await scraper.search(
                keywords='laptop',
                location='london',
                max_results=3
            )
            
            print(f"\n✅ Found {len(listings)} laptops")
            return True
            
    except KeyboardInterrupt:
        print("\n⏭️  Skipped visible browser test")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n🎭 FACEBOOK MARKETPLACE SCRAPER TEST SUITE")
    print("=" * 60)
    print("\nThis will test the Playwright-based scraper")
    print("Make sure you have run: playwright install chromium")
    print("\nStarting tests in 3 seconds...\n")
    
    await asyncio.sleep(3)
    
    results = {}
    
    # Test 1: URL Monitoring
    results['url_monitoring'] = await test_url_monitoring()
    
    # Test 2: Automated Search
    results['automated_search'] = await test_automated_search()
    
    # Test 3: Visible Browser (optional)
    print("\n" + "=" * 60)
    response = input("Run visible browser test? (y/n): ")
    if response.lower() == 'y':
        results['visible_browser'] = await test_with_visible_browser()
    else:
        print("⏭️  Skipping visible browser test")
        results['visible_browser'] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⏭️  SKIPPED"
        
        print(f"{status:12} {test_name.replace('_', ' ').title()}")
    
    # Check if all passed
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    print("\n" + "=" * 60)
    if passed == total and total > 0:
        print("🎉 ALL TESTS PASSED! Facebook scraper is working!")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\nTroubleshooting tips:")
        print("1. Make sure Playwright is installed: pip install playwright")
        print("2. Install browser: playwright install chromium")
        print("3. Check your internet connection")
        print("4. Facebook may be blocking automated access")
        print("5. Try running with headless=False to see what's happening")
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
