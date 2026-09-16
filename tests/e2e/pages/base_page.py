from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_TIMEOUT = 10


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def open(self, path):
        self.driver.get(f"{self.base_url}{path}")
        return self

    def find(self, test_id, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'[data-testid="{test_id}"]')
            )
        )

    def find_clickable(self, test_id, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'[data-testid="{test_id}"]')
            )
        )

    def exists(self, test_id, timeout=3):
        try:
            self.find(test_id, timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_absent(self, test_id, timeout=DEFAULT_TIMEOUT):
        WebDriverWait(self.driver, timeout).until_not(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'[data-testid="{test_id}"]')
            )
        )

    def flash_messages(self):
        WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="flash-message"]')
            )
        )
        return [
            el.text
            for el in self.driver.find_elements(
                By.CSS_SELECTOR,
                '[data-testid="flash-message"]'
            )
        ]