import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re


@pytest.fixture
def driver(request):
    chrome_driver = webdriver.Chrome()
    # firefox_driver = webdriver.Firefox(firefox_binary="/Applications/Firefox Nightly.app/Contents/MacOS/firefox")
    # safari_driver = webdriver.Safari()
    chrome_driver.implicitly_wait(10)
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


def is_alphabet_order(my_list):
    for i in range(len(my_list)-1):
        if my_list[i] > my_list[i+1]:
            return False
    return True


# Задание 9. Проверить сортировку стран и геозон в админке
def test_countries_alphabet_sorted(driver):
    driver.get("http://localhost/litecart/admin/?app=countries&doc=countries")
    username_field = driver.find_element_by_name("username")
    username_field.send_keys("admin")
    password_field = driver.find_element_by_name("password")
    password_field.send_keys("admin")
    login_button = driver.find_element_by_name("login")
    login_button.click()
    rows = driver.find_elements_by_xpath('//table[@class="dataTable"]//tr')
    countries = []
    countries_to_check = []
    for i in range(2, len(rows)):
        country = driver.find_element_by_xpath('//table[@class="dataTable"]//tr[{}]/td[5]'.format(i)).text
        countries.append(country)
        zones_num = int(driver.find_element_by_xpath('//table[@class="dataTable"]//tr[{}]/td[6]'.format(i)).text)
        if zones_num > 0:
            countries_to_check.append(country)
    assert is_alphabet_order(countries)
    for country in countries_to_check:
        link = driver.\
            find_element_by_xpath('//table[@class="dataTable"]//td[contains(.,"{}")]/a'.format(country))\
            .get_attribute("href")
        driver.get(link)
        zones_cells = driver.find_elements_by_xpath('//table[@id="table-zones"]//td[3]')
        zones = []
        for i in range(len(zones_cells)-1):
            zones.append(zones_cells[i].text)
        assert is_alphabet_order(zones)
        driver.back()


# Задание 9. Проверить сортировку стран и геозон в админке
def test_geo_zones(driver):
    driver.get("http://localhost/litecart/admin/?app=geo_zones&doc=geo_zones")
    username_field = driver.find_element_by_name("username")
    username_field.send_keys("admin")
    password_field = driver.find_element_by_name("password")
    password_field.send_keys("admin")
    login_button = driver.find_element_by_name("login")
    login_button.click()
    country_cells = driver.find_elements_by_xpath('//table[@class="dataTable"]//td[3]')
    links = []
    for country_cell in country_cells:
        links.append(country_cell.find_element_by_xpath('./a').get_attribute("href"))
    for link in links:
        driver.get(link)
        zone_cells = driver.find_elements_by_xpath('//table[@id="table-zones"]//td[3]//*[@selected="selected"]')
        zones = []
        for zone_cell in zone_cells:
            zones.append(zone_cell.text)
        assert is_alphabet_order(zones)
        driver.back()


def parse_color(color):
    f = re.findall(r"\((.+)\)", color)
    return [int(x) for x in f[0].split(",")]


def get_price_properties(css_locator, product):
    price = product.find_element_by_css_selector(css_locator)
    price_num = int(price.text[1:])
    price_color = price.value_of_css_property("color")
    colors = parse_color(price_color)
    price_decoration = price.value_of_css_property("text-decoration").split(" ")[0]
    price_font_weight = price.value_of_css_property("font-weight")
    return price_num, colors, price_decoration, price_font_weight


# Задание 10. Проверить, что открывается правильная страница товара
def test_compare_product_data(driver):
    driver.get("http://localhost/litecart/")
    product = driver.find_element_by_css_selector("div#box-campaigns li.product")
    link = product.find_element_by_css_selector("a").get_attribute("href")
    title = product.find_element_by_css_selector("div.name").text
    regular_price_num, colors, decoration, _ = get_price_properties("s.regular-price", product)
    assert colors[0] == colors[1] and colors[1] == colors[2]
    assert decoration == 'line-through'

    campaign_price_num, colors, _, font_weight = get_price_properties("strong.campaign-price", product)
    assert colors[0] != 0 and colors[1] == 0 and colors[2] == 0
    assert font_weight in ("700", "900", "bold")

    assert regular_price_num > campaign_price_num

    driver.get(link)
    actual_title = driver.find_element_by_css_selector("h1").text
    assert title == actual_title

    actual_regular_price_num, colors, decoration, _ = get_price_properties("s.regular-price", driver)
    assert colors[0] == colors[1] and colors[1] == colors[2]
    assert decoration == 'line-through'

    actual_campaign_price_num, colors, _, font_weight = get_price_properties("strong.campaign-price", driver)
    assert colors[0] != 0 and colors[1] == 0 and colors[2] == 0
    assert font_weight in ("700", "900", "bold")

    assert actual_regular_price_num > actual_campaign_price_num
    assert actual_regular_price_num == regular_price_num
    assert actual_campaign_price_num == campaign_price_num
