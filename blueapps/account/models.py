# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import unicode_literals

import datetime
import logging
import random
import traceback

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from blueapps.account import conf
from blueapps.account.utils import sms
from itsm.component.utils.basic import dotted_name
from itsm.role.models import UserRole

ConfFixture = conf.ConfFixture

# 结合获取用户配置的二步验证配置结果
SV_CONF = conf.SECOND_VERIFY_CONF
user_sv_conf = getattr(settings, "SECOND_VERIFY_CONF", {})
SV_CONF.update(user_sv_conf)

logger = logging.getLogger("app")


class UserManager(BaseUserManager):
    def _create_user(
        self,
        username,
        is_staff=False,
        is_superuser=False,
        password=None,
        **extra_fields
    ):
        now = timezone.now()
        if not username:
            raise ValueError(_("The given username must be set"))
        user = self.model(
            username=username,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            date_joined=now,
            **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, False, False, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        return self._create_user(username, True, True, password, **extra_fields)


# class User(AbstractBaseUser, PermissionsMixin):
#     username = models.CharField(
#         _("username"),
#         max_length=64,
#         unique=True,
#         help_text=_(
#             "Required. 64 characters or fewer. Letters, " "digits and underlined only."
#         ),
#         validators=[
#             validators.RegexValidator(
#                 r"^[a-zA-Z0-9_]+$",
#                 _(
#                     "Enter a valid openid. "
#                     "This value may contain only letters, "
#                     "numbers and underlined characters."
#                 ),
#                 "invalid",
#             ),
#         ],
#         error_messages={"unique": _("A user with that openid already exists.")},
#     )
# 
#     nickname = models.CharField(
#         _("nick name"),
#         max_length=64,
#         blank=True,
#         help_text=_("Required. 64 characters or fewer."),
#     )
#     is_staff = models.BooleanField(
#         _("staff status"),
#         default=False,
#         help_text=_("Designates whether the user can log into this " "admin site."),
#     )
#     is_active = models.BooleanField(
#         _("active"),
#         default=True,
#         help_text=_(
#             "Designates whether this user should be treated as "
#             "active. Unselect this instead of deleting accounts."
#         ),
#     )
#     date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
# 
#     objects = UserManager()
# 
#     USERNAME_FIELD = "username"
#     REQUIRED_FIELDS = ["nickname"]
# 
#     class Meta:
#         verbose_name = _("user")
#         verbose_name_plural = _("users")
# 
#         # Pass platform default user table
#         # db_table = 'auth_user'
# 
#     def get_full_name(self):
#         full_name = "{}({})".format(self.username, self.nickname)
#         return full_name.strip()
# 
#     def get_short_name(self):
#         return self.nickname
# 
#     def get_property(self, key):
#         try:
#             return self.properties.get(key=key).value
#         except UserProperty.DoesNotExist:
#             return None
# 
#     def set_property(self, key, value):
#         key_property, _ = self.properties.get_or_create(key=key)
#         key_property.value = value
#         key_property.save()
# 
#     @property
#     def avatar_url(self):
#         return self.get_property("avatar_url")
# 
#     @avatar_url.setter
#     def avatar_url(self, a_url):
#         self.set_property("avatar_url", a_url)
# 
#     def send_sms(self, code):
# 
#         try:
#             result = sms.send_sms([self.username], SV_CONF["SMS_FORMAT"].format(code))
#         except Exception:  # pylint: disable=broad-except
#             logger.error(
#                 "cmsi.send_sms_for_external_user failed. "
#                 "username->[%s], code->[%s] for->[%s]"
#                 % (self.username, code, traceback.format_exc())
#             )
#             return {"result": False, "message": _("ESB发送短信接口错误，可能由权限问题导致")}
#         return {"result": result["result"], "message": result["message"]}
# 
#     def send_code(self):
#         now = timezone.now()
#         v_info = VerifyInfo.objects.filter(user=self)
#         v_info_cnt = v_info.count()
#         if v_info_cnt == 0:
#             # 从未发送过验证码 或 发送过验证码但已被使用（使用后会删除db中的记录）
#             # 生成新的验证码并发送
#             code = random.randint(111111, 999999)
#             VerifyInfo.objects.create(user=self, code=code)
#             ret = self.send_sms(code)
#             if ret["result"]:
#                 ret["message"] = _("初始化验证码，发送成功")
# 
#         elif v_info_cnt == 1:
#             cur = v_info[0]
#             if cur.updated_at >= now - datetime.timedelta(
#                     minutes=SV_CONF["VALID_MINUTES"]
#             ):
#                 # 早前生成过验证码，且未过期
#                 if cur.updated_at < now - datetime.timedelta(
#                         minutes=SV_CONF["RETRY_MINUTES"]
#                 ):
#                     # 重发已生成的
#                     ret = self.send_sms(cur.code)
#                     if ret["result"]:
#                         ret["message"] = _("已生成的验证码，重发成功")
#                 else:
#                     # 等待时间不足，不重发
#                     ret = {"result": False, "message": _("暂不能重发验证码，请稍等")}
#             else:
#                 # 已过期，重新生成并重发
#                 new_code = random.randint(111111, 999999)
#                 cur.code = new_code
#                 cur.save()
#                 ret = self.send_sms(new_code)
#                 if ret["result"]:
#                     ret["message"] = _("重新生成验证码，发送成功")
#         else:
#             logger.error("found more than one code of the user->[%s]" % self.id)
#             ret = {"result": False, "message": _("数据库中的验证码异常")}
#         return ret
# 
#     def verify_code(self, code):
#         check = VerifyInfo.objects.filter(
#             user=self,
#             code=code,
#             updated_at__gt=timezone.now()
#                            - datetime.timedelta(minutes=SV_CONF["VALID_MINUTES"]),
#         ).count()
#         if check == 1:
#             # 一个验证码只能用一次 用完删除
#             VerifyInfo.objects.filter(user=self, code=code).delete()
#             return True
#         return False


from django.utils.http import urlquote
from blueapps.account.manager import (BkUserManager, LoginLogManager)
from blueapps.account.constants import (ROLECODE_CHOICES, RoleCodeEnum, LANGUAGE_CHOICES,
                                        TIME_ZONE_CHOICES)


# class BkRole(models.Model):
#     """
#     角色表
#     """
#     code = models.IntegerField("角色编号", choices=ROLECODE_CHOICES, unique=True)
# 
#     def __unicode__(self):
#         return '%s' % (self.code)
# 
#     class Meta:
#         db_table = "login_bkrole"
#         verbose_name = "用户角色"
#         verbose_name_plural = "用户角色"


class User(AbstractBaseUser, PermissionsMixin):
    """
    BK user

    username and password are required. Other fields are optional.
    """

    username = models.CharField("用户名", max_length=128, unique=True)
    chname = models.CharField("中文名", max_length=254, blank=True)
    qq = models.CharField("QQ号", max_length=32, blank=True)
    phone = models.CharField("手机号", max_length=64, blank=True)
    email = models.EmailField("邮箱", max_length=254, blank=True)
    # role = models.ManyToManyField(UserRole, verbose_name="角色", through='BkUserRole')

    nickname = models.CharField(
        _("nick name"),
        max_length=64,
        blank=True,
        help_text=_("Required. 64 characters or fewer."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this " "admin site."),
    )
    is_active = models.BooleanField(
        _("is_active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    is_wiki_superuser = models.BooleanField(
        _("is_wiki_superuser"),
        default=False,
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = BkUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    # @property
    # def is_staff(self):
    #     return self.is_superuser

    # @property
    # def role_code(self):
    #     role_list = self.role.all().values_list('code', flat=True)
    #     # 多个角色，则已最高角色为主（superuser > developer > staff）
    #     if RoleCodeEnum.SUPERUSER in role_list:
    #         return RoleCodeEnum.SUPERUSER
    #     if RoleCodeEnum.DEVELOPER in role_list:
    #         return RoleCodeEnum.DEVELOPER
    #     if RoleCodeEnum.OPERATOR in role_list:
    #         return RoleCodeEnum.OPERATOR
    #     if RoleCodeEnum.AUDITOR in role_list:
    #         return RoleCodeEnum.AUDITOR
    #     return RoleCodeEnum.STAFF

    @property
    def role_code(self):
        # role_list = self.role.all().values_list('role_key', flat=True)
        role_list = UserRole.objects.filter(members__contains=dotted_name(self.username)).values_list(
            "role_key", flat=True
        )
        return list(role_list)

    @property
    def is_superuser_role(self):
        # return self.role.filter(code=RoleCodeEnum.SUPERUSER).exists()
        return UserRole.is_itsm_superuser(self.username)

    @property
    def wx_userid(self):
        if hasattr(self, 'userinfo') and self.userinfo is not None:
            return self.userinfo.wx_userid if self.userinfo.wx_userid else ''
        return ''

    @property
    def language(self):
        if hasattr(self, 'userinfo') and self.userinfo is not None:
            return self.userinfo.language if self.userinfo.language else ''
        return ''

    @property
    def time_zone(self):
        if hasattr(self, 'userinfo') and self.userinfo is not None:
            return self.userinfo.time_zone if self.userinfo.time_zone else ''
        return ''

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Return the username plus the chinese name, with a space in between
        """
        full_name = '%s %s' % (self.username, self.chname)
        return full_name.strip()

    def get_property(self, key):
        try:
            return self.properties.get(key=key).value
        except UserProperty.DoesNotExist:
            return None

    def set_property(self, key, value):
        key_property, _ = self.properties.get_or_create(key=key)
        key_property.value = value
        key_property.save()

    @property
    def avatar_url(self):
        return self.get_property("avatar_url")

    @avatar_url.setter
    def avatar_url(self, a_url):
        self.set_property("avatar_url", a_url)


# class BkUserRole(models.Model):
#     """
#     用户角色多对多表
#     """
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     role = models.ForeignKey(BkRole, on_delete=models.CASCADE)
#     create_time = models.DateTimeField(_('create_time'), default=timezone.now)
# 
#     def __unicode__(self):
#         return '%s(%s)' % (self.user.username, self.role.code)
# 
#     class Meta:
#         db_table = "login_bkuser_role"
#         verbose_name = "用户角色关系表"
#         verbose_name_plural = "用户角色关系表"


class Loignlog(models.Model):
    """
    User login log
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户", on_delete=models.CASCADE)
    login_time = models.DateTimeField("登录时间")
    login_browser = models.CharField("登录浏览器", max_length=200, blank=True, null=True)
    login_ip = models.CharField("用户登录ip", max_length=50, blank=True, null=True)
    login_host = models.CharField("登录HOST", max_length=100, blank=True, null=True)
    app_id = models.CharField('APP_ID', max_length=30, blank=True, null=True)

    objects = LoginLogManager()

    def __unicode__(self):
        return "%s(%s)" % (self.user.chname, self.user.username)

    class Meta:
        db_table = "login_bklog"
        verbose_name = "用户登录日志"
        verbose_name_plural = "用户登录日志"


class BkToken(models.Model):
    """
    登录票据
    """
    token = models.CharField("登录票据", max_length=255, unique=True, db_index=True)
    # 是否已经退出登录
    is_logout = models.BooleanField("票据是否已经执行过退出登录操作", default=False)
    # 无操作过期时间戳
    inactive_expire_time = models.IntegerField("无操作失效时间戳", default=0)

    def __uincode__(self):
        return self.token

    class Meta:
        db_table = "login_bktoken"
        verbose_name = "登录票据"
        verbose_name_plural = "登录票据"


class UserInfo(models.Model):
    """
    用户信息
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wx_userid = models.CharField("企业号用户USERID/公众号用户OPENID", max_length=64, blank=True, null=True)
    bind_time = models.DateTimeField("微信绑定时间", default=timezone.now, blank=True, null=True)
    language = models.CharField("语言", max_length=32, choices=LANGUAGE_CHOICES, blank=True,
                                null=True)
    time_zone = models.CharField("时区", max_length=32, choices=TIME_ZONE_CHOICES, blank=True,
                                 null=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"
        db_table = 'login_userinfo'


class UserProperty(models.Model):
    """
    Add user extra property
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    key = models.CharField(
        max_length=64,
        help_text=_(
            "Required. 64 characters or fewer. Letters, " "digits and underlined only."
        ),
        validators=[
            validators.RegexValidator(
                r"^[a-zA-Z0-9_]+$",
                _(
                    "Enter a valid key. "
                    "This value may contain only letters, "
                    "numbers and underlined characters."
                ),
                "invalid",
            ),
        ],
    )
    value = models.TextField()

    class Meta:
        verbose_name = _("user property")
        verbose_name_plural = _("user properties")
        db_table = "account_user_property"
        unique_together = (("user", "key"),)


class VerifyInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    updated_at = models.DateTimeField(auto_now=True)
