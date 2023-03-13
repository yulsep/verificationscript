import os
import time

from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from urls import urls

translator = Translator()


def is_menu_valid(driver):
    """
    Verify that the menu opens and closes correctly.
    """
    driver.find_element(By.CSS_SELECTOR, 'main-nav-dropdown').over()
    time.sleep(5)
    is_displayed = driver.find_element('main-nav-dropdown').is_displayed()
    driver.find_element('main-nav-dropdown').click()
    return is_displayed


def is_translation_valid(driver):
    """
    Verify that the page is fully translated into Hindi.
    """
    hindi_text = translator.translate(driver.page_source, src='en', dest='hi').text
    return 'classcentral' not in hindi_text


def is_image_valid(image):
    """
    Verify that the image has its original resolution and is not blurred.
    """
    if 'data:image' in image.get_attribute('src'):
        return True
    if not os.path.exists(image.get_attribute('src')):
        return False
    return image.size['height'] >= 100 and image.size['width'] >= 100


def is_page_valid(driver, url):
    """
    Verify that internal pages are fully translated into Hindi.
    """
    inner_links = driver.find_element('a button')
    for i in range(min(5, len(inner_links))):
        inner_links[i].send_keys(Keys.CONTROL + Keys.RETURN)
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])
        hindi_valid = is_translation_valid(driver)
        if not hindi_valid:
            print(f'{url}: La página interna {driver.current_url} no está completamente traducida al hindi')
            driver.quit()
            return False
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    return True


def is_scroll_valid(driver):
    """
    Verify that the scroll is working properly.
    """
    initial_height = driver.execute_script('return document.body.scrollHeight')
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(5)
    new_height = driver.execute_script('return document.body.scrollHeight')
    return new_height > initial_height


def check_all_pages(url):
    """
    Checks the internal pages of a URL.
    """
    # Initializing the Selenium driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    service = Service('F:\Cursos\selenium-server-4.8.1')
    driver = webdriver.Chrome(service=service)
    driver.get(url)

    menu_valid = is_menu_valid(driver)

    translation_valid = is_translation_valid(driver)

    images_valid = is_image_valid(driver)

    scroll_valid = is_scroll_valid(driver)

    # Click on some interior links and verify that they work.
    is_internal_pages_valid = True
    inner_links = driver.find_element('.card a')
    for i in range(min(5, len(inner_links))):
        inner_links[i].send_keys(Keys.CONTROL + Keys.RETURN)
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])
        hindi_text = translator.translate(driver.page_source, src='en', dest='hi').text
        if 'classcentral' not in hindi_text:
            print(f'{url}: La página interna {driver.current_url} no está completamente traducida al hindi')
            is_internal_pages_valid = False
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    # Close Selenium driver
    driver.quit()

    # Determine if the page passes or fails verification
    is_valid = menu_valid and translation_valid and images_valid and scroll_valid and is_internal_pages_valid
    result = "PASS" if is_valid else "FAIL"
    print(f"{url} - {result}")


for url in urls:
    check_all_pages(url)
