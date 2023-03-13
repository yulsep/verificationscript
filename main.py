import os
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from googletrans import Translator

from urls import urls


translator = Translator()


def is_menu_valid(driver):
    """
    Verifica que el menú se abra y cierre correctamente.
    """
    driver.find_element_by_css_selector('.menu-toggle').click()
    time.sleep(5)
    is_displayed = driver.find_element_by_css_selector('.menu-list').is_displayed()
    driver.find_element_by_css_selector('.close-menu').click()
    return is_displayed


def is_translation_valid(driver):
    """
    Verifica que la página esté completamente traducida al hindi.
    """
    hindi_text = translator.translate(driver.page_source, src='en', dest='hi').text
    return 'classcentral' not in hindi_text


def is_image_valid(image):
    """
    Verifica que la imagen tenga su resolución original y no esté borrosa.
    """
    if 'data:image' in image.get_attribute('src'):
        return True
    if not os.path.exists(image.get_attribute('src')):
        return False
    return image.size['height'] >= 100 and image.size['width'] >= 100


def is_page_valid(driver, url):
    """
    Verifica que las páginas internas estén completamente traducidas al hindi.
    """
    inner_links = driver.find_elements_by_css_selector('.card a')
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
    Verifica que el scroll funcione correctamente.
    """
    initial_height = driver.execute_script('return document.body.scrollHeight')
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(5)
    new_height = driver.execute_script('return document.body.scrollHeight')
    return new_height > initial_height

def check_all_pages(url):
    """
    Verifica las páginas internas de una URL.
    """
    # Inicializar el driver de Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Verificar el menú
    menu_valid = is_menu_valid(driver)

    # Verificar la traducción al hindi
    translation_valid = is_translation_valid(driver)

    # Verificar las imágenes
    images_valid = is_image_valid(driver)

    # Verificar el scroll
    scroll_valid = is_scroll_valid(driver)

    # Hacer clic en algunos enlaces interiores y verificar que funcionen
    is_internal_pages_valid = True
    inner_links = driver.find_elements_by_css_selector('.card a')
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

    # Cerrar el driver de Selenium
    driver.quit()

    # Determinar si la página pasa o falla en la verificación
    is_valid = menu_valid and translation_valid and images_valid and scroll_valid and is_internal_pages_valid
    result = "PASS" if is_valid else "FAIL"
    print(f"{url} - {result}")


for url in urls:
    check_all_pages(url)
