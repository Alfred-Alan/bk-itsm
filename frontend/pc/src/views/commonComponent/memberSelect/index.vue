<!--
  - Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
  -
  - License for BK-ITSM 蓝鲸流程服务:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <div :class="[extCls]" test-posi-id="bk-member-selector">
    <bk-user-selector
      :value="value"
      class="ui-user-selector"
      :fixed-height="true"
      :disabled="disabled"
      :multiple="multiple"
      :placeholder="placeholder"
      :fuzzy-search-method="fuzzySearchMethod"
      :exact-search-method="exactSearchMethod"
      @change="onChange">
    </bk-user-selector>
  </div>
</template>

<script>
  import BkUserSelector from '@blueking/user-selector';
  import i18n from '@/i18n/index.js';

  export default {
    name: 'MemberSelector',
    components: {
      BkUserSelector,
    },
    model: {
      prop: 'value',
      event: 'change',
    },
    props: {
      /**
       * 指定的人员 id
       * 配置了该数组，就只能在该人员列表中选择
       */
      specifyIdList: {
        type: Array,
        default() {
          return [];
        },
      },
      placeholder: {
        type: String,
        default: i18n.t('m.newCommon["请选择"]'),
      },
      disabled: {
        type: Boolean,
        default: false,
      },
      // 多选
      multiple: {
        type: Boolean,
        default: true,
      },
      value: {
        type: Array,
        default() {
          return [];
        },
      },
      // 外部设置的 class name
      extCls: {
        type: String,
        default: '',
      },
    },
    data() {
      return {
        customUserList: [],
        users: [],
      };
    },
    computed: {
      api() {
        const host = location.origin;
        return `${host}/accounts/`;
      },
    },
    created() {
    },
    methods: {
      // 精确搜索
      async exactSearchMethod(usernames) {
        if (!Array.isArray(usernames)) {
          return;
        }
        this.customUserList = [];
        const res = await this.$store.dispatch('user/getAllUser', { exact_lookups: usernames.join(',') });
        if (!res.result) {
          this.$bkMessage({
            message: '用户拉取失败',
            theme: 'success',
          });
        } else {
          this.customUserList = res.data;
        }
        return this.getUserInfo(usernames);
      },
      // 查询指定 id 用户信息
      getUserInfo(username) {
        const isArray = Array.isArray(username);
        const usernames = isArray ? username : [username];
        const users = [];
        usernames.forEach(keyword => {
          this.customUserList.forEach(item => {
            const names = item.username + item.display_name;
            if (names.indexOf(keyword) > -1) {
              users.push(item);
            }
          });
        });
        return users;
      },
      // 模糊搜索匹配值，有 dataList 时生效
      async fuzzySearchMethod(keyword) {
        if (!keyword) {
          return;
        }
        this.customUserList = [];
        const res = await this.$store.dispatch('user/getAllUser', { keyword });
        if (!res.result) {
          this.$bkMessage({
            message: '用户拉取失败',
            theme: 'success',
          });
        } else {
          this.customUserList = res.data;
        }
        return Promise.resolve({
          next: false,
          results: this.getUserInfo(keyword),
        });
      },
      onChange(value) {
        this.$emit('change', value);
      },
    },
  };
</script>

<style lang="scss" scoped>
    .ui-user-selector {
        width: 100%;
    }
</style>
