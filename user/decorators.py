from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test


def check_user_not_authenticated(user):
    return not user.is_authenticated


def not_auth_user_required(view_func, login_url='/profile'):
    decorated_view_func = user_passes_test(
        check_user_not_authenticated,
        login_url=login_url,
        redirect_field_name=None
    )(view_func)
    return decorated_view_func