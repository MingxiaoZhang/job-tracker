"""
Debug undetected-chromedriver configuration issues.
"""
import undetected_chromedriver as uc
import traceback

print("="*80)
print("Debugging undetected-chromedriver setup")
print("="*80 + "\n")

# Try to see what's going wrong
try:
    print("Attempt 1: Default configuration...")
    driver = uc.Chrome()
    print("✅ SUCCESS with default config!")
    print(f"Driver created: {driver}")
    driver.quit()
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*80 + "\n")

# Try with explicit headless
try:
    print("Attempt 2: With headless=True...")
    driver = uc.Chrome(headless=True)
    print("✅ SUCCESS with headless!")
    driver.quit()
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*80 + "\n")

# Try with options
try:
    print("Attempt 3: With ChromeOptions...")
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    print("✅ SUCCESS with options!")
    driver.quit()
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*80)
print("Debug complete")
print("="*80)
