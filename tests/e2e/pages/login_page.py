from selenium.webdriver.support.ui import WebDriverWait

from tests.e2e.pages.base_page import (
    BasePage,
    DEFAULT_TIMEOUT,
)


class LoginPage(BasePage):
    def open_login(self):
        self.open("/login")
        return self

    def login(self, username, password):
        self.find("username-input").send_keys(username)
        self.find("password-input").send_keys(password)
        self.find_clickable("login-submit").click()

        WebDriverWait(
            self.driver,
            DEFAULT_TIMEOUT,
        ).until(
            lambda driver: "/dashboard" in driver.current_url
        )

        return self


class RegisterPage(BasePage):
    def open_register(self):
        self.open("/register")
        return self

    def register(self, username, password):
        self.find("username-input").send_keys(username)
        self.find("password-input").send_keys(password)
        self.find_clickable("register-submit").click()
        return self