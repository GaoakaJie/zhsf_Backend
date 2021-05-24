import os
import json
from os.path import splitext, basename
from elasticsearch import Elasticsearch

from zhsfstt.settings.settings import Settings
from zhsfstt.utils import util_functions as uf


def delete_template(es, template_id):
    es.delete_script(template_id)


def get_template(es, template_id):
    return es.get_script(template_id)


def put_template(es, template_id, template_body):
    es.put_script(template_id, template_body)


def search_template(es, body):
    return es.search_template(body=body)


def combine_zscqQuery_with_aggs(tt_settings, analysis_type, analysis_perspectives):
    zscqQuery = uf.read_file(tt_settings.zscqQueryTempalte)
    base_aggs = [os.path.join(tt_settings.zscqBaseAggs, analysis_type, "zscq" + p + analysis_type + ".json") for p in analysis_perspectives]
    templates = list()
    for base_agg in base_aggs:
        if os.path.isfile(base_agg):
            aggs_template = uf.read_json_file(base_agg)['aggs']
            template_id = splitext(basename(base_agg))[0]
            template = zscqQuery[: -1] + ",\"aggs\": " + json.dumps(aggs_template, indent=2) + zscqQuery[-1: ]
            templates.append((template_id, template))

    return templates


def write_zscq_series_template(tt_settings, analysis_type):
    templates = combine_zscqQuery_with_aggs(tt_settings, analysis_type, tt_settings.zscqPerspective)
    es = uf.get_es(tt_settings)
    for template_id, template in templates:
        '''
        if es.get_script(template_id):
            es.delete_script(template_id)
        '''
        body = {
            "script": {
                "lang": "mustache",
                "source": template
            }
        }
        es.put_script(template_id, body)
        if es.get_script(template_id):
            print(template_id, "saved!")


if __name__ == '__main__':
    tt_settings = Settings()
    for analyze_type in [tt_settings.ay, tt_settings.spzc, tt_settings.spcx, 
            tt_settings.sscjr, tt_settings.ssqq, tt_settings.ajjg, tt_settings.flsy]:
        write_zscq_series_template(tt_settings, analyze_type)  # 只需要改动这里的参数