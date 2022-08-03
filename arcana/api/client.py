# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import unicode_literals
import time
import json
import logging

from cachetools import cached, TTLCache
from requests.models import PreparedRequest

from .http import http_get, http_post, http_put, http_delete

logger = logging.getLogger("arcana")


class Client(object):
    """
    input: json
    """

    def __init__(self, token, arcana_host):
        self._token = token
        self._host = arcana_host

    def _call_api(self, http_func, host, path, data, headers, timeout=None):
        url = "{host}{path}".format(host=host, path=path)

        begin = time.time()

        # if debug, add ?debug=True in url
        if logger.isEnabledFor(logging.DEBUG):
            preReq = PreparedRequest()
            preReq.prepare_url(url, {"debug": "true"})
            url = preReq.url

        ok, _data = http_func(url, data, headers=headers, timeout=timeout)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("do http request: method=`%s`, url=`%s`, data=`%s`", http_func.__name__,
                         url, json.dumps(data))
            logger.debug("http request result: ok=`%s`, _data=`%s`", ok, json.dumps(_data))
            logger.debug("http request took %s ms", int((time.time() - begin) * 1000))

        if not ok:
            return False, "verify from arcana server fail", None

        return True, "ok", _data

    def _call_arcana_api(self, http_func, path, data, timeout=None):
        headers = {
            "Cookie": "ticket={token}".format(token=self._token)
        }
        return self._call_api(http_func, self._host, path, data, headers, timeout=timeout)

    def save_json(self, file_path, data):
        with open(file_path, "w", encoding="utf-8")as f:
            f.write(json.dumps(data, indent=4, ensure_ascii=False))

    def permission_group(self):
        """
        获取用户组权限
        """
        path = "/arcana-api/services/authentication/current-context"
        ok, message, data = self._call_arcana_api(http_get, path, None)
        return ok, message, data


if __name__ == '__main__':
    a = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzc29BdXRoIjoiIiwidG9rZW5JZCI6IiIsInVzZXJOYW1lIjoibGpxIiwiZXhwIjoxNjYwMDM0MDUwfQ.qtJ_u6yP1LdCwMqnoWCgs8Q1waBLhhcoQ5HgVvtGu94'
    client = Client(a, 'http://192.168.100.244:7088')
    res = client.permission_group()
    print(res)
