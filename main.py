import json
import time
from selenium import webdriver
from bs4 import BeautifulSoup


# Regardless of where you are in the UK, by changing the postcode, the url will automatically change
# Because of the above, there is no need to change westminster

postcode = 'SW1A 2AA'
BASE_URL = f'https://deliveroo.co.uk'
MAIN_PAGE = f'/restaurants/london/westminster?postcode={postcode}&collection=all-restaurants'

DENY_COOKIES_BUTTON_ID =  '#onetrust-reject-all-handler'
ACCEPT_COUPON_BUTTON_CLASS = '.ccl-388f3fb1d79d6a36.ccl-6d2d597727bd7bab.ccl-59eced23a4d9e077.ccl-7be8185d0a980278'

RESTAURANT_TAG_CLASS = 'HomeFeedGrid-b0432362335be7af'
RATING_TAG_CLASS = 'css-87fssf'
HREF_TAG_CLASS = 'css-1hms87c'

INFO_BUTTON_TAG_CLASS = '.ccl-4704108cacc54616.ccl-4f99b5950ce94015.ccl-724e464f2f033893'

initial_load_time = 3
scroll_pause_time = 0.0001


def enter_restaurant_page(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(initial_load_time)

    driver.execute_script('document.querySelector(\"' + DENY_COOKIES_BUTTON_ID + '\").click()')
    driver.execute_script('document.querySelector(\"' + INFO_BUTTON_TAG_CLASS + '\").click()')

    driver.quit()

driver = webdriver.Chrome()
driver.get(BASE_URL + MAIN_PAGE)


time.sleep(initial_load_time)
screen_height = driver.execute_script('return window.screen.height;')
#Click on deny cookies
driver.execute_script('document.querySelector(\"' + DENY_COOKIES_BUTTON_ID + '\").click()')
#Click on accept coupon
driver.execute_script('document.querySelector(\"' + ACCEPT_COUPON_BUTTON_CLASS + '\").click()')

#Scroll to the end of the page, this makes all restaurants available load
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

data = []
for restaurant in soup.find_all(class_ = RESTAURANT_TAG_CLASS):
    rating = restaurant.find(class_ = RATING_TAG_CLASS)

    if rating == None:
        #Skip iteration
        continue
    if rating.text == 'New on Deliveroo':
        print(restaurant.prettify())
        restaurantDetail = restaurant.find(class_ = HREF_TAG_CLASS)
        enter_restaurant_page(BASE_URL + restaurantDetail['href'])
        #TODO: ENTRAR A PAGINA WEB ESPECIFICA DE RESTAURANTE (DELIVEROO) Y SACAR LA INFO POSTEADA
        #TODO: INVESTIGAR COMO CREAR OBJETO JSON Y DUMPEAR INFO NECESARIA
    
    
    
with open('output.json', 'w') as file:
    json.dump(data, file, indent=4)



#new_restaurants = []

#for restaurant in restaurants_html:
    #rating = restaurant.find('span', attrs={'class': 'ccl-649204f2a8e630fd ccl-6f43f9bb8ff2d712'}).text.strip()
    #if rating == "New on Deliveroo":
        #new_restaurants.append(rating)

#print(new_restaurants)