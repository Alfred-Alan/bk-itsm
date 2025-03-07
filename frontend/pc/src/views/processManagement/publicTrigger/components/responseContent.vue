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
  <div class="bk-response-content">
    <!-- 更改处理人 -->
    <div @click="item.contentStatus = false">
      <bk-form :form-type="'horizontal'"
        :label-width="200"
        ref="conductorForm">
        <!-- 区分API和普通的响应事件结构 -->
        <template v-if="item.wayInfo.key === 'api'">
          <api-call :item="item">
          </api-call>
        </template>
        <template v-else-if="item.wayInfo.key === 'modify_field'">
          <modify-field :field-schema="item.wayInfo.field_schema"></modify-field>
        </template>
        <template v-else>
          <template v-for="(itemInfo, index) in item.wayInfo.field_schema">
            <!-- 对于多层嵌套和单层嵌套的区别 -->
            <template v-if="itemInfo.type === 'SUBCOMPONENT'">
              <send-message :key="index"
                :item-info="itemInfo">
              </send-message>
            </template>
            <template v-else>
              <bk-form-item :ext-cls="itemInfo.required ? 'bk-field-schema mb20' : 'bk-field-schema no-require-item mb20'"
                :label="itemInfo.name"
                :required="itemInfo.required"
                :key="index"
                :desc="itemInfo.tips">
                <change-conductor
                  :item-info="itemInfo">
                </change-conductor>
              </bk-form-item>
            </template>
          </template>
        </template>
        <!-- 所有的响应事件都存在执行方式 -->
        <bk-form-item :label="$t(`m.trigger['执行方式']`)" :required="true" :ext-cls="'bk-field-schema mb20'">
          <bk-radio-group v-model="item.performData.runMode">
            <bk-radio
              :value="'BACKEND'"
              :ext-cls="'mr50 pr10'">{{$t(`m.trigger['后台自动执行']`)}}</bk-radio>
            <bk-radio
              v-if="isShowFrontendTrigger"
              :value="'MANUAL'">{{$t(`m.trigger['前台按钮触发']`)}}</bk-radio>
          </bk-radio-group>
        </bk-form-item>
        <template v-if="item.performData.runMode === 'MANUAL'">
          <bk-form-item
            :required="true"
            :label="$t(`m.trigger['按钮名称']`)"
            :ext-cls="'bk-field-schema mb20'">
            <bk-input
              :clearable="true"
              v-model="item.performData.displayName"
              style="width: 260px;"></bk-input>
          </bk-form-item>
        </template>
        <bk-form-item
          :required="true"
          :label="$t(`m.trigger['触发次数']`)"
          :ext-cls="'bk-field-schema'">
          <bk-radio-group v-model="item.performData.repeat">
            <bk-radio :value="'one'" :disabled="disableRepeat" :ext-cls="'mr50 pr10'">{{$t(`m.trigger['一次']`)}}</bk-radio>
            <bk-radio :value="'more'">{{$t(`m.trigger['不限']`)}}</bk-radio>
          </bk-radio-group>
        </bk-form-item>
      </bk-form>
      <p class="bk-error-info" v-if="item.contentStatus">{{$t(`m.trigger['您还有内容未填写，请确认。']`)}}</p>
    </div>
  </div>
</template>
<script>
  import changeConductor from './changeConductor.vue';
  import sendMessage from './sendMessage.vue';
  import apiCall from './apiCall.vue';
  import modifyField from './modifyField';

  export default {
    name: 'responseContent',
    components: {
      changeConductor,
      sendMessage,
      apiCall,
      modifyField,
    },
    props: {
      item: {
        type: Object,
        default() {
          return {};
        },
      },
      signal: String,
    },
    data() {
      return {
      };
    },
    computed: {
      // 只允许后台自动执行的触发事件列表
      onlyBackendSignals() {
        return this.$store.state.common.configurInfo.only_backend_signals || [];
      },
      // 是否显示前台触发 radio
      isShowFrontendTrigger() {
        return !this.onlyBackendSignals.includes(this.signal);
      },
      disableRepeat() {
        return this.signal === 'GLOBAL_LEAVE_STATE' || this.signal === 'GLOBAL_ENTER_STATE';
      },
    },
    watch: {
      isShowFrontendTrigger: {
        handler(val) {
          if (!val) {
            this.item.performData.runMode = 'BACKEND';
          }
        },
        immediate: true,
      },
      signal: {
        handler(val) {
          if (val === 'GLOBAL_LEAVE_STATE' || val === 'GLOBAL_ENTER_STATE') {
            this.item.performData.repeat = 'more';
          }
        },
        immediate: true,
      },
    },
    created() {
      this.initData();
    },
    methods: {
      initData() {
        this.$set(this.item, 'contentStatus', false);
        // 对于API字段需要做特定的数据处理
        if (this.item.wayInfo.key === 'api') {
          this.item.wayInfo.field_schema.forEach(schema => {
            if (schema.key === 'api_source') {
              this.$set(schema, 'systemId', '');
              this.$set(schema, 'apiId', '');
            } else {
              this.$set(schema, 'apiContent', {});
            }
          });
        } else {
          // 内置content内容
          this.item.wayInfo.field_schema.forEach(schema => {
            let valueInfo = schema.value || '';
            if (schema.type === 'MEMBERS' || schema.type === 'MULTI_MEMBERS') {
              valueInfo = [];
              if (schema.value) {
                schema.value.forEach(schemaValue => {
                  if (schemaValue.value) {
                    const itemValue = {
                      key: schemaValue.value.member_type,
                      value: schemaValue.value.members,
                      secondLevelList: [],
                      isLoading: false,
                    };
                    valueInfo.push(itemValue);
                  }
                });
              } else {
                const itemValue = {
                  key: '',
                  value: '',
                  secondLevelList: [],
                  isLoading: false,
                };
                valueInfo.push(itemValue);
              }
            }
            this.$set(schema, 'value', valueInfo);
            // 对于发通知的数据格式
            if (schema.type === 'SUBCOMPONENT' && schema.sub_components && schema.sub_components.length) {
              schema.sub_components.forEach(subComponent => {
                if (subComponent.field_schema.length) {
                  subComponent.field_schema.forEach(subField => {
                    let subFieldValue = subField.value || '';
                    if (subField.type === 'MEMBERS' || subField.type === 'MULTI_MEMBERS') {
                      subFieldValue = [];
                      if (Array.isArray(subField.value)) {
                        subField.value.forEach(schemaValue => {
                          if (schemaValue.value) {
                            const itemValue = {
                              key: schemaValue.value.member_type,
                              value: schemaValue.value.members,
                              secondLevelList: [],
                              isLoading: false,
                            };
                            subFieldValue.push(itemValue);
                          }
                        });
                      } else {
                        subFieldValue = [
                          {
                            key: '',
                            value: '',
                            secondLevelList: [],
                            isLoading: false,
                          },
                        ];
                      }
                    }
                    this.$set(subField, 'value', subFieldValue);
                  });
                }
              });
            }
          });
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';

    .bk-response-content {
        border-top: 1px solid #DCDEE5;
        padding: 18px 0;
    }
    .bk-field-schema {
        padding: 0 18px;
    }
    .no-require-item{
        /deep/ .bk-label:after{
            color: transparent;
        }
    }
    .bk-error-info {
        color: #ff5656;
        font-size: 12px;
        line-height: 30px;
        padding: 0 18px;
    }
</style>
