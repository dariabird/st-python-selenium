import os
import pytest
import re
import time
import uuid

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


@pytest.fixture
def driver(request):
    chrome_driver = webdriver.Chrome()
    # firefox_driver = webdriver.Firefox(firefox_binary="/Applications/Firefox Nightly.app/Contents/MacOS/firefox")
    # safari_driver = webdriver.Safari()
    chrome_driver.implicitly_wait(5)
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


def wait_for_elements_present(driver, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located(locator))
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


def login_user(driver, login, password):
    driver.find_element_by_xpath('//input[@name="email"]').send_keys(login)
    driver.find_element_by_xpath('//input[@name="password"]').send_keys(password)
    driver.find_element_by_xpath('//button[@name="login"]').click()


def logout_user(driver):
    wait_for_element_present(driver, (By.XPATH, '//a[contains(.,"Logout")]')).click()


def create_unique_email():
    return str(uuid.uuid4()) + "@test.com"


def register_new_user(driver, email, tax_id="123", company="Test company", first_name="First",
                      last_name="Last name", address_1="Address 1", address_2="Address 2",
                      postcode="12345-6789", city="City", country="United States", state="Alaska",
                      phone="+71234567901", is_newsletter=True, desired_password="pass", confirm_password="pass"):
    driver.find_element_by_xpath('//a[contains(.,"New customers click here")]').click()
    wait_for_element_present(driver, (By.CSS_SELECTOR, "h1.title"))
    email_field = driver.find_element_by_xpath('//input[@name="email"]')
    tax_id_field = driver.find_element_by_xpath('//input[@name="tax_id"]')
    company_field = driver.find_element_by_xpath('//input[@name="company"]')
    first_name_field = driver.find_element_by_xpath('//input[@name="firstname"]')
    last_name_field = driver.find_element_by_xpath('//input[@name="lastname"]')
    address_1_field = driver.find_element_by_xpath('//input[@name="address1"]')
    address_2_field = driver.find_element_by_xpath('//input[@name="address2"]')
    postcode_field = driver.find_element_by_xpath('//input[@name="postcode"]')
    city_field = driver.find_element_by_xpath('//input[@name="city"]')
    country_field = Select(driver.find_element_by_xpath('//select[@name="country_code"]'))
    state_field = Select(driver.find_element_by_xpath('//select[@name="zone_code"]'))
    phone_field = driver.find_element_by_xpath('//input[@name="phone"]')
    newsletter_checkbox = driver.find_element_by_xpath('//input[@name="newsletter"]')
    desired_password_field = driver.find_element_by_xpath('//input[@name="password"]')
    confirm_password_field = driver.find_element_by_xpath('//input[@name="confirmed_password"]')
    create_account_btn = driver.find_element_by_xpath('//button[@name="create_account"]')

    tax_id_field.send_keys(tax_id)
    company_field.send_keys(company)
    first_name_field.send_keys(first_name)
    last_name_field.send_keys(last_name)
    address_1_field.send_keys(address_1)
    address_2_field.send_keys(address_2)
    postcode_field.send_keys(postcode)
    city_field.send_keys(city)
    country_field.select_by_visible_text(country)
    state_field.select_by_visible_text(state)
    email_field.send_keys(email)
    phone_field.send_keys(phone)
    desired_password_field.send_keys(desired_password)
    confirm_password_field.send_keys(confirm_password)
    newsletter_checkbox.click()
    create_account_btn.click()


# Задание 11. Сделайте сценарий регистрации пользователя
def test_register_new_user(driver):
    driver.get("http://localhost/litecart/en/")
    email = create_unique_email()
    password = "test"
    register_new_user(driver, email, desired_password=password, confirm_password=password)
    logout_user(driver)
    login_user(driver, email, password)
    logout_user(driver)


def open_add_new_product_page(driver):
    catalog_menu_item = wait_for_element_present(driver, (By.XPATH, '//li[@id="app-"]/a[contains(.,"Catalog")]'))
    time.sleep(1)
    catalog_menu_item.click()
    add_new_product_btn = driver.find_element_by_xpath('//a[contains(.,"Add New Product")]')
    add_new_product_btn.click()
    wait_for_element_present(driver, (By.XPATH, '//h1[contains(.,"Add New Product")]")'))


def fill_in_product_general_info(driver, image_path, status="Enabled", name="Pink Dotted", code="12345",
                                 categories=["Root", "Rubber Ducks"], default_category="Rubber Ducks",
                                 product_groups=["Unisex"], quantity=4,
                                 quantity_unit="pcs", delivery_status="3-5 days",
                                 sold_out_status="Temporary sold out", date_valid_from="12.02.2020",
                                 date_valid_to="12.06.2020"):
    general_info_tab = driver.find_element_by_xpath('//a[contains(.,"General")]')
    general_info_tab.click()
    time.sleep(1)
    if status == "Enabled":
        status_radio_btn = driver.find_element_by_xpath('//input[@type="radio" and @value=1]')
    else:
        status_radio_btn = driver.find_element_by_xpath('//input[@type="radio" and @value=0]')
    status_radio_btn.click()

    name_field = driver.find_element_by_css_selector('input[name^=name]')
    name_field.send_keys(name)

    code_field = driver.find_element_by_name('code')
    code_field.send_keys(code)

    for category in categories:
        category_checkbox = driver.find_element_by_css_selector('input[data-name="{}"]'.format(category))
        if category_checkbox.is_selected():
            pass
        else:
            category_checkbox.click()

    default_categories_select = Select(driver.find_element_by_name('default_category_id'))
    default_categories_select.select_by_visible_text(default_category)

    for product_group in product_groups:
        product_group_el = driver.find_element_by_xpath('//input[@name="product_groups[]"]/../../td[contains(.,"{}")]'
                                                        .format(product_group))
        product_group_el.find_element_by_xpath("./../td/input").click()

    quantity_field = driver.find_element_by_name("quantity")
    driver.execute_script("arguments[0].value=arguments[1]", quantity_field, str(quantity))

    quantity_units_select = Select(driver.find_element_by_name("quantity_unit_id"))
    quantity_units_select.select_by_visible_text(quantity_unit)

    delivery_status_select = Select(driver.find_element_by_name("delivery_status_id"))
    delivery_status_select.select_by_visible_text(delivery_status)

    sold_out_status_select = Select(driver.find_element_by_name("sold_out_status_id"))
    sold_out_status_select.select_by_visible_text(sold_out_status)

    image_field = driver.find_element_by_name("new_images[]")
    image_field.send_keys(image_path)

    date_valid_from_field = driver.find_element_by_name("date_valid_from")
    date_valid_from_field.send_keys(date_valid_from)
    date_valid_to_field = driver.find_element_by_name("date_valid_to")
    date_valid_to_field.send_keys(date_valid_to)


def fill_in_product_information(driver, manufacturer="ACME Corp.", keywords="dots", short_descrition="Pink Dotted Duck",
                                description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                                            "Phasellus id convallis ipsum. Quisque viverra urna a massa facilisis, "
                                            "nec blandit dolor tempor.", head_title="Pink",
                                meta_description="Pink rubber duck with dots"):
    info_tab = driver.find_element_by_xpath('//a[contains(.,"Information")]')
    info_tab.click()
    time.sleep(2)
    manufacturer_select = Select(driver.find_element_by_name("manufacturer_id"))
    manufacturer_select.select_by_visible_text(manufacturer)
    keywords_field = driver.find_element_by_name("keywords")
    keywords_field.send_keys(keywords)
    short_description_field = driver.find_element_by_css_selector("[name^=short_description]")
    short_description_field.send_keys(short_descrition)
    description_field = driver.find_element_by_css_selector(".trumbowyg-editor")
    driver.execute_script("arguments[0].innerText=arguments[1]", description_field, description)
    description_field.send_keys(description)
    head_title_field = driver.find_element_by_css_selector("[name^=head_title]")
    head_title_field.send_keys(head_title)
    meta_description_field = driver.find_element_by_css_selector("[name^=meta_description]")
    meta_description_field.send_keys(meta_description)


def fill_in_product_prices(driver, purchase_price=5, currency="Euros",
                           price_usd=10, price_usd_tax=12,
                           price_euro=9, price_euro_tax=10):
    prices_tab = driver.find_element_by_xpath('//a[contains(.,"Prices")]')
    prices_tab.click()
    purchase_price_field = driver.find_element_by_name("purchase_price")
    driver.execute_script("arguments[0].value=arguments[1]", purchase_price_field, str(purchase_price))
    currency_select=Select(driver.find_element_by_name("purchase_price_currency_code"))
    currency_select.select_by_visible_text(currency)
    price_usd_field = driver.find_element_by_name("prices[USD]")
    price_usd_field.send_keys(str(price_usd))
    price_usd_tax_field = driver.find_element_by_name("gross_prices[USD]")
    driver.execute_script("arguments[0].value=arguments[1]", price_usd_tax_field, str(price_usd_tax))
    price_euro_field = driver.find_element_by_name("prices[EUR]")
    price_euro_field.send_keys(str(price_euro))
    price_euro_tax_field = driver.find_element_by_name("gross_prices[EUR]")
    driver.execute_script("arguments[0].value=arguments[1]", price_euro_tax_field, str(price_euro_tax))


def login_admin(driver, login="admin", password="admin"):
    login_field = driver.find_element_by_name("username")
    login_field.send_keys(login)
    password_field = driver.find_element_by_name("password")
    password_field.send_keys(password)
    login_button = driver.find_element_by_name("login")
    login_button.click()


def save_product(driver):
    driver.find_element_by_name("save").click()


def is_product_appeared(driver, product_name="Pink Dotted"):
    product_rows = driver.find_elements_by_css_selector(".dataTable .row")
    for product_row in product_rows:
        if product_name in product_row.text:
            return True
    return False


# Задание 12. Сделайте сценарий добавления товара
def test_add_new_product(driver):
    driver.get("http://localhost/litecart/admin/")
    login_admin(driver)
    open_add_new_product_page(driver)
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "duck.jpg")
    product_name = "Super Pink Dotted"
    fill_in_product_general_info(driver, image_path, name=product_name)
    fill_in_product_information(driver)
    fill_in_product_prices(driver)
    save_product(driver)
    assert is_product_appeared(driver, product_name=product_name)


class is_text_of_element_changed(object):
    def __init__(self, locator, text):
        self.locator = locator
        self.text = text

    def __call__(self, driver):
        actual_text = driver.find_element(*self.locator).text
        return actual_text != self.text


def add_first_product_to_cart(driver):
    products = driver.find_elements_by_css_selector('ul.products li')
    time.sleep(1)
    products[0].click()
    add_to_cart_button = wait_for_element_present(driver, (By.NAME, "add_cart_product"))
    if is_element_present(driver, By.CSS_SELECTOR, 'select[name="options[Size]"]'):
        size_selector = Select(driver.find_element_by_css_selector('select[name="options[Size]"]'))
        size_selector.select_by_index(1)
    cart_counter_text = driver.find_element_by_css_selector('a.content').text
    add_to_cart_button.click()
    WebDriverWait(driver, 10).until(is_text_of_element_changed((By.CSS_SELECTOR, 'a.content'), cart_counter_text))


def go_home(driver):
    driver.find_element_by_css_selector('i[title=Home]').click()
    wait_for_element_present(driver, (By.XPATH, '//h3[contains(.,"Most Popular")]'))


def go_to_cart(driver):
    driver.find_element_by_xpath('//a[contains(., "Checkout")]').click()
    wait_for_element_present(driver, (By.XPATH, '//h2[contains(.,"Order Summary")]'))


def delete_product_from_cart(driver):
    if are_elements_present(driver, By.CSS_SELECTOR, 'ul.shortcuts li'):
        shortcut = driver.find_element_by_css_selector('ul.shortcuts li a')
        time.sleep(1)
        shortcut.click()
    if is_element_present(driver, By.CSS_SELECTOR, 'button[name="remove_cart_item"]'):
        order_summary = driver.find_element_by_id("box-checkout-summary")
        remove_button = driver.find_element_by_css_selector('button[name="remove_cart_item"]')
        remove_button.click()
        WebDriverWait(driver, 10).until(EC.staleness_of(order_summary))


# Задание 13. Сделайте сценарий работы с корзиной
def test_work_with_cart(driver):
    driver.get("http://localhost/litecart/en/")
    add_first_product_to_cart(driver)
    go_home(driver)
    add_first_product_to_cart(driver)
    go_home(driver)
    add_first_product_to_cart(driver)
    go_to_cart(driver)
    delete_product_from_cart(driver)
    delete_product_from_cart(driver)
    delete_product_from_cart(driver)
