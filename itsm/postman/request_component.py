# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import json
from abc import abstractmethod

from json import JSONDecodeError

import urllib
import traceback
import requests

from django.conf import settings

from config import APP_ID, APP_TOKEN, RUN_VER

from blueapps.utils import get_request
from common.log import logger
from itsm.component.constants import ResponseCodeStatus
from itsm.component.utils.auth import get_tapd_oauth_url
from itsm.component.utils.sandbox import map_data
from itsm.component.utils.bk_bunch import Bunch, bunchify, unbunchify  # noqa


class BaseClient(object):
    @abstractmethod
    def build_absolute_url(self, path, domain=None):
        raise NotImplementedError

    @abstractmethod
    def get_client(self, data):
        raise NotImplementedError

    def request(self, method, url, params=None, data=None, **kwargs):
        """Send request
        """
        # determine whether access test environment of third-party system
        headers = kwargs.pop('headers', {})

        params, data = self.merge_params_data_with_common_args(
            method, params, data)
        logger.debug(
            'Calling %s %s with params=%s, data=%s, headers=%s',
            method,
            url,
            params,
            data,
            headers)
        return requests.request(method, url, params=params, data=data, verify=False, timeout=20,
                                headers=headers, **kwargs)

    def merge_params_data_with_common_args(
        self, method, params, data
    ):
        """get common args when request
        """
        common_args = dict()
        if method == 'GET':
            _params = common_args.copy()
            _params.update(params or {})
            params = _params
        elif method == 'POST':
            _data = common_args.copy()
            _data.update(data or {})
            data = json.dumps(_data)
        return params, data


class OpenClient(object):

    def __init__(self):
        self.client = BaseClient()

    @classmethod
    def build_absolute_url(cls, path, domain=None):
        system_domain = domain if domain else ''
        return urllib.parse.urljoin(system_domain, path)

    def request(self, method, path, data, domain=None, **kwargs):
        url = self.build_absolute_url(path, domain)
        api_auth = data.pop("api_auth", None)
        if api_auth:
            kwargs.update({"auth": api_auth})

        # 对额外添加的header进行处理
        origin_headers = kwargs.get("headers", {})
        headers = data.pop("headers", {})
        origin_headers.update(headers)
        kwargs["headers"] = origin_headers

        if method == "POST":
            if data.get("content_type") == "text":
                # 发送格式为文本的时候，直接用requests发送请求
                res = self.raw_post_request(url, data=data.get("raw", ""), **kwargs)
            else:
                res = self.client.request("POST", url, data=data, **kwargs)
        else:
            res = self.client.request("GET", url, params=data, **kwargs)

        if not res:
            message = "empty response: {}".format(url)
            # 获取tapd授权链接
            if settings.ITSM_TAPD_APIGW and settings.ITSM_TAPD_APIGW in url:
                workspace_id = data.get("workspace_id", "")
                message = get_tapd_oauth_url(workspace_id)
            return {
                "result": False,
                "message": message,
                "data": {},
            }

        try:
            return res.json()
        except JSONDecodeError:
            logger.warning("[{}]: JSONDecodeError".format(url))
            return {
                "result": False,
                "message": "not support invalid json response: {}".format(url),
                "data": {},
            }

    @staticmethod
    def raw_post_request(url, data, **kwargs):
        """
        支持原生的text请求方式
        :param url: 请求链接
        :param data: 请求数据
        :param kwargs: 其他参数
        :return:
        """

        return requests.request(
            "POST",
            url,
            data=data,
            verify=False,
            timeout=20,
            headers=kwargs.get("headers"),
            **kwargs
        )


class BkComponent(object):
    def __init__(self):
        self.client = OpenClient()

    def http(self, config):

        # post.body or get.query_params
        query_params = config.get("query_params")
        path = config.get("path")
        method = config.get("method")
        system_domain = config.get("system_domain")
        map_code = config.get("map_code")
        before_req = config.get("before_req")
        rsp_data = config.get("rsp_data")
        kwargs = {'headers': config.get('headers', {})}

        # 请求参数预处理
        if before_req:
            try:
                query_params = map_data(before_req, query_params, "query_params")
            except Exception:
                return {
                    "result": False,
                    "message": traceback.format_exc().split("\n")[-2],
                    "data": {},
                }

        try:
            response = self.client.request(
                method, path, query_params, system_domain, **kwargs
            )
        except Exception as e:
            logger.error("[{}] response.Exception: {}".format(path, e))
            return {
                "result": False,
                "message": str(e),
                "data": {},
            }

        # 返回结果后处理
        if map_code:
            try:
                response = map_data(map_code, response, "response")
            except Exception:
                return {
                    "result": False,
                    "message": traceback.format_exc().split("\n")[-2],
                    "data": {},
                }

        if response.get("result", False) and rsp_data:
            return {
                "result": True,
                "message": "success",
                "code": ResponseCodeStatus.OK,
                "data": self.handle_response(response, rsp_data),
            }

        return response

    def handle_response(self, response, rsp_data):
        """提取response中的字段值，比如
        rsp_data = 'data.info'
        return reponse['data']['info']
        """
        data = {}
        for attr in rsp_data.split(","):
            if not attr:
                continue

            try:
                handle_code = (
                    "handle_data = unbunchify(bunchify(response).{rsp_data})".format(
                        rsp_data=attr
                    )
                )
                exec(handle_code)
                data[attr] = locals()["handle_data"]
            except AttributeError as e:
                logger.warning(
                    "handle_response attribute_error[{}]: {}".format(attr, e)
                )
                data[attr] = ""

        return data


bk = BkComponent()
