# file: selenium_test_login.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

@pytest.fixture
def driver():
    # Thiết lập WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    yield driver
    # Đóng trình duyệt sau khi test xong
    driver.quit()

def test_login_successful(driver):
    """Test case: Đăng nhập thành công."""
    # Thay 'path/to/your/login.html' bằng đường dẫn thực tế
    driver.get("file:///path/to/your/login.html") 
    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("password123")
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(1) # Chờ trang phản hồi
    # Giả sử sau khi login thành công, sẽ có một thẻ h1 với id 'welcome-message'
    message = driver.find_element(By.ID, "welcome-message").text
    assert "Welcome" in message

def test_login_failed(driver):
    """Test case: Đăng nhập thất bại do sai thông tin."""
    driver.get("file:///path/to/your/login.html")
    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("wrongpassword")
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(1)
    # Giả sử có một thẻ p với id 'error-message' hiển thị lỗi
    error_message = driver.find_element(By.ID, "error-message").text
    assert "Invalid username or password" in error_message

def test_login_empty_input(driver):
    """Test case: Để trống input."""
    driver.get("file:///path/to/your/login.html")
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(1)
    error_message = driver.find_element(By.ID, "error-message").text
    assert "Username and password are required" in error_message