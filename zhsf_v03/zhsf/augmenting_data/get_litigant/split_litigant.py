import os
import re
import json

from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf


def get_name_and_other(info):
    return re.split(r'[，。,\n]', info, maxsplit=1)


def get_litigants(litigant_p, docId):
    litigants = list()
    infos = re.split(r'\[\[([^\]]+?)\]\]', litigant_p[docId]['LP'])[1:]
    for i in range(0, len(infos), 2):
        litigant = dict()
        litigant['role'] = infos[i]
        litigant['name'], litigant['other'] = get_name_and_other(infos[i+1])
        litigants.append(litigant)
    return litigants


@uf.timing_deco
def split_litigant(year):
    ws_settings = Settings()
    litigant_p = uf.read_json_file(os.path.join(ws_settings.litigant_roles_mark, str(year) + '.json'))
    
    ws_litigants = dict()
    for docId in litigant_p:
        ws_litigants[docId] = {'LP': get_litigants(litigant_p, docId), 'CAL': litigant_p[docId]['CAL']}
    return ws_litigants


if __name__ == '__main__':
    ws_settings = Settings()

    for year in range(2011, 2019):
        uf.write_json_file(split_litigant(year), os.path.join(ws_settings.litigant_split, str(year) + '.json'))