from threading import Thread
from typing import List
from concurrent.futures import ThreadPoolExecutor


from channel.common import gen
from channel.models import Channel, Manager
from common import get_user_links_by_text
from scraper.telegram import get_scrap_card_by_link, ScrapPreviewUser
from sessions.main import sessions


def set_managers_by_channel(channel: Channel):

    session = next(sessions)
    channel_card = get_scrap_card_by_link(session=session, link=channel.link_tg)

    if channel_card and channel_card.description:
        channel.description = channel_card.description
        channel.save()

        managers = get_user_links_by_text(text=channel.description)

        for manager_link in managers:
            try:
                manager = Manager.objects.filter(link_tg=manager_link).first()

                if not manager:
                    manager_scrap_card = get_scrap_card_by_link(session=session, link=manager_link)
                    if isinstance(manager_scrap_card, ScrapPreviewUser):
                        try:
                            manager = Manager(
                                name=manager_scrap_card.name,
                                username=manager_scrap_card.username,
                                description=manager_scrap_card.description,
                                link_avatar=manager_scrap_card.link_avatar,
                                link_tg=manager_scrap_card.link_tg,
                            )
                            manager.save()
                            channel.managers.add(manager)
                        except AttributeError as ex:
                            continue

            except Exception as ex:
                pass

    return


def set_managers_by_channels_with_threads(channels: List[Channel], threads_num=1):
    channels = gen(channels)

    with ThreadPoolExecutor(max_workers=threads_num) as executor:
        executor.map(set_managers_by_channel, channels)
































