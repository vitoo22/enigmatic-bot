from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


browser = webdriver.Firefox()
browser.get('https://www.instagram.com/accounts/login/')
time.sleep(3)

username = browser.find_element_by_xpath('/html/body/span/div/article/div/div[1]/div/form/div[1]/input')
password = browser.find_element_by_xpath('/html/body/span/div/article/div/div[1]/div/form/div[2]/input')

username.send_keys('vitoo22')
password.send_keys('Serginho27')

time.sleep(1)

to_click = WebDriverWait(browser, 10).until(
			EC.element_to_be_clickable((
				By.XPATH, '/html/body/span/div/article/div/div[1]/div/form/span/button')))

browser.click(to_click)

# browser.close()