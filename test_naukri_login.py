from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.naukri.com/nlogin/login")
time.sleep(4)

# Print ALL input fields found on the page
inputs = driver.find_elements(By.TAG_NAME, "input")
print(f"\n Found {len(inputs)} input fields:")
for i, inp in enumerate(inputs):
    print(f"  [{i}] type={inp.get_attribute('type')} | "
          f"id={inp.get_attribute('id')} | "
          f"name={inp.get_attribute('name')} | "
          f"placeholder={inp.get_attribute('placeholder')}")

print("\n Page title:", driver.title)
print("\n Current URL:", driver.current_url)

input("\n>>> Press ENTER to close browser...")
driver.quit()
