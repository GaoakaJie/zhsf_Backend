# 智慧司法项目重构

zhsf_v03目录下的outputs与test_outputs目录中存放输出数据，未上传，放在压缩包中。

说明书：《智慧司法搜索系统说明书》

大致地思考了下这个项目的目录结构。

## 经常执行的命令

```
python -m zhsf.augmenting_data.get_keywords

python -m zhsf.augmenting_data.get_cause


python -m zhsf.augmenting_data.get_litigant.get_litigant_paragraph

python -m zhsf.augmenting_data.get_litigant.get_roles

python -m zhsf.augmenting_data.get_litigant.split_litigant

python -m zhsf.augmenting_data.get_litigant.get_litigant_other_info
```

