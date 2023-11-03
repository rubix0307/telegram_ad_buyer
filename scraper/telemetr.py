import re
import os.path
from typing import List

import requests
from dataclasses import dataclass

from bs4 import BeautifulSoup
import datetime as dt

from RedisCache.cache import cache_decorator


@dataclass
class ScrapChannel:
    id: int
    title: str
    link_avatar: str
    link_tg: str
    link_telemetr: str
    description: str
    participants: int
    views: int
    views24: int | None
    er: int
    er24: int | None
    categories: List[str] | None = None
    descriptions: list | None = None
    buyers: list | None = None
    links: list | None = None
    check_date: dt.datetime = dt.datetime.now()

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.title}'

    def __repr__(self):
        return self.__str__()


def clear_text(text):
    return re.sub(r'[\n\t\']', '', text).strip()


@cache_decorator(ignore_keys=['session'])
def get_channels_by_category_page(
        *,
        session: requests.Session,
        category_url: str,
        page: int,
        max_participants=1_000_000) -> List[ScrapChannel]:

    channels = []
    params = dict(
        page=page,
        participants_to=max_participants,
        lang_code='any',
    )

    response = session.get(category_url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    channels_table = soup.find('table', id='channels_table')
    channels_tbody = channels_table.find('tbody')
    channels_tbody_tr = channels_tbody.find_all('tr')

    channel_trs = [[channels_tbody_tr[num], channels_tbody_tr[num+1]] for num, tr in enumerate(channels_tbody_tr) if not num % 2]

    for data in channel_trs:
        tr_main_data, tr_categories = data

        photo_td = tr_main_data.find('td', 'text-center wd-100 pb-0')

        photo_block = photo_td.select_one('img') if photo_td else None
        photo = photo_block.get('src') if photo_block else None

        channel_data = tr_main_data.select_one('td.wd-300.pb-0')
        channel_a = channel_data.select_one('a')
        link_telemetr = f'https://telemetr.me{channel_a.get("href", "")}'
        title = channel_a.get_text(strip=True)

        data_cid = channel_data.select_one('button').get('data-cid')
        channel_id = int(data_cid) if data_cid else None

        link_tg = channel_data.select_one('a.btn.btn-sm.btn-xs.a_icon_black').get('data-link')
        description_block = channel_data.select_one('div.text-nowrap.pt-3')

        try:
            description = (description_block
                           .select_one('span.btn.btn-outline-warning.btn-sm.btn-xs.kt-font-dark')
                           .get('data-cont')
                           .replace('<br>', '\n')) if description_block else ''
        except AttributeError:
            description = None

        td_all = tr_main_data.find_all('td', class_='text-nowrap pb-0')

        participants_str = td_all[0].get_text(strip=True)
        participants = int(participants_str.replace('\'','')) if participants_str else 1

        views_block = td_all[2]

        views_data = []
        views_spans = views_block.find_all('span')
        for span in views_spans:
            views_data.append(int(span.text.replace('\'', '')) if span else 0)
        if not views_data or len(views_data) != 2:
            views_data = [0, 0]

        views, views24 = views_data

        categories_a = (tr_categories.find('td').find('div', class_='web-hide pb-2')
                        .find_all('a', class_='btn btn-label-facebook btn-sm pl-2 pr-2 pt-1 pb-1 kt-font-12'))
        categories = [c.text.split(' ')[0] for c in categories_a]

        try:
            er = round((views / participants) * 100, 1)
            er24 = round((views24 / participants) * 100, 1)
        except ZeroDivisionError:
            er = 0
            er24 = 0

        channel = ScrapChannel(
            id=channel_id,
            title=title,
            link_avatar=photo,
            link_tg=link_tg,
            link_telemetr=link_telemetr,
            description=description,
            participants=participants,
            views=views,
            views24=views24,
            er=er,
            er24=er24,
            categories=categories,
        )
        channels.append(channel)

    return channels


@cache_decorator(ignore_keys=['session'])
def get_channel_by_page(
        *,
        session: requests.Session,
        link_telemetr: str) -> ScrapChannel:

    response = session.get(link_telemetr)
    soup = BeautifulSoup(response.text, 'html.parser')

    tab_panel = soup.find('div',class_='tab-pane active')
    rows = tab_panel.find_all('div', class_='col-lg-4 col-md-4')
    left_row, middle_row, right_row = rows

    #left_row
    div_avatar = left_row.find('div', class_='kt-widget__media text-center kt-hidden- analytics-main-c-avatar-wrap')
    img_avatar = div_avatar.find('img')
    link_avatar = img_avatar.attrs.get('src')

    div_content = left_row.find('div', class_='kt-widget__content')
    div_title = div_content.find('div', class_='kt-widget__head')
    a_title = div_title.find('a', class_='kt-widget__username')
    title = a_title.get_text(strip=True)
    link_tg = a_title.attrs.get('href')

    div_info = div_content.find('div', class_='kt-widget__info')
    div_description = div_info.find('div', class_='kt-widget__desc t_long')
    description = '\n'.join([part.get_text(strip=True) for part in div_description.contents if str(part) != '<br/>'])

    c_id = left_row.find('select').attrs.get('data-id')
    option_categories = left_row.select('option[selected]')
    categories = [category.attrs.get('value') for category in option_categories]

    #middle_row
    div_participants_data = middle_row.find('div', class_='row text-center')
    div_participants, *_ = div_participants_data.find_all('div', class_='col-md-3')
    participants = int(clear_text(div_participants.find('span', attrs={'data-num': 'participants'}).get_text(strip=True)))

    views = int(clear_text(middle_row.find('span', attrs={'data-num': 'views_per_post'}).get_text(strip=True)))

    try:
        er = round((views / participants) * 100, 1)
    except ZeroDivisionError:
        er = 0

    channel = ScrapChannel(
        id=c_id,
        title=title,
        link_avatar=link_avatar,
        link_tg=link_tg,
        link_telemetr=link_telemetr,
        description=description,
        participants=participants,
        views=views,
        views24=None,
        er=er,
        er24=None,
        categories=categories,
    )

    return channel


@redis_cache(ignore_keys=['session'])
def get_all_categories(*, session: requests.Session) -> List[ScrapCategories]:

    response = session.get('https://telemetr.me/channels')
    soup = BeautifulSoup(response.text, 'html.parser')

    cats_long = soup.find('div', class_='row cats_long')
    cats_span = cats_long.find_all('span', class_='btn-group btn-group cat-group')

    categories = []
    for span in cats_span:
        a = span.find('a')
        categories.append(ScrapCategories(
            title=a.get_text(strip=True),
            link_telemetr='https://telemetr.me' + a.attrs.get('href').split('?')[0]
        ))
    return categories






















