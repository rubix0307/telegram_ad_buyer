import os
import pickle
import random
from itertools import cycle
from typing import Generator, List

import requests

headers = {
    'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,it;q=0.6',
    'Content-Length': '721',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}
proxies_list = [
    'http://50.168.72.119:80', 'http://24.205.201.186:80', 'http://70.166.167.38:57728',
    'http://172.67.3.115:80', 'http://185.162.229.142:80', 'http://185.162.229.28:80',
    'http://107.1.93.211:80', 'http://50.207.199.86:80', 'http://50.168.72.114:80',
    'http://50.169.62.106:80', 'http://66.235.200.116:80', 'http://172.67.180.2:80',
    'http://45.14.174.128:80', 'http://45.8.104.0:80', 'http://45.12.30.214:80',
    'http://185.162.228.186:80', 'http://45.12.31.197:80', 'http://185.162.231.169:80',
    'http://185.162.230.147:80', 'http://45.8.105.232:80'
]


def load_object(path):
    with open(path, "rb") as file:
        data = pickle.load(file)
        return data


def get_proxy(proxies=proxies_list):
    proxies_cycle = cycle(proxies)

    for proxy in proxies_cycle:
        yield proxy


proxies = get_proxy(proxies_list)


def all_sessions(*, cookies_path):
    all_cookies = [
        load_object(os.path.join(cookies_path, cookies_name))
        for cookies_name in os.listdir(cookies_path) if cookies_name.endswith('pkl')
    ]

    sessions_list: List[requests.Session] = []
    for cookies in all_cookies:
        new_session = requests.Session()

        for cookie in cookies:
            new_session.cookies.set(cookie['name'], cookie['value'])

        new_session.headers.update(headers)
        # new_session.proxies.update({'http': next(proxies)})
        sessions_list.append(new_session)

    random.shuffle(sessions_list)
    sessions_cycle = cycle(sessions_list)

    for session in sessions_cycle:
        yield session


sessions = all_sessions(cookies_path='sessions/cookies')
