from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import threading
import time
import json
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
            self.running = True
            self.inputs_handled = False

        def close_cookies_popup(self):
            try:
                buttons = self.browser.find_elements(By.CLASS_NAME, 'VfPpkd-dgl2Hf-ppHlrf-sM5MNb')
                for button in buttons:
                    if "Приемане" in button.text:
                        button.click()
            except Exception: print("Cookies Accepted")

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

        @staticmethod
        def remove_duplicate_lines(path: str):
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]
                lines = list(dict.fromkeys(lines))
            with open(path, 'w', encoding='utf-8') as f:
                for line in lines:
                    f.write(line + "\n")

        def stop_scraper_thread(self):
            while not self.inputs_handled:
                time.sleep(1)
            print('Press enter to exit scraper safely')    
            input()
            self.running = False

        def acquire_places_urls(self, url: str) -> set:
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
                    print('Loading takes more than 150 seconds. Skipping')
                    break
                try: self.browser.find_element(By.CSS_SELECTOR, (
                '#QA0Szd > div > div > div.w6VYqd > div.bJzME'
                '.tTVLSc > div > div.e07Vkf.kA9KIf.dS8AEf > div > div'
                '> div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.'
                'kA9KIf.dS8AEf.ecceSd.QjC7t > div.lXJj5c.Hk4XGb > div.qjESne.veYFef'))    
                except Exception: stuck_counter = 0   
                else: stuck_counter +=1
                if stuck_counter >= 15:
                    print('Loading takes too long. Skipping')
                    break

                #Scroll
                for _ in range(15):
                    try:
                        self.browser.find_element(By.XPATH, ('/html/body/div[3]/div[9]/div[9]/div/div/'
                        'div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')).send_keys(Keys.PAGE_DOWN)
                        if self.running is False:
                            print('Scraper stopped')   
                            self.browser.close()
                            self.browser.quit()
                            Scraper.remove_duplicate_lines('places_urls.txt')
                            Scraper.remove_duplicate_lines('reviews.txt')
                            print('Removed duplicates from files')
                            return 1
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
            return urls
                
        def scrape_reviews(self, urls: set):
            print(f'Scraping reviews for {len(urls)} businesses')
            # Create a loop for obtaining data from URLs
            for index, url in enumerate(urls):
                
                # Open the Google Map URL
                self.browser.get(url)

                #Close cookies popup
                self.close_cookies_popup()   
                
                # Click get reviews button
                try:
                    wait = WebDriverWait(self.browser, 10)
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'DkEaL')))
                    buttons = self.browser.find_elements(By.CLASS_NAME, 'DkEaL')
                    for button in buttons:
                        if 'отзив' in button.text:
                            button.click()
                            time.sleep(0.5)
                            break
                except Exception:
                    print('No reviews for business. Going to next business')
                    continue    

                # Scroll to get more reviews
                reviews = set()
                end_reached = False
                loop_start_time = time.time()
                while not end_reached:

                    #Check if stuck
                    if (time.time() - loop_start_time) > 150:
                        print('Loading takes more than 150 seconds. Skipping')
                        break

                    for _ in range(15):
                        try:
                            wait = WebDriverWait(self.browser, 10)
                            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf')))
                            self.browser.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf').send_keys(Keys.PAGE_DOWN)
                            if self.running is False:
                                print('Scraper stopped')   
                                self.browser.close()
                                self.browser.quit()
                                Scraper.remove_duplicate_lines('places_urls.txt')
                                Scraper.remove_duplicate_lines('reviews.txt')
                                print('Removed duplicates from files')
                                return 1
                        except Exception:
                            print("Can't scroll. Reached end of reviews. ")
                            end_reached = True
                            break
                        time.sleep(0.2)
                    
                    # Find reviews
                    new_reviews = self.browser.find_elements(By.CLASS_NAME, "jJc9Ad")

                    if len(new_reviews) > 2:
                        for review in new_reviews:
                            if 'Преведено' not in review.text and review.text != '':
                                reviews.add(review.text)
                    if new_reviews:
                        if len((new_reviews[-1]).text) < 5:
                            break                            
            
                # Save reviews
                # with open('reviews.txt', 'a', encoding='utf-8') as f:
                #     if len(reviews) > 2:
                #         print(f'Saving {len(reviews)} reviews')
                #         for review in reviews:
                #             f.write(f'{str(review)}\n')  
                #             #f.write(f'{str(review)} - {BUSINESS_NAME}\n')      
                with open('data.json', 'r', encoding='utf-8') as f:
                    json_obj = json.load(f)

                if len(reviews) > 2:
                    print(f'Saving {len(reviews)} reviews')
                    json_obj['data']['pairs'][url] = list(reviews)

                    with open(file='data.json', mode='w', encoding='utf-8') as f:
                        json.dump(json_obj, f, indent=2)
                         
                
                #Delete the scraped url from file
                with open('places_urls.txt', 'r') as f:
                    lines = [line.strip() for line in f.readlines()]
                with open('places_urls.txt', 'w') as f:
                    for line in lines:
                        if line != url:
                            f.write(f'{line}\n')
                print(f'{index} / {len(urls)}')            

        def screenshot_review(self, target_url: str, target_review: str):
            self.browser.get(target_url)
            self.close_cookies_popup()   
            try:
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'DkEaL')))
                buttons = self.browser.find_elements(By.CLASS_NAME, 'DkEaL')
                for button in buttons:
                    if 'отзив' in button.text:
                        button.click()
                        time.sleep(0.5)
                        break
            except Exception:
                print('No reviews for business. Going to next business')
                return None    

            # Scroll to get more reviews
            end_reached = False
            loop_start_time = time.time()
            while not end_reached:

                #Check if stuck
                if (time.time() - loop_start_time) > 150:
                    print('Loading takes more than 150 seconds. Skipping')
                    break

                for _ in range(15):
                    try:
                        wait = WebDriverWait(self.browser, 10)
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf')))
                        self.browser.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf').send_keys(Keys.PAGE_DOWN)
                        if self.running is False:
                            print('Scraper stopped')   
                            self.browser.close()
                            self.browser.quit()
                            Scraper.remove_duplicate_lines('places_urls.txt')
                            Scraper.remove_duplicate_lines('reviews.txt')
                            print('Removed duplicates from files')
                            return 1
                    except Exception:
                        print("Can't scroll. Reached end of reviews. ")
                        end_reached = True
                        break
                    time.sleep(0.2)
                
                # Find reviews
                new_reviews = self.browser.find_elements(By.CLASS_NAME, "jJc9Ad")
                
                if len(new_reviews) > 2:
                    for review in new_reviews:
                        if target_review in review.text:
                            print('Saving screenshot')
                            review.screenshot(os.path.join('screenshots', f'{time.time()}.png'))
                            return 0
                    if len((new_reviews[-1]).text) < 5:
                        return 1                            

        def search_phrases(self, phrases: list = [], screenshot: bool = False):
            BG_WORDS = [
                'педал', 'путка', 'наебан', 'насран',
                'грозен', 'малоумен', 'глупав', 'да еба',
                'шибан', 'копеле', 'боклук', 'чукундур',
                'майна'
                ]
            ENG_WORDS = [
                'maika', 'pedal', 'kuche', 'putka',
                'naeban', 'nasran', 'grozen', 'maloumen',
                'glupav', 'da eba', 'shiban', 'kopele',
                'bokluk', 'chukundur', 'maina'
                ] 

            with open('filtered reviews.txt', 'r', encoding='utf-8') as f:
                saved_reviews = f.read()

            with open('data.json', 'r', encoding='utf-8') as f:
                json_obj = json.load(f)
            url_dict = json_obj['data']['pairs']
            print('Loaded reviews')
            print('Searching phrases')
            with open('filtered reviews.txt', 'a', encoding='utf-8') as f:
                for url, reviews in url_dict.items():
                    for review in reviews:
                        if phrases[0] != '':
                            #Example: hello, looks like, this example
                            for phrase in phrases:
                                if phrase in review.lower() and review not in saved_reviews:
                                    f.write(f'{review} - {url}\n')
                                    if screenshot:
                                        self.screenshot_review(target_url=url, target_review=review)
                                    break
                        else:
                            for phrase in ENG_WORDS:
                                if phrase in review.lower() and review not in saved_reviews:
                                    #print(f'########{phrase}#########', review)
                                    f.write(f'{review} - {url}\n')
                                    if screenshot:
                                        self.screenshot_review(target_url=url, target_review=review)
                                    break  
                            for phrase in BG_WORDS:
                                if phrase in review.lower() and review not in saved_reviews:
                                    #print(f'########{phrase}#########', review)
                                    f.write(f'{review} - {url}\n')
                                    if screenshot:
                                        self.screenshot_review(target_url=url, target_review=review)
                                    break
                            
    scrape_reviews = input("(1) Scrape reviews from places_urls.txt\n(2) Acquire places URLs\n(3) Search phrases in reviews.txt\nChoice: ")
    
    headless = input('Run headless? (Y/N) ')
    headless = True if 'y' in headless.lower() else False    
    scraper = Scraper(headless=headless)
    threading.Thread(target=scraper.stop_scraper_thread).start()

    if scrape_reviews == '1':
        scraper.inputs_handled = True
        with open('places_urls.txt', 'r', encoding='utf-8') as f:
            places_urls = set([line.strip() for line in f.readlines()])  
        scraper.scrape_reviews(places_urls)  
    elif scrape_reviews == '2':
        search_urls = Scraper.build_search_urls()
        SEARCH_URLS_COUNT = len(search_urls)
        for index, search_url in enumerate(search_urls):
            print(f'Acquiring places urls for: {search_url[35:]} | {index} / {SEARCH_URLS_COUNT}')
            scraper.acquire_places_urls(url=search_url)
    else:
        phrases =  input('Enter phrases to search separated by ", ": ')
        phrases = phrases.split(', ')
        screenshot = input("Screenshot found reviews? (Y/N): ")
        scraper.inputs_handled = True
        screenshot = True if 'y' in screenshot.lower() else False    
        scraper.search_phrases(phrases=phrases, screenshot=screenshot)       

if __name__ == '__main__':
    main()
    