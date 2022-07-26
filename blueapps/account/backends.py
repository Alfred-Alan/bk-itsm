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
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from blueapps.account.accounts import Account
from blueapps.account.conf import ConfFixture
from blueapps.account.utils import load_backend


class BkBackend(ModelBackend):
    """
    自定义认证方法
    """

    def authenticate(self, request):
        print("BkBackend")
        account = Account()
        login_status, username, message = account.is_bk_token_valid(request)
        if not login_status:
            return None

        user_model = get_user_model()
        try:
            user = user_model._default_manager.get_by_natural_key(username)
        except user_model.DoesNotExist:
            user = None
        return user


if hasattr(ConfFixture, "USER_BACKEND"):
    UserBackend = load_backend(ConfFixture.USER_BACKEND)

if hasattr(ConfFixture, "WEIXIN_BACKEND"):
    WeixinBackend = load_backend(ConfFixture.WEIXIN_BACKEND)

if hasattr(ConfFixture, "RIO_BACKEND"):
    RioBackend = load_backend(ConfFixture.RIO_BACKEND)

if hasattr(ConfFixture, "BK_JWT_BACKEND"):
    BkJwtBackend = load_backend(ConfFixture.BK_JWT_BACKEND)
