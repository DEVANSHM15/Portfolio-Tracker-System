import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import signal
import sys
import os

@pytest.fixture(scope="module")
def flask_app():
    # Start the Flask app in a subprocess
    env = os.environ.copy()
    env["FLASK_ENV"] = "testing"
    proc = subprocess.Popen([sys.executable, "app.py"], env=env)
    time.sleep(3)  # Wait for the server to start
    yield
    # Teardown: terminate the Flask app
    proc.terminate()
    proc.wait()

@pytest.fixture(scope="module")
def driver(flask_app):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_register_login_logout(driver):
    driver.get("http://localhost:5000/register")
    time.sleep(1)
    driver.find_element(By.NAME, "name").send_keys("E2E User")
    driver.find_element(By.NAME, "email").send_keys("e2euser@rvu.edu.in")
    driver.find_element(By.NAME, "password").send_keys("password123")
    driver.find_element(By.NAME, "role").send_keys("student")
    driver.find_element(By.NAME, "usn").send_keys("1RVU23CSE999")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)
    assert "Please login" in driver.page_source or "Login" in driver.page_source

    driver.get("http://localhost:5000/login")
    time.sleep(1)
    driver.find_element(By.NAME, "email").send_keys("e2euser@rvu.edu.in")
    driver.find_element(By.NAME, "password").send_keys("password123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)
    assert "Logout" in driver.page_source or "logged in" in driver.page_source

    driver.get("http://localhost:5000/logout")
    time.sleep(1)
    assert "You have been logged out" in driver.page_source or "Login" in driver.page_source
