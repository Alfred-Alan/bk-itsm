# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""  # noqa
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.views.generic import View
from common.mixins.exempt import LoginExemptMixin
from common.responses import ApiV1FailJsonResponse, ApiV1OKJsonResponse
from blueapps.account.models import User
from blueapps.account.utils.token import validate_bk_token, is_request_from_esb
from blueapps.account.constants import ApiErrorCodeEnum


class CheckLoginView(LoginExemptMixin, View):
    def get(self, request):
        # 验证Token参数
        is_valid, user, message = validate_bk_token(request.GET)
        if not is_valid:
            return ApiV1FailJsonResponse(message, code=ApiErrorCodeEnum.PARAM_NOT_VALID)
        return ApiV1OKJsonResponse(_("用户验证成功"), data={'username': user.username})


class UserView(LoginExemptMixin, View):
    def get(self, request):
        # 验证Token参数
        is_valid, user, message = validate_bk_token(request.GET)
        if not is_valid:
            # 如果是ESB的请求，可以直接从参数中获取用户名
            is_from_esb = is_request_from_esb(request)
            username = request.GET.get('username')
            if not is_from_esb or not username:
                return ApiV1FailJsonResponse(message, code=ApiErrorCodeEnum.PARAM_NOT_VALID)
        else:
            username = user.username

        # 获取用户数据
        result, data, message = User.objects.get_user_info(username)
        if not result:
            return ApiV1FailJsonResponse(message, code=ApiErrorCodeEnum.USER_NOT_EXISTS2)

        return ApiV1OKJsonResponse(_("用户信息获取成功"), data=data)
