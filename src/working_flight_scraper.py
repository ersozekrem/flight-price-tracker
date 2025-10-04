from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime

class WorkingFlightScraper:
    def __init__(self):
        self.service = Service('./chromedriver.exe')
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = None
        self.wait = None
    
    def start_driver(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.maximize_window()
    
    def search_with_assistance(self, origin, destination):
        """Semi-automated search with manual date selection"""
        print(f"🔍 Starting search: {origin} → {destination}")
        
        self.start_driver()
        
        # Start at Google Flights
        self.driver.get("https://www.google.com/travel/flights")
        time.sleep(3)
        
        print("\n" + "="*50)
        print("PLEASE COMPLETE THE SEARCH:")
        print("="*50)
        print(f"1. Set origin to: {origin}")
        print(f"2. Set destination to: {destination}")
        print("3. Select your date")
        print("4. Click Search/Explore")
        print("="*50)
        print("\n⏰ You have 45 seconds...\n")
        
        # Wait for manual input
        time.sleep(45)
        
        # Check if we're on results page
        current_url = self.driver.current_url
        if "search" in current_url or "booking" in current_url:
            print("✅ On results page!")
            return self.extract_flight_details()
        else:
            print("❌ Not on results page")
            return None
    
    def extract_flight_details(self):
        """Extract detailed flight information"""
        print("\n📊 Extracting flight details...")
        
        flights = []
        
        try:
            # Wait for page to stabilize
            time.sleep(3)
            
            # Method 1: Look for flight cards/containers
            # Try multiple possible selectors
            selectors = [
                "li[class*='pIav2d']",  # Common flight list item
                "div[jscontroller*='xKXaIb']",  # Flight controller
                "div[class*='yR1fYc']",  # Flight card
                "ul[role='list'] > li",  # List items
                "div[data-ved]"  # Elements with tracking
            ]
            
            flight_elements = []
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Check if these look like flight cards
                    for elem in elements[:3]:  # Check first 3
                        text = elem.text
                        if '$' in text and ('AM' in text or 'PM' in text or 'hr' in text):
                            flight_elements = elements
                            print(f"✅ Found flight elements with selector: {selector}")
                            break
                if flight_elements:
                    break
            
            # Extract data from flight elements
            for i, element in enumerate(flight_elements[:10]):  # First 10 flights
                try:
                    text = element.text
                    if '$' in text and len(text) > 20:  # Likely a flight
                        
                        # Create flight object
                        flight = {
                            "index": i + 1,
                            "raw_text": text,
                            "price": self.extract_price(text),
                            "times": self.extract_times(text),
                            "duration": self.extract_duration(text),
                            "airline": self.extract_airline(text),
                            "stops": self.extract_stops(text)
                        }
                        
                        flights.append(flight)
                        
                        # Print summary
                        print(f"\n✈️ Flight #{i+1}:")
                        print(f"   Price: {flight['price']}")
                        print(f"   Times: {flight['times']}")
                        print(f"   Duration: {flight['duration']}")
                        print(f"   Airline: {flight['airline']}")
                        print(f"   Stops: {flight['stops']}")
                        
                except Exception as e:
                    continue
            
            # If no structured data found, fall back to price extraction
            if not flights:
                print("⚠️ No flight cards found, extracting prices only...")
                price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
                
                for i, elem in enumerate(price_elements[:20]):
                    text = elem.text
                    if '$' in text and len(text) < 200:
                        flights.append({
                            "index": i + 1,
                            "price_text": text.strip()
                        })
            
            # Take screenshot
            self.driver.save_screenshot("flight_results_detailed.png")
            print(f"\n📸 Screenshot saved")
            print(f"✅ Extracted {len(flights)} flights")
            
        except Exception as e:
            print(f"❌ Error during extraction: {str(e)}")
        
        return flights
    
    def extract_price(self, text):
        """Extract price from text"""
        if '$' in text:
            # Find the dollar sign
            start = text.find('$')
            # Extract until space or newline
            end = start + 1
            while end < len(text) and text[end].isdigit():
                end += 1
            return text[start:end]
        return "N/A"
    
    def extract_times(self, text):
        """Extract departure and arrival times"""
        import re
        # Look for time patterns like 6:00 AM
        times = re.findall(r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)', text)
        if len(times) >= 2:
            return f"{times[0]} - {times[1]}"
        return "N/A"
    
    def extract_duration(self, text):
        """Extract flight duration"""
        import re
        # Look for patterns like "5 hr 30 min" or "5h 30m"
        duration = re.search(r'(\d+)\s*(?:hr|h)\s*(\d+)?\s*(?:min|m)?', text)
        if duration:
            hours = duration.group(1)
            mins = duration.group(2) if duration.group(2) else "0"
            return f"{hours}h {mins}m"
        return "N/A"
    
    def extract_airline(self, text):
        """Extract airline name"""
        # Common airlines
        airlines = ['United', 'American', 'Delta', 'Southwest', 'JetBlue', 
                   'Alaska', 'Spirit', 'Frontier', 'Hawaiian']
        
        for airline in airlines:
            if airline in text:
                return airline
        
        return "N/A"
    
    def extract_stops(self, text):
        """Extract number of stops"""
        if 'Nonstop' in text or 'nonstop' in text:
            return "Nonstop"
        elif '1 stop' in text:
            return "1 stop"
        elif '2 stop' in text:
            return "2 stops"
        elif 'stop' in text:
            return "Multiple stops"
        return "N/A"
    
    def save_results(self, flights, filename="flight_results.json"):
        """Save results to JSON file"""
        results = {
            "search_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": self.driver.current_url,
            "total_flights": len(flights),
            "flights": flights
        }
        
        with open(f"data/{filename}", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to data/{filename}")
        return results

# Main execution
if __name__ == "__main__":
    scraper = WorkingFlightScraper()
    
    # Search with manual assistance
    flights = scraper.search_with_assistance("JFK", "LAX")
    
    if flights:
        # Save results
        results = scraper.save_results(flights)
        
        print("\n" + "="*50)
        print("SEARCH COMPLETE!")
        print("="*50)
        print(f"Total flights found: {len(flights)}")
        
        # Print first 3 flights
        print("\nFirst 3 flights:")
        for flight in flights[:3]:
            print(f"\nFlight {flight.get('index', 'N/A')}:")
            if 'price' in flight:
                print(f"  Price: {flight.get('price', 'N/A')}")
                print(f"  Times: {flight.get('times', 'N/A')}")
            else:
                print(f"  {flight.get('price_text', 'N/A')}")
    
    print("\n🔄 Press Enter to close browser...")
    input()
    scraper.driver.quit()