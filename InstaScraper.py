from typing import List, Dict
import re
import pickle
from time import sleep

# requests
import requests
import json
from urllib.parse import quote

# selenium
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait



class InstaScraper:
    def __init__(self):
        # requests related
        self.driver = self._get_chrome_driver()
        self.req_session = self._create_request_session()
        self._req_headers = self._get_req_headers()
    
    def get_first_page_data(self,username):
        """
        Returns the data is json format from the landing page of an Insta account

        Arguments:
            Username of the account that needs to be scraped in form of a string

        Return:
            Account data in json format from the landing page of the user account
        """

        res = self.req_session.get(
            url="https://www.instagram.com/" + username + "/?__a=1",
            headers=self._req_headers
        )

        data = res.json()
        return data

    def get_account_id(self,account_data):
        """
        Returns the user id of the account, given the data from the landing page

        Arguments:
            Account data in json format retrieved from the landing page

        Return:
            The user id of the instagram account as a string
        """
        #retrieves a list of media items present on the instagram page
        media_list = (
            account_data.get("graphql").get("user").get("edge_owner_to_timeline_media").get("edges")
        )
        #gets the user id from the first media item retrieved from the page
        user_id = media_list[0].get("node").get("owner").get("id")
        return user_id

    def get_first_page_id(self,account_data):
        """
        Returns the page id of the landing page, given the data from the landing page

        Arguments:
            Account data in json format retrieved from the landing page

        Return:
            The page id of the instagram account's landing page as a string
        """
        data=account_data
        #checks if the has_next_page attribute is True for the current page
        next_exist = (
                data.get("graphql")
                .get("user")
                .get("edge_owner_to_timeline_media")
                .get("page_info")
                .get("has_next_page")
            )
        #If the a next page exists, checks for the page id for the current page 
        if next_exist!=False:
            next_page = (
                data.get("graphql")
                .get("user")
                .get("edge_owner_to_timeline_media")
                .get("page_info")
                .get("end_cursor")
            )
            return next_page
        return None

    def get_page_id(self,account_data):
        """
        Returns the page id of the instagram page, given the data from the page

        Arguments:
            Account data in json format retrieved from the page

        Return:
            The page id of the instagram account's page as a string
        """

        data=account_data
        #checks if the has_next_page attribute is True for the current page
        next_exist = (
                data.get("data")
                .get("user")
                .get("edge_owner_to_timeline_media")
                .get("page_info")
                .get("has_next_page")
            )
         #If the a next page exists, checks for the page id for the current page 
        if next_exist!=False:
            next_page = (
                data.get("data")
                .get("user")
                .get("edge_owner_to_timeline_media")
                .get("page_info")
                .get("end_cursor")
            )
            return next_page
        return None

    def url_genrator(self,user_id,page_id):
        """
        Returns the URL for the GET request to retrive next page data, given the user id and page id of the current page

        Arguments:
            User id and page id of the current page

        Return:
            URL for the GET request to retrive next page data
        """
        new_url = (
                'https://www.instagram.com/graphql/query/?query_hash=472f257a40c653c64c666ce877d59d2b&variables={"id":"'
                + user_id
                + '","first":90,"after":"'
                + page_id
                + '"}'
            )
        return new_url

    def get_account_data(self,url):
        """
        Returns the data is json format from the current page of an Insta account

        Arguments:
            URL to send the get request to in form of a string

        Return:
            Account data in json format from the current page of the user account
        """

        res = self.req_session.get(
                url=url,
                headers=self._req_headers
            )
        data = res.json()
        return data
        

    def get_account_media(self,data):
        """
        Returns a list of media items present on the current page given the data in json format

        Arguments:
            Data retrived from the current page in json format

        Return:
            List of media items present on the current page
        """

        media_list = (
                data.get("data")
                .get("user")
                .get("edge_owner_to_timeline_media")
                .get("edges")
            )
        return media_list

    def _get_chrome_driver(self):
        # Configure Selenium
        opts = Options()
        opts.add_argument(
            "User-Agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
        )
        opts.add_argument("--diable-notifications")
        opts.add_argument("user-data-dir=chrome-data")
        opts.add_argument("--headless")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        return driver
    
    def _get_session_cookies(self):
        """
        Load cookies from session_cookies.pkl file. If the file doesn't exist, get the cookie from the chrome driver
        """
        # load cookie from file
        try:
            with open("insta_session_cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
        # if cookie file doesn't exist, get cookies from selenium
        except IOError:
            WAIT_TIME = 10
            self.driver.get("https://www.instagram.com/")
            sleep(WAIT_TIME)
            cookies = self.driver.get_cookies()
            with open("insta_session_cookies.pkl", "wb") as f:
                pickle.dump(cookies, f)
        # to exit the selenium session once we are done setting up the cookies
        self.driver.quit()
        return cookies
    
    def _create_request_session(self):
        """Create a requests session with cookies loaded"""

        # TODO: log in, change location
        cookies = self._get_session_cookies()
        req_session = requests.Session()

        # set cookies to request session
        for cookie in cookies:
            cookie_name = cookie.get("name")
            cookie_val = cookie.get("value")
            if cookie_name and cookie_val:
                req_session.cookies.set(cookie_name, cookie_val)

        return req_session

    def _get_req_headers(self):
        """Request headers for Instagram. It's always the same"""

        headers = {
            "origin": "https://www.instagram.com",
            "referer": "https://www.instagram.com/",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        }
        return headers

       