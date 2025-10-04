from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

def test_selenium():
    """Test if Selenium and ChromeDriver are working"""
    try:
        # Initialize Chrome driver
        service = Service('./chromedriver.exe')
        driver = webdriver.Chrome(service=service)
        
        # Navigate to Google
        driver.get("https://www.google.com")
        print("✅ Successfully opened Google")
        
        # Wait a moment
        time.sleep(2)
        
        # Close browser
        driver.quit()
        print("✅ Browser closed successfully")
        print("\n🎉 Setup is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Chrome is installed")
        print("2. Check ChromeDriver version matches Chrome version")
        print("3. Ensure ChromeDriver is in PATH or specify path in Service()")

if __name__ == "__main__":
    test_selenium()