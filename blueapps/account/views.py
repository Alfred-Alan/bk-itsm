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


from django.conf import settings
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse, QueryDict
from django.shortcuts import render
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _
from django.views.generic import View, TemplateView

from common.log import logger
from common.mixins.base import SuperuserRequiredMixin, SuperuserOrPutOwnerRequiredMixin
from common.mixins.exempt import LoginExemptMixin
from common.responses import FailJsonResponse, OKJsonResponse
from blueapps.account.utils.basic import first_error_message
from blueapps.account.accounts import Account
from blueapps.account.forms import UserInfoForm, SetPasswordForm, UserQueryForm, ImportUserForm
from blueapps.account.models import User
from blueapps.account.utils.user import (get_page_info)


class UserPageView(TemplateView):
    """
    用户管理页面
    """
    template_name = "bkaccount/users.html"

    def get_context_data(self, **kwargs):
        context = super(UserPageView, self).get_context_data(**kwargs)
        request = self.request

        context.update({
            'default_paasword': settings.PASSWORD,
            'error_msg': request.GET.get('error_msg') or '',
            'success_msg': request.GET.get('success_msg') or ''
        })
        return context


class UserListPage(TemplateView):
    """
    用户信息列表页面
    """
    template_name = "bkaccount/user_table.part"

    def get_context_data(self, **kwargs):
        context = super(UserListPage, self).get_context_data(**kwargs)
        request = self.request

        form = UserQueryForm(request.GET)
        form.is_valid()

        page = form.cleaned_data["page"]
        page_size = form.cleaned_data["page_size"]
        page, page_size = get_page_info(page, page_size)

        # 管理员查看所有用户，无需过滤
        search_username = '' if request.user.is_superuser else request.user.username
        # 根据查询条件过滤
        search_data = form.cleaned_data["search_data"]
        search_role = form.cleaned_data["search_role"]

        # 获取分页数据
        records = User.objects.get_batch_user_with_paginator(page, page_size, search_username,
                                                             search_data, search_role)

        # 前端分页临近页数，默认设置为 3
        adjacent_pages = 3
        start_page = max(records.number - adjacent_pages, 1)
        start_page = 1 if start_page < adjacent_pages else start_page
        end_page = records.number + adjacent_pages + 1
        if end_page > records.paginator.num_pages - adjacent_pages + 2:
            end_page = records.paginator.num_pages + 1
        page_numbers = [n for n in range(start_page, end_page)]
        show_first = 1 not in page_numbers
        show_last = records.paginator.num_pages not in page_numbers
        context.update({
            'records': records,
            'page_numbers': page_numbers,
            'show_first': show_first,
            'show_last': show_last,
        })
        return context


class UserView(SuperuserOrPutOwnerRequiredMixin, View):
    """
    CUD User
    """

    def _add_or_update(self, request, user_id=None):
        request_param = request.POST if user_id is None else QueryDict(request.body)
        form = UserInfoForm(request_param)

        if not form.is_valid():
            message = first_error_message(form)
            return FailJsonResponse(message)

        # 创建用户
        result, user_id, message = User.objects.modify_or_create_user_by_userid(
            user_id,
            form.cleaned_data["username"],
            form.cleaned_data["chname"],
            form.cleaned_data["phone"],
            form.cleaned_data["email"],
        )
        print(result)
        if not result:
            return FailJsonResponse(message)
        return OKJsonResponse(_("保存用户信息成功"), data={"user_id": user_id})

    def post(self, request):
        return self._add_or_update(request, None)

    def put(self, request, user_id):
        return self._add_or_update(request, user_id)

    def delete(self, request, user_id):
        result, message = User.objects.delete_user(user_id)
        if not result:
            return FailJsonResponse(message)
        return OKJsonResponse(_("用户删除成功"))


class UserPasswordView(SuperuserOrPutOwnerRequiredMixin, View):
    def put(self, request, user_id):
        request_param = QueryDict(request.body)
        form = SetPasswordForm(request_param)

        if not form.is_valid():
            message = first_error_message(form)
            return FailJsonResponse(message)

        # 修改密码
        result, message = User.objects.modify_password_by_userid(user_id,
                                                                 form.cleaned_data['new_password1'])
        if not result:
            return FailJsonResponse(message)
        return OKJsonResponse(_("修改密码成功"))
