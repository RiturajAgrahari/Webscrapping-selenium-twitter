from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import twitter.constants as const
from bs4 import BeautifulSoup
import datetime
import time
import pyperclip


class UseTwitter(webdriver.Chrome):
    def __init__(self, driver_path="../chromedriver.exe", teardown=False, headless=True):
        self.driver_path = driver_path
        self.teardown = teardown  # The browser will quit after doing operation {Boolean}.
        self.headless = headless  # The browser will work without window {Boolean}.

        # Initialize service and options
        self.service = Service(executable_path=self.driver_path)
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_experimental_option("detach", True)

        # maximizing window if not headless
        super(UseTwitter, self).__init__(service=self.service, options=self.options)
        self.implicitly_wait(60)
        self.maximize_window()
        self.get(url=const.BASE_URL)

        # signing up...
        sign_in = self.find_element(By.XPATH,
                                    "//div[@dir='ltr'][span[@style='text-overflow: unset;'][span[text()[contains(., 'Sign in')]]]]")
        sign_in.click()

        input_username = self.find_element(By.XPATH,
                                           "//label[@class='css-175oi2r r-1ets6dv r-z2wwpe r-rs99b7 r-18u37iz']//div[contains(@class, 'css-175oi2r')]//div[@dir='ltr']/input[@autocomplete='username']")
        input_username.send_keys(const.YOUR_USERNAME)

        proceed = self.find_element(By.XPATH, "//div[@dir='ltr']/span/span[text()[contains(., 'Next')]]")
        proceed.click()

        input_password = self.find_element(By.XPATH,
                                           "//label[@class='css-175oi2r r-z2wwpe r-rs99b7 r-18u37iz r-vhj8yc r-9cip40']//div[contains(@class, 'css-175oi2r')]//div[@dir='ltr']/input[@autocomplete='current-password']")
        input_password.send_keys(const.YOUR_PASSWORD)

        log_in = self.find_element(By.XPATH, "//div[@dir='ltr']/span/span[text()[contains(., 'Log in')]]")
        log_in.click()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown and self.headless:
            self.quit()

    def set_user(self, user_id: str):
        find_search = self.find_element(By.CSS_SELECTOR, "a[href='/explore']")
        find_search.click()

        input_search = self.find_element(By.CSS_SELECTOR, "input[aria-label='Search query']")
        input_search.send_keys(user_id)

        time.sleep(5)

        click_this = self.find_element(By.XPATH,
                                       f"//div[@tabindex='-1']/div[@class='css-175oi2r'][div[@dir='ltr'][span[text()[contains(., '@{user_id}')]]]]")
        click_this.click()

    def get_profile(self):
        time.sleep(5)
        user_description = []

        try:
            banner = self.find_element(By.XPATH, "//div[@class='css-175oi2r']/a[@role='link']//img[@draggable='true']")
            user_banner = banner.get_attribute('src')
        except:
            user_banner = ''
            print('banner not found')

        try:
            pfp = self.find_element(By.XPATH, "//div[@aria-label='Opens profile photo']/img")
            user_profile_picture = pfp.get_attribute('src')
        except:
            user_profile_picture = ''
            print('pfp not found')

        try:
            name = self.find_element(By.XPATH, "//div[@data-testid='UserName']//div[@dir='ltr']/span/span")
            username = name.get_attribute('innerHTML')
        except:
            username = ''
            print('name not found')

        try:
            uid = self.find_element(By.XPATH,
                                    "//div[@data-testid='UserName']//div[@tabindex='-1']//div[@dir='ltr']/span")
            user_id = uid.get_attribute('innerHTML')
        except:
            user_id = ''
            print('userid not found')

        try:
            description = self.find_element(By.XPATH, "//div[@data-testid='UserDescription']")
            description_element = description.get_attribute('innerHTML')
            soup = BeautifulSoup(description_element, 'html.parser')
            for description_content in soup:
                user_description.append(description_content.text)
        except:
            print('description not found')

        try:
            header_link = self.find_element(By.CSS_SELECTOR, "a[data-testid='UserUrl']")
            user_official_link = header_link.get_attribute('href')
        except:
            user_official_link = ''
            print('header_link not found')

        try:
            header_date = self.find_element(By.XPATH, "//span[@data-testid='UserJoinDate']/span")
            user_joined_date = header_date.get_attribute('innerHTML')
        except:
            user_joined_date = ''
            print('header_date not found')

        return user_banner, user_profile_picture, username, user_id, user_description, \
            user_official_link, user_joined_date

        # try:
        #     user_following = self.find_element("//div[@class='css-175oi2r r-1mf7evn']/a[@dir='ltr']/span/span")
        #     print(user_following.get_attribute('innerHTML'))
        # except Exception as e:
        #     print('user_following not found :', e)

    def get_post_data(self, date=str(datetime.date.today())):
        time.sleep(5)
        tweet_texts = []
        tweet_images = []
        tweet_videos = []
        post_found = False

        try:
            if date == str(datetime.date.today()):
                raw_date = date.split('-')  # ['27', '12', '2023']
                raw_date.reverse()
                my_month = datetime.date(int(raw_date[2]), int(raw_date[1]), int(raw_date[0])).strftime("%B")[0:3]
                my_date = datetime.date(int(raw_date[2]), int(raw_date[1]), int(raw_date[0])).strftime('%d')
                try:
                    open_post = self.find_element(By.XPATH, f"//time[text()[contains(., 'h')]]")
                    # print('page is found via hour!')
                except:
                    open_post = self.find_element(By.XPATH, f"//time[text()[contains(., '{my_month} {my_date}')]]")
                    # print('page is found via date!')

            else:
                raw_date = date.split('-')
                my_month = datetime.date(int(raw_date[2]), int(raw_date[1]), int(raw_date[0])).strftime("%B")[0:3]
                my_date = datetime.date(int(raw_date[2]), int(raw_date[1]), int(raw_date[0])).strftime('%d')
                open_post = self.find_element(By.XPATH, f"//time[text()[contains(., '{my_month} {my_date}')]]")

            open_post.click()
            post_found =True
        except:
            print('post is not found')

        if post_found:
            try:
                tweet_text = self.find_element(By.XPATH, "//div[@data-testid='tweetText']")
                tweet_text_content = tweet_text.get_attribute('innerHTML')
                soup = BeautifulSoup(tweet_text_content, 'html.parser')
                for element in soup:
                    print(element.text)
                    tweet_texts.append(element.text)
            except Exception as e:
                print('No text in tweet')

            try:
                tweet_image = self.find_element(By.XPATH, "//div[@data-testid='tweetPhoto']")
                tweet_image_content = tweet_image.get_attribute('innerHTML')
                soup = BeautifulSoup(tweet_image_content, 'html.parser')
                for element in soup:
                    print(element.get('src'))
                    tweet_images.append(element.get('src'))

            except Exception as e:
                print('No image in tweet')

            try:
                tweet_video = self.find_element(By.XPATH, "//div[@data-testid='videoComponent']")
                tweet_video_content = tweet_video.get_attribute('innerHTML')
                soup = BeautifulSoup(tweet_video_content, 'html.parser')
                for element in soup:
                    print(element.get('src'))
                    tweet_videos.append(element.get('src'))

            except Exception as e:
                print('No video in tweet')

            share_link = self.find_element(By.CSS_SELECTOR, "div[aria-label='Share post']")
            share_link.click()

            copy_link = self.find_element(By.XPATH, "//div[@role='menuitem']/div/div[@dir='ltr']/span[text()[contains(., 'Copy link')]]")
            copy_link.click()

            clipboard_content = pyperclip.paste()
            print("Clipboard Content:", clipboard_content)

            self.back()

            return tweet_texts, tweet_images, tweet_videos, clipboard_content

        else:
            return tweet_texts, tweet_images, tweet_videos, ''





