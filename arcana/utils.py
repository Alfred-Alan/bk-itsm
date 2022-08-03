import os
import json
from django.conf import settings
from django.core.cache import cache
from blueapps.utils import get_request

from common.log import logger
from itsm.component.constants import (
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.exceptions import IamGrantCreatorActionError
from itsm.project.models import Project
from itsm.workflow.models import TemplateField

from arcana.api.client import Client, logger
from iam.exceptions import AuthAPIError
from itsm.component.constants import CACHE_30MIN


class ArcanaRequest(object):
    """
    input: object
    """

    def __init__(self, request):
        token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzc29BdXRoIjoiIiwidG9rZW5JZCI6IiIsInVzZXJOYW1lIjoibm9pdHNtIiwiZXhwIjoxNjYwMTE1MzM0fQ.coIGKP4c1d382dTNZkjbiPGP_yXJO_-036-djP9Irw4'
        self.arcana_host = settings.ARCANA_INNER_HOST
        self._client = Client(token, self.arcana_host)
        self.request = request
        self.username = request.user.username
    
    def _permission_query(self): # noqa
        """
        获取itsm权限
        """
        ok, message, data = self._client.permission_group()
        if not ok:
            raise AuthAPIError(message)
        initial_actions = self.get_initial_actions()
        action_ids = [action['id'] for action in initial_actions]
        actions = []
        for user_group in data.get('groups', []):
            for permissions in user_group.get('permission', []):
                for child in permissions.get('child', []):
                    if child['value'] not in action_ids:
                        continue
                    actions.append({
                        'id': child['value'],
                        'name': child['name'],
                    })

        return actions

    def _do_policy_query(self):
        action_policies = self._permission_query()
        return action_policies

    def _do_policy_query_by_actions(self, actions: []):
        """
        指定action查找权限
        """
        action_policies = self._permission_query()
        return list(filter(lambda a: a['id'] in actions, action_policies))
    
    def multi_actions_allowed(self, actions: []):
        """
        批量操作鉴权
        """
        actions_allowed = {}
        try:
            action_policies = self._do_policy_query_by_actions(actions)
        except Exception as error:
            logger.exception(error)
            action_policies = []
        logger.debug("the return policies: %s", action_policies)
        if not action_policies:
            logger.debug("no return policies, will reject all perms")
            for action in actions:
                actions_allowed[action] = False
            return actions_allowed
        
        # 所需权限和已有权限鉴权
        for action_policy in action_policies:
            action = action_policy["id"]
            actions_allowed[action] = action in actions

        return actions_allowed

    def export_json(self, file_path):
        data = {}
        if not os.path.exists(file_path):
            return data
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
        except Exception as error:
            logger.exception(error)
        return data

    def get_or_update_actions(self):
        data = self.export_json('arcana/initial_permission.json')
        actions = []
        for permission in data.get('permission', []):
            for child in permission.get('child', []):
                actions.append({
                    'id': child['value'],
                    'name': child['name'],
                })
        return actions

    def get_initial_actions(self):
        """获取初始权限"""
        cache_key = "initial_actions"
        actions = cache.get(cache_key)
        if not actions:
            actions = self.get_or_update_actions()
            cache.set(cache_key, actions, CACHE_30MIN)
        return cache.get(cache_key)

