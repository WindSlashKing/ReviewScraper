from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os

def main():
    class Scraper:
        def __init__(self, headless: bool):
            # Make browser headless
            service = Service(ChromeDriverManager().install())    
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('headless')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--allow-running-insecure-content')
                options.add_argument("--disable-extensions")
                options.add_argument("--start-maximized")
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--no-sandbox')

            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            self.browser = webdriver.Chrome(service=service, options=options, service_log_path='NUL')


        def close_cookies_popup(self):
            try:
                buttons = self.browser.find_elements(By.CLASS_NAME, 'VfPpkd-dgl2Hf-ppHlrf-sM5MNb')
                for button in buttons:
                    if "Приемане" in button.text:
                        button.click()
            except Exception: print("No cookies to accept")

        @staticmethod
        def build_search_urls() -> list:
            print('Building search urls')
            with open('towns.txt', 'r', encoding='utf-8') as f:
                towns = [line.strip() for line in f.readlines()]
                towns = [town.replace(' ', '+') for town in towns]
            with open('scraped_towns.txt', 'r', encoding='utf-8') as f:
                scraped_towns =  f.read()
            urls_list = [f'https://www.google.com/maps/search/{town}+Ресторанти' for town in towns if town not in scraped_towns]   
            print(f'Places to be acquired: {len(urls_list)}')
            return urls_list


        def acquire_places_urls(self, url: str) -> set:
            start_time = time.time()
            #Get the business URLs
            urls = set()
            self.browser.get(url)
            self.close_cookies_popup()

            #Wait for places to load
            try:
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'hfpxzc')))
            except Exception:
                with open('scraped_towns.txt', 'a', encoding='utf-8') as f:
                    f.write(url[35:] + '\n')
                return urls    

            stuck_counter = 0
            loop_start_time = time.time()
            while 'Стигнахте до края на списъка.' not in self.browser.page_source:

                #Check if stuck
                if (time.time() - loop_start_time) > 150:
                    break
                try: self.browser.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf.dS8AEf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd.QjC7t > div.lXJj5c.Hk4XGb > div.qjESne.veYFef')    
                except Exception: stuck_counter = 0   
                else: stuck_counter +=1
                if stuck_counter >= 15:
                    print('Loading takes too long. Skipping')
                    break

                #Scroll
                for _ in range(15):
                    try:
                        self.browser.find_element(By.XPATH, '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]').send_keys(Keys.PAGE_DOWN)
                    except Exception:
                        #if there's an error with the page we just continue to the next page
                        break
                    time.sleep(0.2)

            page = self.browser.page_source
            soup = BeautifulSoup(page, 'html.parser')
            with open('places_urls.txt', 'a', encoding='utf-8') as f:
                for match in soup.find_all('a', href=True):
                    if '/place/' in (link := str(match['href'])):
                        f.write(link + "\n")
                        urls.add(link)

            with open('scraped_towns.txt', 'a', encoding='utf-8') as f:
                f.write(url[35:] + '\n')
            #print(f'Took {(time.time() - start_time):.0f}s to acquire places urls')    
            return urls
                
        def scrape_reviews(self, urls: set):
            print(f'Scraping reviews for {len(urls)} businesses')
            # Create a loop for obtaining data from URLs
            for url in urls:

                # Open the Google Map URL
                self.browser.get(url)

                #Close cookies popup
                self.close_cookies_popup()   
                    
                # Obtain the reviews of that place
                
                # Click get reviews button
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'DkEaL')))
                self.browser.find_element(By.CLASS_NAME, 'DkEaL').click()

                # Scroll to get more reviews
                reviews = set()
                end_reached = False
                time.sleep(10)
                while end_reached is False:
                    for _ in range(15):
                        self.browser.find_element(By.XPATH, '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]').send_keys(Keys.PAGE_DOWN)
                        time.sleep(0.1)
                    
                    # Find reviews
                    for review in self.browser.find_elements(By.CLASS_NAME, "wiI7pd"):
                        if len(review.text) > 15:
                            reviews.add(review.text)
                        else:
                            end_reached = True
                            break

                # Save reviews
                print(f'Saving {len(reviews)} reviews from url: {url}')
                with open("reviews.txt", 'a', encoding='utf-8') as f:
                    for review in reviews:
                        f.write(str(review) + "\n\n")
                self.browser.quit() 

    try:
        scraper = Scraper(headless=True)
        search_urls = Scraper.build_search_urls()
        SEARCH_URLS_COUNT = len(search_urls)
        for index, search_url in enumerate(search_urls):
            print(f'Acquiring places urls for: {search_url[35:]} | {index} / {SEARCH_URLS_COUNT}')
            scraper.acquire_places_urls(url=search_url)
    except KeyboardInterrupt:
        print('Scraper stopped')
        #Remove duplicate lines
        with open('places_urls.txt', 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
            lines = list(dict.fromkeys(lines))
        with open('places_urls.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + "\n")
        print('Removed duplicates from places_urls.txt')        
        scraper.browser.quit()
        os._exit(os.X_OK)
            
    print('Done!')

if __name__ == '__main__':
    main()
    