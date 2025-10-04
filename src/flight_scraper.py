from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import json

class GoogleFlightsScraper:
    def __init__(self, headless=False):
        """Initialize the scraper with Chrome options"""
        self.service = Service('./chromedriver.exe')
        self.options = webdriver.ChromeOptions()
        
        # Add options to avoid detection
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
        if headless:
            self.options.add_argument('--headless')
        
        self.driver = None
        self.wait = None
    
    def start_driver(self):
        """Start the Chrome driver"""
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.maximize_window()
    
    def close_driver(self):
        """Close the Chrome driver"""
        if self.driver:
            self.driver.quit()
    
    def search_flights(self, origin, destination, departure_date, return_date=None):
        """Search for flights and extract data"""
        print(f"🔍 Searching flights from {origin} to {destination} on {departure_date}")
        
        self.start_driver()
        
        try:
            # Go to Google Flights with a more specific URL
            url = f"https://www.google.com/travel/flights/search?tfs=CBwQAhoeagwIAxIIL20vMDJfMjg2EgoyMDI0LTAzLTE1cgcIARIDTEFYcAGCAQsI____________AUABSAGYAAQ&tfu=CnRDalJJWTJKbVNVMXJOMU5uY1VGQmRIbEJSeTFDUlVGQlFVRkJRVUZ2WTBsVFFVRkJFZ2t5TlRjc01qWTNOaG9MQ0xIWEF4QUNHZ05WVTBRNElCb0xDSy1iQXhBQ0dnTlZVMFE0SUFFb0EySUNDQVE9Gg0Ikc0BEgkvbS8wNWZzeg"
            
            self.driver.get("https://www.google.com/travel/flights")
            time.sleep(3)
            
            # Debug: Print current URL
            print(f"📍 Current URL: {self.driver.current_url}")
            
            # Try multiple selectors for the trip type
            trip_selectors = [
                "//div[@role='radiogroup']//div[contains(@aria-label,'One way')]",
                "//span[contains(text(),'One way')]",
                "//div[contains(text(),'One way')]",
                "//button[contains(@aria-label,'One way')]"
            ]
            
            for selector in trip_selectors:
                try:
                    print(f"🔍 Trying selector: {selector}")
                    trip_type = self.driver.find_element(By.XPATH, selector)
                    trip_type.click()
                    print("✅ Successfully clicked 'One way'")
                    time.sleep(1)
                    break
                except:
                    continue
            
            # Try multiple selectors for origin input
            origin_selectors = [
                "//input[@aria-label='Where from?']",
                "//input[@placeholder='Where from?']",
                "//input[contains(@aria-label,'origin')]",
                "(//input[@type='text'])[1]"
            ]
            
            origin_clicked = False
            for selector in origin_selectors:
                try:
                    print(f"🔍 Trying origin selector: {selector}")
                    origin_input = self.driver.find_element(By.XPATH, selector)
                    origin_input.click()
                    time.sleep(1)
                    origin_input.clear()
                    origin_input.send_keys(origin)
                    time.sleep(2)
                    origin_input.send_keys(Keys.ENTER)
                    print(f"✅ Successfully entered origin: {origin}")
                    origin_clicked = True
                    time.sleep(2)
                    break
                except Exception as e:
                    print(f"❌ Failed with selector {selector}: {str(e)}")
                    continue
            
            if not origin_clicked:
                print("⚠️ Could not find origin input field")
            
            # Try destination input
            dest_selectors = [
                "//input[@aria-label='Where to?']",
                "//input[@placeholder='Where to?']",
                "//input[contains(@aria-label,'destination')]",
                "(//input[@type='text'])[2]"
            ]
            
            dest_clicked = False
            for selector in dest_selectors:
                try:
                    print(f"🔍 Trying destination selector: {selector}")
                    dest_input = self.driver.find_element(By.XPATH, selector)
                    dest_input.click()
                    time.sleep(1)
                    dest_input.clear()
                    dest_input.send_keys(destination)
                    time.sleep(2)
                    dest_input.send_keys(Keys.ENTER)
                    print(f"✅ Successfully entered destination: {destination}")
                    dest_clicked = True
                    time.sleep(2)
                    break
                except:
                    continue
            
            if not dest_clicked:
                print("⚠️ Could not find destination input field")
            
            # Date selection
            date_selectors = [
                "//input[@placeholder='Departure']",
                "//input[contains(@aria-label,'Departure')]",
                "//div[contains(@aria-label,'Departure')]",
                "(//input[@type='text'])[3]"
            ]
            
            for selector in date_selectors:
                try:
                    print(f"🔍 Trying date selector: {selector}")
                    date_input = self.driver.find_element(By.XPATH, selector)
                    date_input.click()
                    print("✅ Clicked on date field")
                    time.sleep(1)
                    break
                except:
                    continue
            
            print("📅 Please manually select your departure date in the browser")
            print("⏰ You have 15 seconds to select the date and click Done...")
            time.sleep(15)
            
            # Click search button
            search_selectors = [
                "//button[contains(@aria-label,'Search')]",
                "//button[contains(text(),'Search')]",
                "//button[contains(@aria-label,'Done')]",
                "//button[contains(text(),'Done')]",
                "//button[@jsname='vLv7Lb']"
            ]
            
            for selector in search_selectors:
                try:
                    search_button = self.driver.find_element(By.XPATH, selector)
                    search_button.click()
                    print("✅ Clicked search/done button")
                    break
                except:
                    continue
            
            # Wait for results
            print("⌛ Waiting for results to load...")
            time.sleep(8)
            
            # Take a screenshot for debugging
            self.driver.save_screenshot("flight_results.png")
            print("📸 Screenshot saved as 'flight_results.png'")
            
            # Extract flight data
            flights = self.extract_flight_data()
            
            return {
                "status": "success",
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "flights_found": len(flights),
                "flights": flights
            }
            
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            # Take a screenshot on error
            self.driver.save_screenshot("error_screenshot.png")
            print("📸 Error screenshot saved as 'error_screenshot.png'")
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            print("🔄 Press Enter to close the browser...")
            input()  # This will pause before closing so you can see what happened
            self.close_driver()
    
    def extract_flight_data(self):
        """Extract flight information from the results page"""
        flights = []
        
        # Try multiple selectors for flight elements
        flight_selectors = [
            "//li[contains(@class,'pIav2d')]",
            "//div[@jscontroller='QyLbse']",
            "//div[contains(@class,'yR1fYc')]",
            "//div[@role='listitem']"
        ]
        
        flight_elements = []
        for selector in flight_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    flight_elements = elements
                    print(f"✅ Found {len(elements)} flights using selector: {selector}")
                    break
            except:
                continue
        
        if not flight_elements:
            print("❌ No flight elements found")
            return flights
        
        for i, flight in enumerate(flight_elements[:5]):
            try:
                flight_data = {"index": i + 1}
                
                # Try to extract price
                price_selectors = [
                    ".//span[contains(@aria-label,'dollars')]",
                    ".//span[contains(text(),'$')]",
                    ".//div[@class='FpEdX']//span"
                ]
                
                for selector in price_selectors:
                    try:
                        price = flight.find_element(By.XPATH, selector).text
                        if price:
                            flight_data["price"] = price
                            break
                    except:
                        continue
                
                # Try to extract duration
                duration_selectors = [
                    ".//div[contains(@class,'Ak5kof')]",
                    ".//div[contains(@aria-label,'Total duration')]",
                    ".//span[contains(text(),'hr')]"
                ]
                
                for selector in duration_selectors:
                    try:
                        duration = flight.find_element(By.XPATH, selector).text
                        if duration:
                            flight_data["duration"] = duration
                            break
                    except:
                        continue
                
                # Add timestamp
                flight_data["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if flight_data.get("price") or flight_data.get("duration"):
                    flights.append(flight_data)
                    print(f"✈️ Flight {i+1}: {flight_data}")
                    
            except Exception as e:
                print(f"⚠️ Error extracting flight {i+1}: {str(e)}")
                continue
        
        return flights

# Test the scraper
if __name__ == "__main__":
    scraper = GoogleFlightsScraper(headless=False)
    result = scraper.search_flights("JFK", "LAX", "2024-03-15")
    
    print("\n" + "="*50)
    print("SEARCH RESULTS:")
    print("="*50)