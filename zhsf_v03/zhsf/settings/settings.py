class Settings():

    def __init__(self):
        # 文书文件的路径
        self.wenshu_path4mysql = 'E:/wenshuES/wenshu'
        self.wenshu_path = 'E:/wenshuES/wenshu/detail'

        # 测试用文书路径
        self.wenshu_path_test = 'E:/wenshuES/wenshu/detail/2010'

        # 数据处理过程中的输出
        self.outputs = 'outputs/'
        self.test_outputs = 'test_outputs/'

        # 清洗数据的输出
        self.id_filter = 'outputs/cleaning_data/step01_清洗数据_ID相同而应去除的文书.txt'
        self.ncl_filter = 'outputs/cleaning_data/step02_清洗数据_案号_法院_当事人姓氏相同而应去除的文书.txt'
        self.clt_filter = 'outputs/cleaning_data/step03_清洗数据_法院_当事人全名_文书名称相同而应去除的文书.txt'

        # 强化数据的输出
        self.aug_keywords = 'outputs/augmenting_data/keywords'
        self.aug_cause = 'outputs/augmenting_data/cause'
        # 当事人
        self.aug_litigant_paragraph = 'outputs/augmenting_data/litigant/litigant_paragraph'
        self.litigant_roles_p = 'outputs/augmenting_data/litigant/litigant_roles'
        self.litigant_roles = 'outputs/augmenting_data/litigant/litigant_roles/litigant_roles_手动.json'
        self.litigant_roles_mark = 'outputs/augmenting_data/litigant/litigant_roles_mark'
        self.litigant_split = 'outputs/augmenting_data/litigant/litigant_split'
        self.litigant_other_info = 'outputs/augmenting_data/litigant/litigant_other_info'
        # 诉讼请求
        self.aug_claims = 'outputs/augmenting_data/claims'
        # 案件结果类型
        self.aug_case_result_type = 'outputs/augmenting_data/case_result_type'
        # 相关文书
        self.aug_relevant_mapping = 'outputs/augmenting_data/relevant_mapping/relevant_mapping.json'

        # 案由标准表
        self.cause_of_case_standard_file = 'data/案由2019-11-06.json'

        # 错误日志的路径
        self.error_log = 'data/error_log/error_log.json'

        # 常用数据
        # 设置、分析设置、mappings
        self.settings_and_mappings_file = 'data/设置-分析-mappings.txt'
        # 法院映射表
        self.court_map_table = 'data/法院映射表.json'


        # Elasticsearch设置
        # self.es_host = 'es-cn-mp91kklyv0005hm3x.public.elasticsearch.aliyuncs.com'
        # self.es_host = 'es-cn-v0h1m6day000d4yic.public.elasticsearch.aliyuncs.com'
        # self.es_http_auth=('zhsf', 'zhsf6666')
        self.es_http_auth = None
        self.es_host = '172.16.154.125'
        self.es_port = 9200
        self.es_use_ssl=False
        self.index_name = 'zhsf_3_0'

        # 索引时批大小
        self.batch_size = 100