import os.path
from typing import List

import requests
from dataclasses import dataclass

from bs4 import BeautifulSoup
import datetime as dt


@dataclass
class ChannelParsData:
    id: int
    title: str
    link_avatar: str
    link_tg: str
    link_telemetr: str
    description: str
    participants: int
    views: int
    views24: int
    er: int
    er24: int
    categories: List[str] | None = None
    descriptions: list | None = None
    buyers: list | None = None
    links: list | None = None
    check_date: dt.datetime = dt.datetime.now()

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.title}'

    def __repr__(self):
        return self.__str__()


def get_channels_by_category_page(
        session: requests.Session,
        category_url: str,
        category_page: int,
        max_participants=1_000_000) -> List[ChannelParsData]:

    channels = []
    params = dict(
        page=category_page,
        participants_to=max_participants,
        lang_code='any',
    )
    if not os.path.exists('test.html'):
        response = session.get(category_url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        soup = BeautifulSoup(open('test.html', 'r', encoding='utf-8'), 'html.parser')

    channels_table = soup.find('table', id='channels_table')
    channels_tbody = channels_table.find('tbody')
    channels_tbody_tr = channels_tbody.find_all('tr')

    channel_trs = [[channels_tbody_tr[num],channels_tbody_tr[num+1]] for num, tr in enumerate(channels_tbody_tr) if not num % 2]

    for num, data in enumerate(channel_trs):
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
        description = (description_block
                       .select_one('span.btn.btn-outline-warning.btn-sm.btn-xs.kt-font-dark')
                       .get('data-cont')
                       .replace('<br>', '\n')) if description_block else ''

        td_all = tr_main_data.find_all('td', class_='text-nowrap pb-0')

        participants_str = td_all[0].get_text(strip=True)
        participants = int(participants_str.replace('\'','')) if participants_str else None

        views_block = td_all[2]

        views_data = []
        views_spans = views_block.find_all('span')
        for span in views_spans:
            span_value = int(span.text.replace('\'', '')) if span else None
            views_data.append(span_value)
        views, views24 = views_data

        categories_a = (tr_categories.find('td').find('div', class_='web-hide pb-2')
                        .find_all('a', class_='btn btn-label-facebook btn-sm pl-2 pr-2 pt-1 pb-1 kt-font-12'))
        categories = [c.text.split(' ')[0] for c in categories_a]

        channel = ChannelParsData(
            id=channel_id,
            title=title,
            link_avatar=photo,
            link_tg=link_tg,
            link_telemetr=link_telemetr,
            description=description,
            participants=participants,
            views=views,
            views24=views24,
            er=round((views/participants) * 100, 1),
            er24=round((views24/participants) * 100, 2),
            categories=categories,
        )
        channels.append(channel)

    return channels
