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

import os

__all__ = ["OAUTH_API_URL", "OAUTH_COOKIES_PARAMS", "OAUTH_PARAMS"]

OAUTH_API_URL = os.getenv("BKPAAS_APIGW_OAUTH_API_URL", "")
OAUTH_COOKIES_PARAMS = {"uin": "p_uin", "skey": "p_skey"}
OAUTH_PARAMS = {"bk_env": "tencent"}
