import os
import re
import json

from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf


def is_right_order4roles(roles):
    for idx, role in enumerate(roles):
        if idx < len(roles)-1:
            for later_role in roles[idx+1:]:
                if role in later_role:
                    return (idx, False)
    return (idx, True)


def exists_common_attorney(line):
    return re.search(r'共同[^，。]*?代理人', line)


def mark_litigant_role(litigant_p, docId, roles_p):
    common_attorney_lines = list()
    lines = ""
    for line in re.split(r'\n', litigant_p[docId]):
        if exists_common_attorney(line):
            common_attorney_lines.append(line)
        else:
            lines += line + '\n'
    for p in roles_p:
        lines = re.sub(p, r'[[\1]]', lines)
        
    litigant_p[docId] = {'LP': lines, 'CAL': common_attorney_lines}


def mark_dict_by_roles_p(litigant_p, roles_p):
    litigant_p_not_mark = dict()
    for docId in litigant_p:
        mark_litigant_role(litigant_p, docId, roles_p)
        if "[[" not in litigant_p[docId]['LP']:
            litigant_p_not_mark[docId] = litigant_p[docId]
    for docId in litigant_p_not_mark:
        litigant_p.pop(docId, None)

    return litigant_p, litigant_p_not_mark


def get_role_p(name):
    return re.compile(r'^[^\[]{0,4}(' + name + '(（[^（）]{1,15}）)?)', re.M)


@uf.timing_deco
def mark_roles(year):
    ws_settings = Settings()
    roles = uf.read_json_file(ws_settings.litigant_roles)
    assert is_right_order4roles(list(roles.keys()))[1], "当事人角色必须长的在前面。"

    roles_p = [get_role_p(role) for role in roles]
    litigant_p = uf.read_json_file(os.path.join(ws_settings.aug_litigant_paragraph, str(year) + '.json'))

    return mark_dict_by_roles_p(litigant_p, roles_p)


@uf.timing_deco
def get_roles(year):
    ws_settings = Settings()
    with open(os.path.join(ws_settings.aug_litigant_paragraph, str(year) + '.json'), encoding='utf-8') as fp:
        litigant_p = json.load(fp)

    roles = set()
    pattern = re.compile(r'^([^，。（\n]{1,20}?)[:：].+$', re.M)
    for docId in litigant_p:
        litigant_paragraph = litigant_p[docId]
        roles.update(re.findall(pattern, litigant_paragraph))
    return roles


def extract_roles2file():
    ws_settings = Settings()

    litigant_roles = set()
    for year in range(2001, 2019):
        litigant_roles.update(get_roles(year))
        
    uf.write_json_file(list(litigant_roles), os.path.join(ws_settings.litigant_roles_p, 'litigant_roles.json'))


def mark_roles2file():
    ws_settings = Settings()

    for year in range(2011, 2019):
        litigant_p, litigant_p_not_mark = mark_roles(year)
        uf.write_json_file(litigant_p, os.path.join(ws_settings.litigant_roles_mark, str(year) + '.json'))
        uf.write_json_file(litigant_p_not_mark, os.path.join(ws_settings.litigant_roles_mark, str(year) + '_not_mark.json'))


if __name__ == '__main__':
    mark_roles2file()