from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from common import get_user_links_by_text
from main import get_channels_by_category, session
from scraper.telegram import get_scrap_card_by_link, ScrapPreviewUser
from .forms import ChannelForm
from .models import Category, Channel, Manager
from scraper.telemetr import get_all_categories
from sessions.main import sessions
from .common import process_advertising_channels


def index(request: WSGIRequest):
    context = {
        'categories': Category.objects.all(),
    }

    return render(request, 'index.html', context=context)


def advertising_channels_test(request: WSGIRequest, seller_id):
    seller = Channel.objects.filter(id=seller_id).first()
    process_advertising_channels(session=next(sessions), seller=seller)
    pass



def find_managers(request: WSGIRequest, category):
    channels = Channel.objects
    if request.method == 'POST':
        form = ChannelForm(request.POST)
        if form.is_valid():
            channel_filter = {change: form.cleaned_data[change] for change in form.changed_data}
            channels = channels.filter(**channel_filter)

    else:
        form = ChannelForm()

    context = {
        'form': form,
        'channels': channels.count(),
        'category': category,
        'categories': Category.objects.all(),
    }

    return render(request, 'channel/find_managers.html', context=context)


def get_channels(request: WSGIRequest):
    if request.method == 'POST':
        channel_name = request.POST.get('channel_name')
        channels = Channel.objects.filter(title__icontains=channel_name).all()[:10]
        return render(request, 'channel/inc/channels_card.html', context={'channels': channels})


def set_data_in_db(request: WSGIRequest):
    categories = get_all_categories(session=session)
    all_channels_id = [channel.id for channel in Channel.objects.all()]
    for lang_code in ['ru', 'ua']:
        for category in categories:

            channels = get_channels_by_category(session=session, category_url=category.link_telemetr, lang_code=lang_code)
            for channel in channels:

                if channel.id in all_channels_id:
                    continue
                all_channels_id.append(channel.id)

                new_channel = Channel(
                    id=channel.id,
                    title=channel.title,
                    link_avatar=channel.link_avatar,
                    link_tg=channel.link_tg,
                    link_telemetr=channel.link_telemetr,
                    description=channel.description,
                    participants=channel.participants,
                    views=channel.views,
                    views24=channel.views24,
                    er=channel.er,
                    er24=channel.er24,
                    lang_code=lang_code,
                )
                new_channel.save()

                for channel_category in channel.categories:
                    category_in_db = Category.objects.filter(title__startswith=channel_category).first()
                    if category_in_db:
                        new_channel.categories.add(category_in_db)

                managers = get_user_links_by_text(text=new_channel.description)
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
                                except AttributeError as ex:
                                    continue
                        new_channel.managers.add(manager)
                    except Exception as ex:
                        pass
                pass

    return render(request, 'base.html')



