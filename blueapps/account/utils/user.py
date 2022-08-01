from blueapps.account.constants import ROLECODE_CHOICES
from blueapps.utils.logger import logger

from django.utils.translation import ugettext as _


def get_page_info(page, page_size, default_page_size=10):
    try:
        page = int(page)
        page_size = int(page_size)

        if page < 1:
            page = 1
        if page_size < 1:
            page_size = default_page_size
    except Exception:
        page = 1
        page_size = default_page_size

    return page, page_size


def get_role_code_by_role_name(role_name):
    """
    将角色名转换为角色编码
    """
    role_name_code_dict = dict([(_(i[1]), i[0]) for i in ROLECODE_CHOICES])
    try:
        role_name = u"%s" % role_name
        role_code = role_name_code_dict.get(role_name)
    except Exception as error:
        logger.exception("role name conversion role code error: {}".format(error))
        role_code = None
    return role_code


def get_role_name_by_role_code(role_code):
    """
    将角色编码转换为角色名
    """
    role_code_name_dict = dict(ROLECODE_CHOICES)
    return _(role_code_name_dict.get(role_code, ''))
