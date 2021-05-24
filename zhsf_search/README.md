# 智慧司法搜索模板

该项目参考[博客](https://fostermade.co/blog/testing-elasticsearch-and-simplifying-query-building)设置如下的结构：

```
/your-directory
├── ansible/                       # See https://github.com/elastic/ansible-Elasticsearch
├── definitions/                   # JSON/Mustache definition files.
|   ├── index/
|   |   ├── mapping/               # See https://www.elastic.co/guid...
|   |   |   ├── your_index.json
|   |   |   └── another_index.json
|   |   └── settings/              # See https://www.elastic.co/guid...
|   |       └── your_index.json
|   └── search-templates/          # Contains search templates.
|       ├── your_index.json.mustache
|       ├── another_index.json.mustache
|       └── another_way_to_search_another_index.json.mustache
└── tests/                         # Automated tests.
```

## 模板基本知识

### 存入模板

```
POST /_scripts/%s
{
  "script": {
    "lang": "mustache",
    "source": """%s"""
  }
}
```

### 渲染模板

```
POST /_render/template
{
  "id": "%s",
  "params": {
    
  }
}
```

### 使用模板

```
POST /zhsf_3_0/_search/template
{
  "id": "%s",
  "params": {
    
  }
}
```

## 模板列表

zhsfAdvanceQuery.mustache：智慧司法高级搜索模板

zscqQuery.mustache：知识产权查询模板，用于筛选分析的数据。

### 分析

zscqAjAy：知识产权-案件-案由。
zscqFyAy：知识产权-法院-案由。
zscqFgAy：知识产权-法官-案由。
zscqLsswsAy：知识产权-律师事务所-案由。
zscqLsAy：知识产权-律师-案由。
zscqDsrAy：知识产权-当事人-案由。

注意：

其中9300是知识产权合同纠纷的ID，9363是知识产权权属、侵权纠纷的ID，9433是不正当竞争纠纷的ID，9449是垄断纠纷的ID。9299是总和，总和减去前面这些就得到其他知识产权与其他纠纷的数量。

9301和9364是著作权相关的内容，9315和9393是商标权相关的内容，9319和9396是专利权相关的内容。9433是不正当竞争纠纷的内容，9449是垄断纠纷的内容。9299是总和，总和减去前面这些就得到其他的内容。

zscqAjSpzz：知识产权-案件-审判组织。
zscqFySpzz：知识产权-法院-审判组织。
zscqFgSpzz：知识产权-法官-审判组织。
zscqLsswsSpzz：知识产权-律师事务所-审判组织。
zscqLsSpzz：知识产权-律师-审判组织。
zscqDsrSpzz：知识产权-当事人-审判组织。

注意：法院级别分布中，1为最高人民法院，2为高级人民法院，3为中级人民法院，4为基层人民法院。

zscqAjSpcx：知识产权-案件-审判程序。
zscqFySpcx：知识产权-法院-审判程序。
zscqFgSpcx：知识产权-法官-审判程序。
zscqLsswsSpcx：知识产权-律师事务所-审判程序。
zscqLsSpcx：知识产权-律师-审判程序。
zscqDsrSpcx：知识产权-当事人-审判程序。

注意：

其中9300是知识产权合同纠纷的ID，9363是知识产权权属、侵权纠纷的ID，9433是不正当竞争纠纷的ID，9449是垄断纠纷的ID。9299是总和，总和减去前面这些就得到其他知识产权与其他纠纷的数量。

在当事人-审判程序中，使用exists_xgws的计数表示上诉数量。

zscqAjSscjr：知识产权-案件-诉讼参加人。
zscqFySscjr：知识产权-法院-诉讼参加人。
zscqFgSscjr：知识产权-法官-诉参加人。
zscqLsswsSscjr：知识产权-律师事务所-诉参加人。
zscqLsSscjr：知识产权-律师-诉参加人。
zscqDsrSscjr：知识产权-当事人-诉参加人。

zscqAjSsqq：知识产权-案件-诉讼请求。
zscqFySsqq：知识产权-法院-诉讼请求。
zscqFgSsqq：知识产权-法官-诉讼请求。
zscqDsrSsqq：知识产权-当事人-诉讼请求。

zscqAjAjjg：知识产权-案件-案件结果。
zscqFyAjjg：知识产权-法院-案件结果。
zscqFgAjjg：知识产权-法官-案件结果。
zscqLsswsAjjg：知识产权-律师事务所-案件结果。
zscqLsAjjg：知识产权-律师-案件结果。
zscqDsrAjjg：知识产权-当事人-案件结果。

zscqAjFlsy：知识产权-案件-法律适用。
zscqFyFlsy：知识产权-法院-法律适用。
zscqFgFlsy：知识产权-法官-法律适用。
zscqDsrFlsy：知识产权-当事人-法律适用。

