# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from __future__ import unicode_literals

from django.db import migrations

from blueapps.account.constants import RoleCodeEnum


def load_data(apps, schema_editor):
    """
    初始化已存在的用户的角色
    """
    try:
        user_model = apps.get_model("account", "User")
        BkRole = apps.get_model("account", "BkRole")
        BkUserRole = apps.get_model("account", "BkUserRole")
        # 获取普通用户和超级用户角色
        staff = BkRole.objects.get(code=RoleCodeEnum.STAFF)
        superuser = BkRole.objects.get(code=RoleCodeEnum.SUPERUSER)
        role_list = [staff, superuser]
        all_user = user_model.objects.all()
        bkuser_role_list = []
        for i in all_user:
            if not i.role.all().count():
                # 沿用用户之前角色
                bkuser_role_list.append(BkUserRole(user=i, role=role_list[int(i.is_superuser)]))
        if bkuser_role_list:
            BkUserRole.objects.bulk_create(bkuser_role_list)
    except Exception as error:
        print(error)


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_initial_role'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]
