from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.contrib import messages

from common import get_user_links_by_text, clear_text
from test_main import get_channels_by_category, session
from task.managers import set_managers_by_channels_with_threads
from scraper.telegram import get_scrap_card_by_link, ScrapPreviewUser
from scraper.telemetr import get_all_categories
from sessions.main import sessions
from .forms import ChannelForm, BuyerForm
from .models import Category, Channel, Manager, Advertisement, UserManagerHistory, UserBuyerHistory
from .common import process_advertising_channels
from user.models import Subscription


def index(request: WSGIRequest):
    context = {
        'subscriptions': Subscription.objects.filter(is_active=True).order_by('price').all()
    }
    return render(request, 'channel/index.html', context=context)


def managers_history(request: WSGIRequest, category_id: int, only_managers_history=False):
    category = Category.objects.filter(id=category_id).first()

    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    history = Manager.objects.filter(
            usermanagerhistory__user=request.user,
            usermanagerhistory__category=category,
            usermanagerhistory__date__gte=today,
        ).distinct()

    if not only_managers_history:
        if request.method == 'POST':
            context = {'managers_history': history}
            return render(request, 'channel/inc/find_managers_history_list.html', context=context)
    return history


@login_required
def find_managers(request: WSGIRequest, category_name):
    category = Category.objects.filter(title=category_name).first()
    channels = Channel.objects.filter(categories__in=[category])

    context = {
        'channels': channels,
        'category': category,
        'form_buyer': BuyerForm(),
    }

    now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    last_payment = request.user.payments.filter(date__gte=now - timedelta(days=31)).order_by('-date').first()
    subscription = last_payment.subscription if last_payment else None

    manager_history = UserManagerHistory.objects.filter(user=request.user, date__gte=now)
    manager_history_count = manager_history.count()
    manager_limit = (subscription.managers_per_day if subscription else manager_history_count) - manager_history_count

    if request.method == 'POST':

        form = ChannelForm(request.POST, subscription=subscription, manager_limit=manager_limit)
        if subscription:
            if form.is_valid():

                # find managers
                channel_filter = {
                    change: form.cleaned_data[change]
                    for change in form.changed_data
                    if change in form.channel_filter_keys
                }
                channels = channels.filter(**channel_filter)

                ads = Advertisement.objects.filter(
                    seller__in=channels,
                    date__lte=now - timedelta(days=form.cleaned_data['ads_period_min']),
                    date__gte=now - timedelta(days=form.cleaned_data['ads_period_max']+1),
                ).order_by('-date')
                buyers = Channel.objects.filter(buyer__in=ads)
                managers = Manager.objects.filter(channel__in=buyers).distinct()

                # exclude managers in history
                recent_managers = UserManagerHistory.objects.filter(
                    user=request.user,
                    manager__in=managers,
                    date__gte=now - timedelta(days=20),
                ).values('manager')

                managers = managers.exclude(pk__in=recent_managers)
                managers = managers[:form.cleaned_data['limit']]

                # set limit
                new_manager_limit = manager_limit - managers.count()
                if form.cleaned_data['limit'] > new_manager_limit:
                    form.cleaned_data.update({'limit': new_manager_limit})

                # write managers history
                new_histories = [
                    UserManagerHistory(user=request.user, manager=manager, category=category)
                    for manager in managers
                ]
                UserManagerHistory.objects.bulk_create(new_histories)

                form = ChannelForm(
                    initial=form.cleaned_data,
                    subscription=subscription,
                    manager_limit=new_manager_limit,
                )
                context.update({'managers': managers})

            else:
                messages.error(request, 'Получены некорректные данные.')
        else:
            messages.error(request, 'Для получения менеджеров, необходимо оплатить подписку.')
    else:
        form = ChannelForm(subscription=subscription, manager_limit=manager_limit)

    context.update({
        'form': form,
        'managers_history': managers_history(request, category.id, only_managers_history=True),
    })

    return render(request, 'channel/find_managers.html', context=context)


def buyers_history(request: WSGIRequest):
    if request.method == 'POST':
        form = BuyerForm(request.POST)

        context = {
            'form_buyer': form,
        }
        if form.is_valid():
            text = form.cleaned_data.get('text', '')
            usernames = ['@' + clear_text(username) for username in text.split('@') if username]

            managers = Manager.objects.filter(username__in=usernames)

            # TODO
            residue = None

            new_histories = [UserBuyerHistory(user=request.user, manager=manager) for manager in managers]
            UserBuyerHistory.objects.bulk_create(new_histories)

            context.update({
                'form_buyer': BuyerForm(),
                'form_buyer_text': f'Успешно записано {len(new_histories)} менеджеров',
            })
        return render(request, 'channel/inc/find_managers_buyer_form.html', context=context)
