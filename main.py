import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


# Regardless of where you are in the UK, by changing the postcode, the url will automatically change
# Because of the above, there is no need to change westminster

postcode = 'SW1A 2AA'
URL_PAGE = f'https://deliveroo.co.uk/restaurants/london/westminster?postcode={postcode}&collection=all-restaurants'

initial_load_time = 2
scroll_pause_time = 0.0001

driver = webdriver.Chrome()
driver.get(URL_PAGE)


time.sleep(initial_load_time)
screen_height = driver.execute_script('return window.screen.height;')
driver.execute_script('document.querySelector("#onetrust-reject-all-handler").click()')
driver.execute_script('document.querySelector(".ccl-388f3fb1d79d6a36.ccl-6d2d597727bd7bab.ccl-59eced23a4d9e077.ccl-7be8185d0a980278").click()')
driver.execute_script('document.querySelector(".ccl-388f3fb1d79d6a36.ccl-9ed29b91bb2d9d02.ccl-59eced23a4d9e077.ccl-7be8185d0a980278").click()')

i = 1
while True:
    driver.execute_script("window.scrollTo(0, {screen_height} * {i});".format(screen_height=screen_height, i = i))
    i += 1
    time.sleep(scroll_pause_time)
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    if screen_height * i > scroll_height:
        break


soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

a_tag_class = 'HomeFeedGrid-b0432362335be7af'

restaurants_html = [str(x) for x in soup.find_all(class_ = a_tag_class)]

print(restaurants_html[0])