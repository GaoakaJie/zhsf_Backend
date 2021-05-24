import sys
from os.path import join

from zhsf.cleaning_data import cleaning_data as cd
from zhsf.utils import util_functions as uf


def test_get_best_doc():
    docs = ['aa×某', 'bbb某', 'cc']
    idxs = [2, 4, 6]
    best_doc = cd.get_best_doc(docs, idxs)
    print(best_doc)


def test_remain_distinct_id():
    pos_list = cd.remain_distinct_id()
    uf.write_json_file(pos_list, 'test_outputs/pos_list.json')


if __name__ == '__main__':
    test_remain_distinct_id()