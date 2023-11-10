from itertools import cycle
from typing import List

from django.utils import timezone

from RedisCache.cache import get_cache_key, get_cache
from channel.models import Channel, Advertisement
from scraper.telemetr import AdvertisingChannel, get_advertising_by_channel


def gen(data: list, is_cycle=False):

    if is_cycle:
        data = cycle(data)

    for d in data:
        yield d


def add_channel_by_advertising_channels(channels: List[AdvertisingChannel]):

    if channels:
        for channel_data in channels:
            channel, created = Channel.objects.update_or_create(
                id=channel_data.id,
                defaults=dict(
                    title=channel_data.title,
                    link_tg=channel_data.link_tg,
                    link_avatar=channel_data.link_avatar,
                    link_telemetr=channel_data.link_telemetr,
                    participants=channel_data.participants,
                ),
            )
            pass


def add_advertising(channels: List[AdvertisingChannel]):

    for channel_data in channels:
        seller = Channel.objects.filter(id=channel_data.seller_id).first()
        buyer = Channel.objects.filter(id=channel_data.id).first()

        try:
            ad, created = Advertisement.objects.update_or_create(
                seller=seller,
                buyer=buyer,
                date=timezone.make_aware(channel_data.date),
            )
        except Exception as ex:
            pass


def process_advertising_channels(session, seller: Channel):

    cache_key = get_cache_key(get_advertising_by_channel, channel=seller)
    cache = get_cache(cache_key)

    if not cache:
        channels = get_advertising_by_channel(session=session, channel=seller)

        add_channel_by_advertising_channels(channels)
        add_advertising(channels)
    else:
        print(f'skip {cache_key}'.encode('utf-8'))



