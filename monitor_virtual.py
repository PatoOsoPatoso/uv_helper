#!/bin/bash

import os
import urllib
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from dotenv import load_dotenv

# Fix to load chromedriver in both linux and windows
extension = '.exe' if os.name == 'nt' else ''

# URL to the uv calendar
url_calendar = 'https://aulavirtual.uv.es/calendar/view.php'

# Headless and 0 loggs for the webdriver
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.headless = True

# Load the .env file with the uv credentials, telegram bot token and chat id
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

username = os.environ.get("UV_USER")
password = os.environ.get("UV_PASS")
token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("CHAT_ID")

# Change this for the years you are currently cursing
year = '2021-2022'

# We need the seasson cookies to keep the task monitor alive
def getCookies():
    # Download chromedriver from: https://chromedriver.storage.googleapis.com/index.html?path=&sort=desc
    driver = webdriver.Chrome(f'chromedriver{extension}', options=options)

    # We use the calendar url to bypass some authentication features and get redirected in less time.
    driver.get(url_calendar)

    # Find the desired clickable
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/section/div/div[2]/div/div/div/div/div[2]/div[1]/div/div/a').click()

    # Send credentials
    driver.find_element_by_name('username').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_name('Login').click()

    # Store and close the driver
    driver_cookies = driver.get_cookies()
    driver.close()

    # We return the necessary parts of the cookie to be used later.
    return {
        "MOODLEID1_": driver_cookies[0]["value"],
        "MDL_SSP_AuthToken": driver_cookies[1]["value"],
        "MoodleSession": driver_cookies[2]["value"],
        "MDL_SSP_SessID": driver_cookies[3]["value"]
    }

def send_message(title, date, course, link):
    hor = '-------------------------------------------------------------'
    alert = '                         NUEVA TAREA                       '
    # We parse the message so it doesn't mess with the URL
    message = urllib.parse.quote(f'*{hor}\n\n{alert}\n\n\n{title}\n\n{date}\n\n{course}\n\n{link}\n\n{hor}*')
    # We use the URL from the telegram api to send the message with the bot token and the chat_id
    requests.get('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message)

def task_monitor(cookies, old_events):
    request = requests.get(url_calendar, cookies=cookies)
    soup = BeautifulSoup(request.text, "html.parser")
    # Get all the events
    events = soup.findAll("div", {"class": "event m-t-1"})
    # Empty list for new events
    new_events = []
    # Iterate all the events
    for event in events:
        title = event.get('data-event-title')
        columns = event.findAll("div", {"class": "col-11"})
        date = columns[0].text
        course = columns[2].find("a")
        # Fix for when the course is not displayed initialy
        if not course:
            course = columns[3].find("a")
        course = course.text.split(year)[1].split(' Gr')[0]
        link = event.find("a", {"class": "card-link"}).get('href')
        # We append the event as a list with all of it's parameters
        new_events.append([title, date, course, link])
        send = True
        for item in old_events:
            if item[0] == title:
                # If this event is stored in the old events we don't send a notification for it because we already did
                send = False
                break
        # If the event is actually new
        if send:
            send_message(title, date, course, link)
    # We store all the new events into the old events to register the ones we sent
    old_events = new_events

def main():
    cookies = getCookies()
    # Initialization of a list to store the old task events
    old_events = []
    while True:
        # If there is a conenction error we reload the cookies
        try:
            task_monitor(cookies, old_events)
        except:
            cookies = getCookies()

if __name__ == "__main__":
    main()