import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


@pytest.fixture
def driver(request):
    chrome_driver = webdriver.Chrome()
    chrome_driver.implicitly_wait(10)
    # firefox_driver = webdriver.Firefox(firefox_binary="/Applications/Firefox Nightly.app/Contents/MacOS/firefox")
    # safari_driver = webdriver.Safari()
    request.addfinalizer(chrome_driver.quit)
    return chrome_driver


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


def is_element_present(driver, *args):
    try:
        driver.find_element(*args)
        return True
    except NoSuchElementException:
        return False


def are_elements_present(driver, *args):
    return len(driver.find_elements(*args)) > 0


def wait_for_element_present(driver, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
    except TimeoutException:
        return None


# Задание 7. Сделайте сценарий, проходящий по всем разделам админки
def test_click_all_menu_items(driver):
    driver.get("http://localhost/litecart/admin/")
    username_field = driver.find_element_by_name("username")
    username_field.send_keys("admin")
    password_field = driver.find_element_by_name("password")
    password_field.send_keys("admin")
    login_button = driver.find_element_by_name("login")
    login_button.click()
    wait_for_element_present(driver, (By.XPATH, '//*[@id="box-apps-menu"]'))  # ждем появления бокового меню
    left_menu = driver.find_elements_by_xpath('//li[@id="app-"]')  # получаем список элементов бокового меню
    left_menu_len = len(left_menu)
    if left_menu_len > 0:
        for i in range(1, left_menu_len+1):
            left_menu_item_locator = '//li[@id="app-"][{}]'.format(i)  # локатор очередного пункта меню верхнего уровня
            left_menu_item = wait_for_element_present(driver, (By.XPATH, left_menu_item_locator))  # получаем соотвествующий элемент
            left_menu_item.click()
            submenu_locator = left_menu_item_locator + '/ul'
            submenu = wait_for_element_present(driver, (By.XPATH, submenu_locator))  # ждем появления подменю у пункта меню верхнего уровня
            if submenu:  # если подменю есть
                submenu_items_locator = submenu_locator + "/li"  # локатор для пункта подменю
                submenu_items_len = len(driver.find_elements_by_xpath(submenu_items_locator))
                for j in range(1, submenu_items_len+1):
                    submenu_item_locator = submenu_items_locator + "[{}]".format(j)  # локатор очередного пункта подменю
                    submenu_item = wait_for_element_present(driver, (By.XPATH, submenu_item_locator))  # получаем соответствующий пункт подменю
                    submenu_item.click()
                    assert is_element_present(driver, By.CSS_SELECTOR, "h1"), "No h1-header on the page"
            else:
                assert is_element_present(driver, By.CSS_SELECTOR, "h1"), "No h1-header on the page"


# Задание 8. Сделайте сценарий, проверяющий наличие стикеров у товаров
def test_one_sticker_for_each_product(driver):
    driver.get("http://localhost/litecart/")
    products = driver.find_elements_by_css_selector('li.product')
    for product in products:
        stickers = product.find_elements_by_css_selector('div.sticker')
        assert len(stickers) == 1, "Product has more than 1 sticker on it."
