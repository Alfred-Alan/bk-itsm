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
  <div :class="{ 'bk-fields-done': true, 'bk-fields-log': origin === 'log' }" :key="routerKey">
    <!-- table -->
    <div v-if="item.type === 'TABLE'" class="bk-fields-done-item" style="width: 100%; max-width: 100%;">
      <span class="bk-li-left" :title="item.name">{{item.name}}</span>
      <div v-if="item.can_edit && !basicInfomation.is_over && origin === 'notLog'" class="bk-fields-done-edit"
        @click="edit(item)">
        <span class="bk-itsm-icon icon-edit-bold isOn"></span>
      </div>
      <div class="bk-form-content bk-over-more" style="margin-left: 0px;" v-if="item.value">
        <bk-table :data="getParseValue(item.value)"
          :size="'small'">
          <template v-for="title in item.choice">
            <bk-table-column :label="title.name" :key="title.key">
              <template slot-scope="props">
                <span :title="props.row[title.key]">{{ props.row[title.key] }}</span>
              </template>
            </bk-table-column>
          </template>
        </bk-table>
      </div>
    </div>
    <!--  custom table  -->
    <div v-else-if="item.type === 'CUSTOMTABLE'" class="bk-fields-done-item" style="width: 100%; max-width: 100%;">
      <span v-if="isShowName" class="bk-li-left" :title="item.name">{{item.name}}</span>
      <div v-if="item.can_edit && !basicInfomation.is_over && origin === 'notLog'" class="bk-fields-done-edit"
        @click="edit(item)">
        <span class="bk-itsm-icon icon-edit-bold isOn"></span>
      </div>
      <div class="bk-form-content bk-over-more" style="margin-left: 0px; width: 100%;" v-if="item.value">
        <bk-table :data="item.value"
          :size="'small'">
          <template v-for="(column) in item.meta.columns">
            <bk-table-column :label="column.name" :key="column.key">
              <template slot-scope="props">
                <span :title="props.row[column.key]">{{ getCustomTableDisplayValue(column, props.row) || '--' }}</span>
              </template>
            </bk-table-column>
          </template>
        </bk-table>
      </div>
    </div>
    <!-- select -->
    <div v-else-if="item.type === 'SELECT'" class="bk-fields-done-item">
      <span v-if="isShowName" class="bk-li-left" :title="item.name">{{item.name}}</span>
      <span class="bk-li-right" :title="item.display_value">
        <span class="bk-pot-after">{{item.display_value || '--'}}</span>
      </span>
    </div>
    <!-- 修改 附件处理 10/31-->
    <div v-else-if="item.type === 'FILE'" class="bk-fields-done-item">
      <span v-if="isShowName" class="bk-li-left" :title="item.name">{{item.name}}</span>
      <span v-for="(file, index) in fileList"
        :key="index"
        class="bk-li-right"
        :style="cursorStyle"
        @click="downFile(file)">
        <i v-if="item.value !== ''"
          style="color: rgb(60, 150, 255)"
          class="bk-icon icon-download bk-tab-cursor">
        </i>
        {{file.name}}
      </span>
    </div>
    <!-- 富文本 -->
    <div v-else-if="item.type === 'RICHTEXT'" class="bk-fields-done-item">
      <span v-if="isShowName" class="bk-li-left" style="float: initial;" :title="item.name">{{item.name}}</span>
      <div class="bk-li-right bk-fields-richtext tui-editor-contents"
        v-html="item.value" :title="item.value.replace(/<[^>]+>/g, '')">
      </div>
    </div>
    <!-- 多行文本展现出后台保存的内容格式 -->
    <div v-else-if="item.type === 'TEXT'" class="bk-fields-done-item">
      <span v-if="isShowName" class="bk-li-left" :title="item.name">{{item.name}}</span>
      <span class="bk-li-right"
        :title="item.display_value">
        <pre class="bk-pre">{{item.display_value || item.value || '--'}}</pre>
      </span>
    </div>
    <!-- 链接 -->
    <div v-else-if="item.type === 'LINK'" class="bk-fields-done-item">
      <span class="bk-li-left" :title="item.name">{{item.name}}</span>
      <span class="bk-li-right" :title="item.value">
        <span class="bk-pot-after bk-li-link" @click="goToLink(item.value)">{{ $t('m.newCommon["点击查看"]') }}</span>
      </span>
    </div>
    <!-- 自定义表单 -->
    <div v-else-if="item.type === 'CUSTOM-FORM'" class="bk-fields-done-item">
      <span v-if="isShowName" class="bk-li-left" style="float: initial;" :title="item.name">{{item.name}}</span>
      <render-view
        style="width: calc(100% - 140px)"
        :form-data="customForm.formData"
        :context="customForm.context">
      </render-view>
    </div>
    <!-- 默认 -->
    <div class="bk-fields-done-item" v-else>
      <span v-if="isShowName" class="bk-li-left" :title="item.name">{{item.name}}</span>
      <business-card
        v-if="(item.type === 'MEMBERS' || item.type === 'MEMBER') && origin === 'notLog'"
        style="margin-top: 3px"
        :item="item">
      </business-card>
      <span class="bk-li-right"
        :class="{ 'pl5': (item.type === 'MEMBERS' || item.type === 'MEMBER') && origin === 'notLog' }"
        :title="item.display_value">{{item.display_value || item.value || '--'}}
      </span>
    </div>
    <!-- 编辑 -->
    <div v-if="item.can_edit && !basicInfomation.is_over && !['TABLE', 'CUSTOMTABLE'].includes(item.type)"
      class="bk-fields-done-edit"
      :class="{ 'bk-member-edit': ((item.type === 'MEMBERS' || item.type === 'MEMBER') && origin === 'notLog') }"
      @click="edit(item)">
      <span class="bk-itsm-icon icon-edit-bold isOn"></span>
    </div>
  </div>
</template>
<script>
  import businessCard from '@/components/common/BusinessCard.vue';
  import RenderView from '@/components/renderview/RenderView';
  import { appendTargetAttrToHtml } from '@/utils/util';
  import { getCustomTableDisplayValue } from '@/components/RenderField/fieldUtils';

  export default {
    name: 'fieldsDone',
    components: {
      businessCard,
      RenderView,
    },
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      fields: {
        type: Array,
        required: false,
        default: () => [],
      },
      ticketId: {
        type: [Number, String],
        required: false,
        default: () => '',
      },
      statedId: {
        type: [Number, String],
        required: false,
        default: () => '',
      },
      commentId: {
        type: String,
        required: false,
        default: () => '',
      },
      item: {
        type: Object,
        default() {
          return {};
        },
      },
      origin: {
        type: String,
        required: false,
        default: () => 'notLog',
      },
      isShowName: {
        type: Boolean,
        default: () => true,
      },
      basicInfoType: Array,
    },
    data() {
      return {
        showMore: false,
        showInfo: true,
        downFileUrl: '',
        routerKey: +new Date(),
        cursorStyle: {
          cursor: 'pointer',
        },
        fileList: [],
        customForm: {
          formData: [],
          context: {},
        },
      };
    },
    computed: {
      profile() {
        if (!this.basicInfomation) {
          return;
        }
        return {
          name: this.basicInfomation.profile.name,
          phone: this.basicInfomation.profile.phone,
          department: this.basicInfomation.profile.departments ? this.basicInfomation.profile.departments : [],
        };
      },
      fieldType() {
        return this.basicInfoType ? this.basicInfoType.includes(this.item.type) : [];
      },
    },
    created() {
      if (this.item.type === 'CUSTOM-FORM') {
        const data = typeof this.item.value === 'string' ? JSON.parse(this.item.value) : this.item.value;
        const { form_data, schemes, config } = data;
        this.customForm = {
          formData: form_data,
          context: { schemes, config },
        };
      }
    },
    mounted() {
      this.$set(this.item, 'isEdit', false);
      this.reloadCurPage();
      if (this.item.type === 'FILE') {
        this.valToList();
      }
      if (this.item.type === 'RICHTEXT') {
        // 这里可以兼容之前创建的 a 标签没加 _blank 的 value,显示时加上
        this.item.value = appendTargetAttrToHtml(this.item.value).replace(/<p>/g, '<p class="rich-text">');
      }
    },
    methods: {
      goToLink(url) {
        if (url.indexOf('http') !== 0) {
          url = `http://${url}`;
        }
        window.open(url, '_blank');
      },
      valToList() {
        const value = this.item.value;
        const tempObj = value ? JSON.parse(value) : {};
        for (const key in tempObj) {
          this.fileList.push({ ...tempObj[key], key });
        }
      },
      reloadCurPage() {
        this.routerKey = +new Date();
      },
      edit() {
        this.fields.forEach(ite => {
          ite.isEdit = false;
        });
        this.$set(this.item, 'isEdit', true);
      },
      // 11.01 修改 附件上传
      downFile(file) {
        this.downFileUrl = `${window.SITE_URL}api/ticket/fields/${this.item.id}/download_file/?unique_key=${file.key}&file_type=ticket`;
        window.open(this.downFileUrl);
      },
      // 解析字符串为数组-特定表格数据场景
      getParseValue(val) {
        if (Array.isArray(val)) {
          return val;
        }
        if (typeof val === 'string') {
          let newVal = [];
          try {
            newVal = JSON.parse(val.replace(/\'/g, '"'));
          } catch (error) {
            console.error(val);
          }
          return newVal;
        }
        return [];
      },
      getCustomTableDisplayValue(column, value) {
        return getCustomTableDisplayValue(column, value);
      },
    },
  };
</script>
<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';
    @import '../../../../scss/mixins/scroller.scss';
    .bk-fields-done {
        width: 100%;
        color: #737987;
        display: flex;
        .isOn {
            font-size: 22px;
            opacity: 0;
            color: #3A84FF;
        }

        &:hover {
            .isOn {
                opacity: 1;
            }
        }
        .bk-fields-done-item {
            // @include scroller(#060707, 3px);
            // overflow: auto;
            max-width: calc(100% - 30px);
            overflow-wrap: break-word;
            display: flex;
            .bk-form-content {
              width: calc(100% - 130px);
            }

            .bk-fields-done-edit {
                display: inline-block;
                margin-top: 2px;
                padding-left: 10px;
                cursor: pointer;
                align-self: flex-start;
            }
            .bk-li-link{
                color: #3a84ff;
                cursor: pointer;
                font-weight: bold;
            }
            .bk-li-left,
            .bk-li-right {
                line-height: 26px;
                color: #313238;
                display: inline-block;
            }
            .bk-li-left {
                width: 120px;
                font-weight: 400;
                margin-right: 10px;
                color: #979Ba5;
                text-align: right;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                &::before {
                    content: (':');
                    top: 3px;
                    left: 126px;
                    position: absolute;
                }
            }
            .bk-li-right {
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .bk-member-edit {
                margin-left: 30px;
            }
            .bk-fields-richtext {
                font-size: 14px;
                /deep/ .rich-text {
                    margin: 5px 0;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
            }
        }
    }

    .bk-fields-log{
        .bk-fields-done-item{
            display: flex;
            .bk-li-left,
            .bk-li-right {
                display: inline-block;
                line-height: 26px;
                color: #313238;
            }
            .bk-li-left {
                display: inline-block;
                width: 120px;
                font-weight: 400;
                text-align: right;
                overflow: hidden;
                margin-right: 10px;
                text-overflow: ellipsis;
                white-space: nowrap;
                color: #979Ba5;
                &::before {
                    content: (':');
                    top: 3px;
                    left: 126px;
                    position: absolute;
                }
            }
        }
    }
    .bk-pre {
        display: inline-block;
        white-space: pre-wrap;
    }
     .bk-li-right {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .bk-li-left {
        display: inline-block;
        width: 120px;
        font-weight: 400;
        text-align: right;
        overflow: hidden;
        margin-right: 10px;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: #979Ba5;
        &::before {
            content: (':');
            top: 3px;
            left: 126px;
            position: absolute;
        }
    }
</style>
