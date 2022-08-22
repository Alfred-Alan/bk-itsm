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
import hashlib
import logging
import random
import traceback

from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core import validators
from django.core.cache import cache
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.utils.http import urlquote
from arcana.utils import ArcanaRequest
from blueapps.account.manager import (BkUserManager, LoginLogManager)
from blueapps.account.constants import (ROLECODE_CHOICES, RoleCodeEnum, LANGUAGE_CHOICES,
                                        TIME_ZONE_CHOICES)
from blueapps.account import conf
from itsm.component.constants import PREFIX_KEY, CACHE_10MIN

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


class BkRole(models.Model):
    """
    角色表
    """
    code = models.IntegerField("角色编号", choices=ROLECODE_CHOICES, unique=True)

    def __unicode__(self):
        return '%s' % (self.code)

    class Meta:
        db_table = "login_bkrole"
        verbose_name = "用户角色"
        verbose_name_plural = "用户角色"


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
    role = models.ManyToManyField(BkRole, verbose_name="角色", through='BkUserRole')

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
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = BkUserManager()
    bulk_objects = BulkUpdateOrCreateQuerySet.as_manager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def role_code(self):
        role_list = self.role.all().values_list('code', flat=True)
        # 多个角色，则已最高角色为主（superuser > developer > staff）
        if RoleCodeEnum.SUPERUSER in role_list:
            return RoleCodeEnum.SUPERUSER
        if RoleCodeEnum.DEVELOPER in role_list:
            return RoleCodeEnum.DEVELOPER
        if RoleCodeEnum.OPERATOR in role_list:
            return RoleCodeEnum.OPERATOR
        if RoleCodeEnum.AUDITOR in role_list:
            return RoleCodeEnum.AUDITOR
        return RoleCodeEnum.STAFF

    @property
    def is_superuser_role(self):
        return self.role.filter(code=RoleCodeEnum.SUPERUSER).exists()
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

    @classmethod
    def update_arcana_users(cls, request):
        arcana_client = ArcanaRequest(request)
        users = arcana_client.fetch_users({
            "offset": 0,
            "sortField": "",
            "sortDirection": 0,
            "keyword": "",
            "group": ""
        })
        usernames = [user['username'] for user in users]
        user_md5 = hashlib.md5(str(usernames).encode()).hexdigest()
        cache_key = "{}usernames_{}".format(PREFIX_KEY, user_md5)
        ac_users = cache.get(cache_key)
        if ac_users:
            return None

        # 取不到代表有新增用户
        try:
            with transaction.atomic():
                users = [cls(username=user['username'], nickname=user['username']) for user in
                         users]
                cls.bulk_objects.bulk_update_or_create(users, ['username', 'nickname'],
                                                       match_field='username')
                cache.set(cache_key, usernames, CACHE_10MIN)
        except Exception as err:
            logger.exception(u"自动创建 & 更新 User Model 失败: %s" % err)
            return None


class BkUserRole(models.Model):
    """
    用户角色多对多表
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(BkRole, on_delete=models.CASCADE)
    create_time = models.DateTimeField(_('create_time'), default=timezone.now)

    def __unicode__(self):
        return '%s(%s)' % (self.user.username, self.role.code)

    class Meta:
        db_table = "login_bkuser_role"
        verbose_name = "用户角色关系表"
        verbose_name_plural = "用户角色关系表"


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
