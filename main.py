import json
import time
from selenium import webdriver
from bs4 import BeautifulSoup


# Regardless of where you are in the UK, by changing the postcode, the url will automatically change
# Because of the above, there is no need to change westminster

postcode = 'SW1A 2AA'
URL_PAGE = f'https://deliveroo.co.uk/restaurants/london/westminster?postcode={postcode}&collection=all-restaurants'

RESTAURANT_TAG_CLASS = 'HomeFeedGrid-b0432362335be7af'
RATING_TAG_CLASS = 'css-87fssf'

initial_load_time = 2
scroll_pause_time = 0.0001

driver = webdriver.Chrome()
driver.get(URL_PAGE)


time.sleep(initial_load_time)
screen_height = driver.execute_script('return window.screen.height;')
#Click on deny cookies
driver.execute_script('document.querySelector("#onetrust-reject-all-handler").click()')
#Click on accept coupon
driver.execute_script('document.querySelector(".ccl-388f3fb1d79d6a36.ccl-6d2d597727bd7bab.ccl-59eced23a4d9e077.ccl-7be8185d0a980278").click()')

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