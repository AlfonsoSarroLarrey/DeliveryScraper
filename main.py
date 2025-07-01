from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

URL_PAGE = "https://deliveroo.co.uk/"

driver = webdriver.Chrome()
driver.get()