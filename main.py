import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os
import requests
# import pygame


# pygame.init()

def get_paid_status(domain):
    base_url = 'http://13.233.93.191:5000/'
    data = {'url': domain}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(base_url, data=data, headers=headers)
    if response.json()['result'] == "PAID":
        print(f"{domain} - PAID")
        return True
    else:
        print(f"{domain} - UNPAID")
        return False

print("""
======================
        CPPST
======================
""")
# Login
url = 'http://copypaste.onlineurlservices.in/Account/Login?ReturnUrl=%2F'
username = input('Enter username: ')
password = input('Enter password: ')
# username = 'ssmg1'
# password = 'ssmg1@01'

# Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.get(url)

# auto login
driver.find_element(By.ID,'Email').send_keys(username)
driver.find_element(By.NAME,'Password').send_keys(password)
driver.find_element(By.XPATH, '//input[@type="submit" and @value="Log in"]').click()

time.sleep(5)

while True:
    time.sleep(10)
    try:
        iframe_src_url = driver.find_element(By.ID, "div_iframe").get_attribute("src")
    except Exception as e:
        print(f"Error: {e}") 
        continue

    try:
        answer = get_paid_status(iframe_src_url)
    except:
        answer = False

    if answer:
        os.system('mpv ~/copypaste/paid.mp3')
        # pygame.mixer.Sound('paid.mp3').play()
        input("Press Enter to continue...")  # Wait for user to press Enter
        continue

    Select(driver.find_element(By.XPATH, "//select[@id='status']")).select_by_index(2)

    try:
        driver.find_element(By.XPATH, '//button[span[text()="Ok"]]').click()
    except Exception as e:
        print(f"error: {e}")
        input("Reset State")

    # not by mistake
    time.sleep(6)
    try:
        driver.find_element(By.XPATH, '//button[span[text()="Ok"]]').click()
    except Exception as e:
        print(f"error: {e}")
        input("Reset State")
