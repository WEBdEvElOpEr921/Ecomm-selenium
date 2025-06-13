# headless.py
import time
import os
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class HeadlessTest:
    def __init__(self):
        """Initialize headless test configuration"""
        self.base_url = "http://localhost:80800"
        self.setup_directories()
        self.setup_driver()
        self.test_status = []

    def setup_directories(self):
        """Setup directories for test results"""
        base_dir = Path(__file__).parent
        self.screenshots_dir = base_dir / "screenshots"
        self.success_screenshots_dir = self.screenshots_dir / "success"
        self.error_screenshots_dir = self.screenshots_dir / "error"
        self.reports_dir = base_dir / "reports"
        
        # Create all required directories
        self.success_screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.error_screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def setup_driver(self):
        """Setup Chrome in headless mode"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--disable-gpu")  # Required for headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # Set viewport size
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        print("✨ Headless Chrome initialized")

    def log_step(self, step_name, status, error=None):
        """Log test step with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_status.append({
            "timestamp": timestamp,
            "step": step_name,
            "status": status,
            "error": error
        })
        
        if status:
            print(f"[{timestamp}] ✅ {step_name}")
        else:
            print(f"[{timestamp}] ❌ {step_name}")
            if error:
                print(f"   Error: {error}")

    def save_report(self, is_success):
        """Save test report with screenshots"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        target_screenshots_dir = self.success_screenshots_dir if is_success else self.error_screenshots_dir
        
        # Save screenshot
        screenshot_path = target_screenshots_dir / f"{'success' if is_success else 'error'}_screenshot_{timestamp}.png"
        self.driver.save_screenshot(str(screenshot_path))
        
        # Generate report content
        report_lines = [
            "╔═══════════════════════════════════════════════════════",
            "║           StyleNest Headless Test Report              ",
            "╚═══════════════════════════════════════════════════════",
            "",
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"🌐 URL: {self.base_url}",
            f"📊 Status: {'✅ PASSED' if is_success else '❌ FAILED'}",
            "",
            "📋 Test Steps:",
            "------------"
        ]
        
        for entry in self.test_status:
            status_icon = "✅" if entry["status"] else "❌"
            report_lines.append(f"[{entry['timestamp']}] {status_icon} {entry['step']}")
            if entry.get("error"):
                report_lines.append(f"   ⚠️ {entry['error']}")
        
        # Save report in reports directory
        report_path = self.reports_dir / f"test_report_{timestamp}.txt"
        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        
        print(f"\n📄 Report saved: {report_path}")
        print(f"📸 Screenshot saved: {screenshot_path}")

    def run_test(self):
        """Run the e-commerce test flow"""
        try:
            # Step 1: Open homepage
            self.driver.get(self.base_url)
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            self.log_step("Opened homepage", True)

            # Step 2: Navigate to products
            if "/products" not in self.driver.current_url:
                shop_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@href, '/products')] | //button[contains(text(), 'Shop Now')]")
                ))
                shop_btn.click()
                self.log_step("Navigated to products page", True)

            # Step 3: Add product to cart
            add_to_cart_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(.,'Add to Cart') or .//span[contains(text(),'Add to Cart')]]")
            ))
            add_to_cart_btn.click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'added to cart')]")))
            self.log_step("Added product to cart", True)

            # Step 4: Go to cart
            cart_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/cart')]")))
            cart_link.click()
            self.wait.until(EC.url_contains("/cart"))
            self.log_step("Navigated to cart", True)

            # Step 5: Proceed to checkout
            checkout_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Proceed to Checkout')]")
            ))
            checkout_btn.click()
            self.wait.until(EC.url_contains("/checkout"))
            self.log_step("Proceeded to checkout", True)

            # Step 6: Fill checkout form
            self.wait.until(EC.presence_of_element_located((By.ID, "fullName"))).send_keys("Garvit Rawal")
            self.wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("garvit@example.com")
            self.wait.until(EC.presence_of_element_located((By.ID, "address"))).send_keys("Hostel 4, India")
            self.log_step("Filled checkout form", True)

            # Step 7: Select payment method
            upi_label = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//label[contains(.//text(), 'UPI')]")
            ))
            upi_label.click()
            self.log_step("Selected payment method", True)

            # Step 8: Place order
            place_order_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Place Order')]")
            ))
            place_order_btn.click()
            self.log_step("Placed order", True)

            # Step 9: Verify success
            self.wait.until(EC.url_contains("/order-success"))
            success_msg = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), 'Order Placed Successfully')]")
            ))
            assert success_msg.is_displayed(), "Success message not found"
            self.log_step("Order confirmed successfully", True)

            # Save successful test report
            self.save_report(True)
            print("\n✨ Test completed successfully!")

        except Exception as e:
            self.log_step("Test failed", False, str(e))
            self.save_report(False)
            print(f"\n❌ Test failed: {str(e)}")
            raise

        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()
                print("🔄 Browser closed")

if __name__ == "__main__":
    print("🚀 Starting headless test...")
    test = HeadlessTest()
    test.run_test()
