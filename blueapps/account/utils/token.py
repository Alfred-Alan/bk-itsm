from django.utils.translation import ugettext as _
from blueapps.account.accounts import Account
from blueapps.conf import settings
from blueapps.account.models import User


def validate_bk_token(request):
    """
    检查bk_token的合法性，并返回用户实例
    """
    account = Account()
    bk_token = request.GET.get(account.BK_COOKIE_NAME)
    if not bk_token:
        bk_token = request.COOKIES.get('bk_token', '')
    # 验证Token参数
    is_valid, username, message = account._is_bk_token_valid(bk_token)
    if not is_valid:
        return False, None, message
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False, None, _("用户不存在")
    return True, user, ''


def is_request_from_esb(request):
    """
    请求是否来自ESB
    """
    x_app_token = request.META.get('HTTP_X_APP_TOKEN')
    x_app_code = request.META.get('HTTP_X_APP_CODE')
    return x_app_code == 'esb' and x_app_token == settings.ESB_TOKEN
