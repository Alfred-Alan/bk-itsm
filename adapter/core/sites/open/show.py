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

import os
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# if settings.OPEN_VER == "enterprise":
#     TITLE = "{} | {}".format(_("流程服务"), _("腾讯蓝鲸智云"))
#     DOC_URL = get_doc_url()
# else:


def get_title():
    # TITLE = "{} | {}".format(_("流程服务"), _("腾讯蓝鲸智云"))
    TITLE = "{}".format(_("流程服务"))
    return TITLE


def get_footer():
    FOOTER = """
            <div class="copyright">
                <ul class="link-list">
                </ul>
                <div class="desc">Copyright &copy; 2012-${year} Di-Matrix. All Rights Reserved.V2.6.1</div>
            </div>
            """
    return FOOTER


LOGIN_URL = "/login/"
