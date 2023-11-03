import re
import os.path
from typing import List

import requests
from dataclasses import dataclass

from bs4 import BeautifulSoup
import datetime as dt

from RedisCache.cache import redis_cache


@dataclass
class ScrapPreviewChannel:
    title: str
    participants: int
    description: str
    link_avatar: str
    link_tg: str
    check_date: dt.datetime = dt.datetime.now()

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.title}'

    def __repr__(self):
        return self.__str__()

@dataclass
class ScrapPreviewUser:
    name: str
    username: str
    description: str
    link_avatar: str
    link_tg: str
    check_date: dt.datetime = dt.datetime.now()

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.name}'

    def __repr__(self):
        return self.__str__()


@redis_cache(ignore_keys=['session'], ex=60*60*24*7)
def get_scrap_card_by_link(*, session, link):

    response = session.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')

    tgme_page = soup.find('div', class_='tgme_page', )

    if not tgme_page or 'tgme_page_post' in tgme_page.attrs.get('class', []):
        return False

    tgme_page_photo = tgme_page.find('div', class_='tgme_page_photo')
    link_avatar = tgme_page_photo.find('img').attrs.get('src') if tgme_page_photo else None

    tgme_page_description = tgme_page.find('div', class_='tgme_page_description')
    description = '\n'.join([str(i) for i in tgme_page_description.contents]) if tgme_page_description else ''

    for stop_word in ['can add', 'group or channel', 'If you have', 'Press the button', 'emoji set']:
        if stop_word.lower() in description.lower():
            return False

    tgme_page_title = tgme_page.find('div', class_='tgme_page_title')
    title = tgme_page_title.get_text(strip=True)

    tgme_page_extra = tgme_page.find('div', class_='tgme_page_extra')
    extra = tgme_page_extra.get_text(strip=True)

    if not 'subscribe' in extra:
        answer = ScrapPreviewUser(
            name=title,
            username=extra,
            description=description,
            link_avatar=link_avatar,
            link_tg=link,
            )
    else:
        participants = int((extra.replace('no','').split('subscribe')[0].replace(' ','')) or 0)
        answer = ScrapPreviewChannel(
            title=title,
            participants=participants,
            description=description,
            link_avatar=link_avatar,
            link_tg=link,
        )
    return answer


