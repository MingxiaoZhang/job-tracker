"""
Check where regular Selenium finds Chrome.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

print("="*80)
print("Checking Chrome location for regular Selenium")
print("="*80 + "\n")

try:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=chrome_options)

    # Get the binary location
    print("✅ Regular Selenium Chrome works!")

    # Try to get capabilities
    caps = driver.capabilities
    print(f"\nChrome version: {caps.get('browserVersion', 'Unknown')}")
    print(f"Chrome driver version: {caps.get('chrome', {}).get('chromedriverVersion', 'Unknown')}")

    # Check binary location from service
    if hasattr(driver.service, 'path'):
        print(f"ChromeDriver path: {driver.service.path}")

    driver.quit()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
