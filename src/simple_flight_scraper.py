from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json

class SimpleFlightScraper:
    def __init__(self):
        self.service = Service('./chromedriver.exe')
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = None
    
    def search_manual(self):
        """Open Google Flights and let user search manually"""
        print("🔍 Opening Google Flights...")
        
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.maximize_window()
        
        # Go to Google Flights
        self.driver.get("https://www.google.com/travel/flights")
        time.sleep(3)
        
        print("\n" + "="*50)
        print("MANUAL SEARCH INSTRUCTIONS:")
        print("="*50)
        print("1. Clear the origin field (click and delete)")
        print("2. Type 'JFK' and select from dropdown")
        print("3. Clear destination field")
        print("4. Type 'LAX' and select from dropdown")
        print("5. Click on date field")
        print("6. Select any date in December 2024")
        print("7. Click 'Search' or 'Explore' button")
        print("="*50)
        print("\n⏰ You have 60 seconds to complete the search...\n")
        
        # Wait 60 seconds for manual search
        for i in range(60, 0, -10):
            print(f"⏱️  {i} seconds remaining...")
            time.sleep(10)
        
        print("\n📊 Attempting to extract results...")
        
        # Get current URL to see if we're on results
        current_url = self.driver.current_url
        print(f"📍 Current URL: {current_url[:100]}...")
        
        # Take screenshot
        self.driver.save_screenshot("manual_search_results.png")
        print("📸 Screenshot saved as 'manual_search_results.png'")
        
        # Try to find ANY price data
        results = []
        
        try:
            # Look for anything with a dollar sign
            all_elements = self.driver.find_elements(By.XPATH, "//*")
            price_count = 0
            
            for element in all_elements:
                try:
                    text = element.text
                    if '$' in text and len(text) < 100:  # Likely a price
                        price_count += 1
                        if price_count <= 10:  # First 10 prices
                            results.append({
                                "element": price_count,
                                "text": text.strip()
                            })
                            print(f"💰 Found price #{price_count}: {text.strip()}")
                except:
                    continue
            
            print(f"\n✅ Total price elements found: {price_count}")
            
        except Exception as e:
            print(f"❌ Error extracting data: {str(e)}")
        
        print("\n🔄 Press Enter to close browser...")
        input()
        self.driver.quit()
        
        return {
            "url": current_url,
            "prices_found": len(results),
            "sample_prices": results[:5]
        }

# Run the manual scraper
if __name__ == "__main__":
    scraper = SimpleFlightScraper()
    result = scraper.search_manual()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    print(json.dumps(result, indent=2))