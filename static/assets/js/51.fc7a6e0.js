(window.webpackJsonp=window.webpackJsonp||[]).push([[51],{B5ja:function(t,e,i){"use strict";i.r(e);var o=i("LZHI"),a=i("JVbF");for(var n in a)["default"].indexOf(n)<0&&function(t){i.d(e,t,(function(){return a[t]}))}(n);i("IrVc");var s=i("KHd+"),c=Object(s.a)(a.default,o.a,o.b,!1,null,"47f9a630",null);e.default=c.exports},IrVc:function(t,e,i){"use strict";i("kDF6")},JVbF:function(t,e,i){"use strict";i.r(e);var o=i("sSkU"),a=i.n(o);for(var n in o)["default"].indexOf(n)<0&&function(t){i.d(e,t,(function(){return o[t]}))}(n);e.default=a.a},LZHI:function(t,e,i){"use strict";i.d(e,"a",(function(){return o})),i.d(e,"b",(function(){return a}));var o=function(){var t=this,e=t._self._c;return e("div",{staticClass:"bk-itsm-service"},[e("div",{staticClass:"is-title",class:{"bk-title-left":!t.sliderStatus}},[e("p",{staticClass:"bk-come-back"},[t._v("\n      "+t._s(t.$t('m["通知配置"]'))+"\n    ")])]),t._v(" "),e("div",{staticClass:"itsm-page-content"},[e("ul",{staticClass:"bk-notice-tab"},t._l(t.noticeType,(function(i,o){return e("li",{key:i.typeName,class:{"bk-check-notice":t.acticeTab===i.typeName},on:{click:function(e){return t.changeNotice(i,o)}}},[e("span",[t._v(t._s(i.name))])])})),0),t._v(" "),e("div",{staticClass:"bk-only-btn"},[e("bk-button",{attrs:{theme:"primary","data-test-id":"notice_button_create"},on:{click:t.addNotice}},[e("i",{staticClass:"bk-itsm-icon icon-itsm-icon-one-five"}),t._v("\n        "+t._s(t.$t("m.deployPage['新增']"))+"\n      ")]),t._v(" "),e("div",{staticClass:"bk-only-search"},[e("bk-input",{attrs:{"data-test-id":"notice_input_search",placeholder:t.$t("m['请输入模板内容']"),clearable:!0,"right-icon":"bk-icon icon-search"},on:{enter:function(e){return t.getNoticeList(1)},clear:function(e){return t.getNoticeList(1)}},model:{value:t.searchNotice,callback:function(e){t.searchNotice=e},expression:"searchNotice"}})],1)],1),t._v(" "),e("bk-table",{directives:[{name:"bkloading",rawName:"v-bkloading",value:{isLoading:t.isDataLoading},expression:"{ isLoading: isDataLoading }"}],attrs:{data:t.noticeList,size:"small"}},[e("bk-table-column",{attrs:{type:"index",label:"No.",align:"center",width:"60"}}),t._v(" "),e("bk-table-column",{attrs:{label:t.$t("m.deployPage['通知类型']"),prop:"action_name"}}),t._v(" "),e("bk-table-column",{attrs:{label:t.$t("m.slaContent['更新时间']"),prop:"update_at"}}),t._v(" "),e("bk-table-column",{attrs:{label:t.$t("m.deployPage['更新人']"),prop:"updated_by"}}),t._v(" "),e("bk-table-column",{attrs:{label:t.$t("m.deployPage['操作']"),width:"150"},scopedSlots:t._u([{key:"default",fn:function(i){return[e("bk-button",{attrs:{theme:"primary",text:""},on:{click:function(e){return t.editNotice(i.row)}}},[t._v("\n            "+t._s(t.$t('m.deployPage["编辑"]'))+"\n          ")]),t._v(" "),e("bk-button",{attrs:{theme:"primary",text:""},on:{click:function(e){return t.deleteNotice(i.row)}}},[t._v("\n            "+t._s(t.$t('m.deployPage["删除"]'))+"\n          ")])]}}])})],1),t._v(" "),e("bk-dialog",{attrs:{width:"690",theme:"primary","mask-close":!1,"auto-close":!1,"header-position":"left",title:t.isEdit?t.$t("m['编辑']"):t.$t("m['新建']")},on:{confirm:t.submitNotice,cancel:t.closeNotice},model:{value:t.isShowEdit,callback:function(e){t.isShowEdit=e},expression:"isShowEdit"}},[e("div",{staticClass:"notice-forms"},[e("bk-form",{ref:"basicFrom",attrs:{model:t.formData,"label-width":300,width:"700","form-type":"vertical",rules:t.rules}},[e("bk-form-item",{attrs:{label:t.$t("m['通知方式']"),required:!0,property:"noticeType"}},[e("bk-select",{attrs:{disabled:!0,searchable:""},model:{value:t.formData.noticeType,callback:function(e){t.$set(t.formData,"noticeType",e)},expression:"formData.noticeType"}},t._l(t.noticeType,(function(t){return e("bk-option",{key:t.typeName,attrs:{id:t.typeName,name:t.name}})})),1)],1),t._v(" "),e("bk-form-item",{attrs:{label:t.$t("m['通知场景']"),required:!0,property:"noticeUserBy"}},[e("bk-select",{attrs:{disabled:!1,searchable:""},on:{selected:t.handleSelectUserBy},model:{value:t.formData.noticeUserBy,callback:function(e){t.$set(t.formData,"noticeUserBy",e)},expression:"formData.noticeUserBy"}},t._l(t.userByList,(function(t){return e("bk-option",{key:t.id,attrs:{id:t.id,name:t.name}})})),1)],1),t._v(" "),e("bk-form-item",{attrs:{label:t.$t("m['通知类型']"),required:!0,property:"noticeAction"}},[e("bk-select",{attrs:{searchable:"",loading:t.actionLoading},model:{value:t.formData.noticeAction,callback:function(e){t.$set(t.formData,"noticeAction",e)},expression:"formData.noticeAction"}},t._l(t.actionList,(function(t){return e("bk-option",{key:t.id,attrs:{id:t.id,name:t.name}})})),1)],1)],1),t._v(" "),e("editor-notice",{ref:"editorNotice",attrs:{"custom-row":t.customRow,"is-show-title":!0,"check-id":t.acticeTab,"is-show-footer":!1,"notice-info":t.formInfo},on:{closeEditor:t.closeEditor}})],1)])],1)])},a=[];o._withStripped=!0},kDF6:function(t,e,i){},sSkU:function(t,e,i){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var o=d(i("4d7F")),a=d(i("14Xm")),n=d(i("D3Ub")),s=d(i("QbLZ")),c=d(i("Whvt")),r=d(i("0hVY")),l=i("L2JU");function d(t){return t&&t.__esModule?t:{default:t}}e.default={name:"Notice",components:{editorNotice:c.default},mixins:[r.default],data:function(){return{acticeTab:"WEIXIN",isShowEdit:!1,isEdit:!1,editNoticeId:"",remindWayList:[{id:"WEIXIN",name:this.$t('m.treeinfo["企业微信"]')},{id:"EMAIL",name:this.$t('m.treeinfo["邮件"]')},{id:"SMS",name:this.$t('m.treeinfo["手机短信"]')}],noticeList:[],noticeTypeLIST:[{id:"WEIXIN",name:this.$t('m.treeinfo["企业微信"]')},{id:"EMAIL",name:this.$t('m.treeinfo["邮件"]')},{id:"SMS",name:this.$t('m.treeinfo["手机短信"]')}],userByList:[{id:"TICKET",name:this.$t("m['单据']")},{id:"SLA",name:this.$t("m['SLA']")},{id:"TASK",name:this.$t("m['任务']")}],rules:{noticeType:[{required:!0,message:this.$t("m['必选项']"),trigger:"blur"}],noticeAction:[{required:!0,message:this.$t("m['必选项']"),trigger:"blur"}],noticeUserBy:[{required:!0,message:this.$t("m['必选项']"),trigger:"blur"}]},actionList:[],typeList:[],formData:{noticeType:"",noticeAction:"",noticeUserBy:""},formInfo:{},isDataLoading:!1,searchNotice:"",customRow:5,actionLoading:!1}},computed:(0,s.default)({sliderStatus:function(){return this.$store.state.common.slideStatus}},(0,l.mapState)({noticeType:function(t){return t.common.configurInfo.notify_type}})),watch:{acticeTab:{handler:function(t){this.formData.noticeType=t},immediate:!0}},mounted:function(){this.getNoticeList()},methods:{changeNotice:function(t){this.acticeTab=t.typeName,this.getNoticeList()},handleSelectUserBy:function(t){var e=this;return(0,n.default)(a.default.mark((function i(){var o,n,s,c;return a.default.wrap((function(i){for(;;)switch(i.prev=i.next){case 0:return i.prev=0,e.actionLoading=!0,e.actionList=[],e.formData.noticeAction="",o={used_by:t},i.next=7,e.$store.dispatch("project/getAction",o);case 7:if((n=i.sent).data&&n.result)for(c in s=n.data)e.actionList.push({id:c,name:s[c]});i.next=14;break;case 11:i.prev=11,i.t0=i.catch(0),console.log(i.t0);case 14:return i.prev=14,e.actionLoading=!1,i.finish(14);case 17:case"end":return i.stop()}}),i,e,[[0,11,14,17]])})))()},getNoticeList:function(t){var e=this;this.isDataLoading=!0;var i={notify_type:this.acticeTab};t&&(i.content_template__icontains=this.searchNotice),this.$store.dispatch("project/getProjectNotice",{params:i}).then((function(t){e.noticeList=t.data})).catch((function(t){console.log(t)})).finally((function(){e.isDataLoading=!1}))},submitNotice:function(){var t=this;o.default.all([this.$refs.editorNotice.$refs.wechatForm.validate(),this.$refs.basicFrom.validate()]).then((function(){var e=t.$refs.editorNotice.formInfo,i={title_template:e.title,content_template:e.message,project_key:t.$route.query.project_id},o=t.isEdit?"project/updateProjectNotice":"project/addProjectNotice";t.isEdit&&(i.id=t.editNoticeId),i.notify_type=t.formData.noticeType,i.action=t.formData.noticeAction,i.used_by=t.formData.noticeUserBy,t.$store.dispatch(o,i).then((function(e){t.$bkMessage({message:e.message,theme:"success"}),t.isShowEdit=!1,t.getNoticeList(),t.clearFromData()})).catch((function(e){t.$bkMessage({message:e.data.message,theme:"error"})}))}))},clearFromData:function(){this.formData.noticeAction="",this.formData.noticeUserBy="",this.$refs.editorNotice.formInfo={title:"",message:""}},closeNotice:function(){this.$refs.basicFrom.clearError(),this.$refs.editorNotice.$refs.wechatForm.clearError(),this.clearFromData(),this.isShowEdit=!1},addNotice:function(){this.isEdit=!1,this.isShowEdit=!0},editNotice:function(t){this.editNoticeId=t.id,this.formData.noticeUserBy=t.used_by,this.handleSelectUserBy(t.used_by),this.formData.noticeAction=t.action,this.$refs.editorNotice.formInfo={title:t.title_template,message:t.content_template},this.isEdit=!0,this.isShowEdit=!0},deleteNotice:function(t){var e=this;this.$bkInfo({title:this.$t('m["确认要删除？"]'),confirmLoading:!0,confirmFn:function(){e.$store.dispatch("project/deleteProjectNotice",t.id).then((function(){e.$bkMessage({message:e.$t('m["删除成功"]'),theme:"success"}),e.getNoticeList()}))}})},closeEditor:function(){this.isShowEdit=!1}}}}}]);