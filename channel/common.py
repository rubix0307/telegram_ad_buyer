from typing import List

from django.utils import timezone

from channel.models import Channel, Advertisement
from scraper.telemetr import AdvertisingChannel, get_advertising_by_channel


def add_channel_by_advertising_channels(channels: List[AdvertisingChannel]):

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
    channels = get_advertising_by_channel(session=session, channel=seller)

    add_channel_by_advertising_channels(channels)
    add_advertising(channels)




