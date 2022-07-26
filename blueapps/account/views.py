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

import time

from django.http import JsonResponse
from django.middleware import csrf
from blueapps.account.decorators import login_exempt
from django.conf import settings
from django.shortcuts import render
from django.utils.module_loading import import_string
from blueapps.account.accounts import Account

import json

from django.views.generic import View

from common.mixins.exempt import LoginExemptMixin
from common.responses import ApiV1FailJsonResponse, ApiV1OKJsonResponse

from blueapps.account.models import User
from blueapps.account.utils.token import validate_bk_token, is_request_from_esb
from blueapps.account.constants import ApiErrorCodeEnum


class LoginView(LoginExemptMixin, View):
    """
    登录
    """

    def _login(self, request):
        account = Account()
        # 判断调用方式
        if settings.LOGIN_TYPE != 'custom_login':
            return account.login(request)
        # 调用自定义login view
        custom_login_view = import_string(settings.CUSTOM_LOGIN_VIEW)
        return custom_login_view(request)

    def get(self, request):
        return self._login(request)

    def post(self, request):
        return self._login(request)


class LogoutView(LoginExemptMixin, View):
    """
    登出
    """

    def get(self, request):
        account = Account()
        return account.logout(request)


@login_exempt
def login_success(request):
    """
    弹框登录成功返回页面
    """
    return render(request, "account/login_success.html")


@login_exempt
def login_page(request):
    """
    跳转至固定页面，然后弹框登录
    """
    refer_url = request.GET.get("refer_url")

    context = {"refer_url": refer_url}
    return render(request, "account/login_page.html", context)


def send_code_view(request):
    ret = request.user.send_code()
    return JsonResponse(ret)


def get_user_info(request):
    return JsonResponse(
        {
            "code": 0,
            "data": {
                "id": request.user.id,
                "username": request.user.username,
                "timestamp": time.time(),
            },
            "message": "ok",
        }
    )


def get_csrf_token(request):
    """
    前端获取csrf_token接口
    """
    csrf_token = csrf.get_token(request)
    return JsonResponse({"csrf_token": csrf_token})
