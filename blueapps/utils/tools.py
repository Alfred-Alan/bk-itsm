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


def get_app_host_by_request(request):
    """通过request对象拼接 app_host 访问地址"""
    return f'{request.META["wsgi.url_scheme"]}://{request.META["HTTP_HOST"]}{request.META["SCRIPT_NAME"]}'


def resolve_login_url(url, request=None, fix_scheme=None):
    """根据网络协议解析url"""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if fix_scheme:
        return f"{fix_scheme}://{url}"
    scheme = getattr(request, "scheme", "http")
    return f"{scheme}://{url}"
