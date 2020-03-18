import pytest
from selenium import webdriver


@pytest.fixture
def driver(request):
    wd = webdriver.Chrome()
    request.addfinalizer(wd.quit)
    return wd


def test_example(driver):
    driver.get("http://www.google.com/")


def test_login_litecart_admin(driver):
    driver.get("http://localhost/litecart/admin/")
    username_field = driver.find_element_by_name("username")
    username_field.send_keys("admin")
    password_field = driver.find_element_by_name("password")
    password_field.send_keys("admin")
    login_button = driver.find_element_by_name("login")
    login_button.click()
