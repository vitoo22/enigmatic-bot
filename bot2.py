import os
from selenium import webdriver

# opts = webdriver.ChromeOptions()
# opts.binary_location(value = "/Applications/browsers")
driver = webdriver.Chrome(chrome_options=opts)
driver.get("http://www.instagram.com")
driver.close()