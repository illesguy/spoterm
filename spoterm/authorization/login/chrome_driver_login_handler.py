from spoterm.authorization.login.login_handler import LoginHandler


class ChromeDriverLoginHandler(LoginHandler):

    def __init__(self, chrome_driver_path: str) -> None:
        self.chrome_driver_path = chrome_driver_path

    def login(self, login_url: str, redirect_uri: str) -> str:
        from selenium import webdriver
        from selenium.webdriver.support.ui import WebDriverWait

        with webdriver.Chrome(self.chrome_driver_path) as driver:
            wait = WebDriverWait(driver, 20)
            driver.get(login_url)
            wait.until(lambda d: d.current_url.startswith(redirect_uri))
            return driver.current_url
