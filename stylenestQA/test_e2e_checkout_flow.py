# test_e2e_checkout_flow.py

import time
import os
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_utils import TestStep, create_test_report
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# Define test steps
steps = [
    TestStep(1, "Open homepage and navigate to products"),
    TestStep(2, "Add product to cart"),
    TestStep(3, "Navigate to cart"),
    TestStep(4, "Proceed to checkout"),
    TestStep(5, "Fill checkout form"),
    TestStep(6, "Select payment method"),
    TestStep(7, "Place order"),
    TestStep(8, "Verify order success")
]

class RetryingWebDriverWait(WebDriverWait):
    def until(self, method, message=''):
        last_exception = None
        end_time = time.time() + self._timeout
        while True:
            try:
                value = method(self._driver)
                if value:
                    return value
            except Exception as exc:
                last_exception = exc
            time.sleep(0.5)
            if time.time() > end_time:
                break
        raise TimeoutException(message) from last_exception

def setup_driver():
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Set up Chrome with the latest driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Set up custom wait with retry logic
    wait = RetryingWebDriverWait(driver, timeout=15)
    return driver, wait

# Initialize driver and wait
driver, wait = setup_driver()

def safe_click(driver, element):
    """Ensure element is in view and clickable before clicking"""
    ActionChains(driver).move_to_element(element).perform()
    time.sleep(0.5)
    element.click()

def handle_test_failure(e, driver, steps):
    """Handle test failure gracefully and generate appropriate reports"""
    # Find the current step that failed (or last step if no in-progress step)
    try:
        current_step = next(step for step in steps if step.status == "🔄")
    except StopIteration:
        # If no step is in progress, mark the last incomplete step as failed
        try:
            current_step = next(step for step in reversed(steps) if step.status != "✅")
        except StopIteration:
            current_step = steps[-1]  # If all steps are complete, use the last step
    
    current_step.complete(False, str(e))
    
    # Take error screenshot in test_results/error directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    error_screenshot = Path(__file__).parent / "test_results" / "error" / f"error_screenshot_{timestamp}.png"
    error_screenshot.parent.mkdir(parents=True, exist_ok=True)
    
    if driver:
        driver.save_screenshot(str(error_screenshot))
        print(f"\n❌ Test Failed!")
        print(f"Error: {str(e)}")
    
    # Generate final report for failure
    report_path, new_screenshot = create_test_report(steps, False, str(e), str(error_screenshot))
    
    print(f"\nTest artifacts saved:")
    print(f"- Report: {report_path}")
    if new_screenshot:
        print(f"- Screenshot: {new_screenshot}")

try:
    # Step 1: Open homepage and wait for it to load
    steps[0].start()
    driver.get("http://localhost:8080/")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    
    # Navigate to products page if we're not there already
    if "/products" not in driver.current_url:
        products_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, '/products')] | //button[contains(text(), 'Shop Now')]")
        ))
        safe_click(driver, products_link)
    steps[0].complete()
    
    # Step 2: Add first product to cart
    steps[1].start()
    add_to_cart_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(.,'Add to Cart') or .//span[contains(text(),'Add to Cart')]]")
    ))
    safe_click(driver, add_to_cart_button)
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'added to cart')]")))
    steps[1].complete()

    # Step 3: Navigate to Cart
    steps[2].start()
    cart_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/cart')]")))
    safe_click(driver, cart_button)
    wait.until(EC.url_contains("/cart"))
    steps[2].complete()

    # Step 4: Proceed to Checkout
    steps[3].start()
    checkout_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Proceed to Checkout')]")
    ))
    safe_click(driver, checkout_button)
    wait.until(EC.url_contains("/checkout"))
    steps[3].complete()

    # Step 5: Fill checkout form
    steps[4].start()
    fullname_input = wait.until(EC.presence_of_element_located((By.ID, "fullName")))
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    address_input = wait.until(EC.presence_of_element_located((By.ID, "address")))

    fullname_input.clear()
    fullname_input.send_keys("Garvit Rawal")
    email_input.clear()
    email_input.send_keys("garvit@example.com")
    address_input.clear()
    address_input.send_keys("Hostel 4, India")
    steps[4].complete()
    
    # Step 6: Select payment method
    steps[5].start()
    upi_label = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//label[contains(.//text(), 'UPI')]")
    ))
    safe_click(driver, upi_label)
    steps[5].complete()

    # Step 7: Submit order
    steps[6].start()
    place_order_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Place Order')]")
    ))
    safe_click(driver, place_order_button)
    steps[6].complete()

    # Step 8: Validate success
    steps[7].start()
    wait.until(EC.url_contains("/order-success"))
    success_heading = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//h1[contains(text(), 'Order Placed Successfully')]")
    ))
    assert success_heading.is_displayed(), "❌ Order Success message not found!"
    steps[7].complete()
      # Take success screenshot in test_results/success directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    success_screenshot = Path(__file__).parent / "test_results" / "success" / f"success_screenshot_{timestamp}.png"
    success_screenshot.parent.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(success_screenshot))
    print(f"\n✅ Test Passed!")
    
    # Generate final report for success
    report_path, new_screenshot = create_test_report(steps, True, screenshot_path=str(success_screenshot))

except Exception as e:
    handle_test_failure(e, driver, steps)

finally:
    if driver:
        try:
            driver.quit()
        except Exception as quit_error:
            print(f"\n⚠️ Note: Browser cleanup encountered an issue (test results are still valid)")
            with open(Path(__file__).parent / "test_results" / "cleanup_warning.txt", "w") as f:
                f.write(f"Browser cleanup warning: {str(quit_error)}\n")
