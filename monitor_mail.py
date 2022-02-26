#!/bin/bash

import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Define some usefull URL
url_login = 'https://as.uv.es/cgi-bin/AuthServer?ATTREQ=portal&PAPIPOAREF=d7f188fc85ae17379c0a0b671cb32f83&PAPIPOAURL=https%3A%2F%2Fportal.uv.es%2Fcgi-bin%2Fportal%2Fportal'
url_mail = 'https://correo.uv.es/cgi-bin/ppostman/cclient/mb_change/noop/ca/'
url_header = 'https://correo.uv.es'

# Load the contents of the .env file with credentials
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Store the UV credentials into a dict to use it with the requests session later
data = {
    'username': os.environ.get("UV_USER"),
    'password': os.environ.get("UV_PASS")
}

# Store telegram token and chat id
token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("CHAT_ID")

def getNotSeen(soup):
    messages = soup.find("table", {"class": "imap_index_table"}).findAll("tr")
    not_seen = []
    if messages:
        for message in messages:
            flags = message.findAll("img", {"class": "img_flags"})
            if flags:
                for flag in flags:
                    if flag.get('title') == 'Nou':
                        not_seen.append(message)
    return not_seen

def getHref(soup):
    a_tags = soup.findAll("a")
    if a_tags:
        for item in a_tags:
            try:
                # Dirty fix to be sure we are in the correct path
                if 'prevpage.gif' == item.find("img", {"class": "buttons_img"}).get('src').split('/')[-1]:
                    return item.get('href')
            except:
                pass
    return ''

def sendMessage(item):
    date = item.find("td", {"class": "i_date"}).text
    sender = item.find("td", {"class": "i_from"}).text
    text = item.find("td", {"class": "i_subject"}).find("a").text
    url = url_header + item.find("td", {"class": "i_subject"}).find("a").get('href')
    separator = "\n\n     -------------------------     \n\n"
    message = f"{date}{separator}{sender}{separator}{text}{separator}{url}"
    requests.get('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Html&text=' + message)

def monitor_msgs(s, saved):
    request = s.get(url_login)
    soup = BeautifulSoup(request.text, "html.parser")

    num = soup.find("div", {"class": "itemmailu"})

    if num:
        num = int(num.text)
        not_seen = []

        request = s.get(url_mail)
        soup = BeautifulSoup(request.text, "html.parser")
        not_seen.extend(getNotSeen(soup))

        while num > len(not_seen):
            href = getHref(soup)
            if href:
                request = s.get(url_header + href)
                soup = BeautifulSoup(request.text, "html.parser")
                not_seen.extend(getNotSeen(soup))
        for i in not_seen:
            send = True
            for j in saved:
                i_num = i.find("td", {"class": "i_num"}).text
                j_num = j.find("td", {"class": "i_num"}).text
                if i_num == j_num:
                    send = False
            if send:
                sendMessage(i)
        saved = not_seen

def main():
    with requests.Session() as s:
        saved = []
        while True:
            try:
                monitor_msgs(s, saved)
            except:
                s.post(url_login, data=data)

if __name__ == "__main__":
    main()