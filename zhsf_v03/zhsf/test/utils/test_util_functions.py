import time
from zhsf.utils import util_functions as uf
from zhsf.settings.settings import Settings


def test_get_relative_path():
    abs_path = "E:/wenshuES/wenshu/detail/2001/0\\1\\c0723d7754ad207bc2aecd141835a62b.json,2"

    ws_settings = Settings()

    print(uf.get_relative_path(abs_path, ws_settings.wenshu_path))


@uf.timing_deco
def test_wenshu_id2wenshu_pos():
    wenshu_id = 'b44ce8c12e3c47b69e6faa3b00e88d4a'
    relpaths, wenshu_pos_list = uf.wenshu_id2wenshu_pos(wenshu_id)
    print("相对路径：", relpaths)
    print("文书位置：", wenshu_pos_list)


@uf.timing_deco
def test_timing_deco(a, b):
    print("方法开始")
    time.sleep(2)
    print(a + b)
    print("方法结束")


def test_read_setting_and_mapping_file():
    ws_settings = Settings()

    sam = uf.read_setting_and_mapping_file(ws_settings.settings_and_mappings_file)
    print(len(sam))
    print(sam['settings'])
    print(len(sam['mappings']['properties']))
    print(sam['mappings']['properties'])


if __name__ == '__main__':
    test_wenshu_id2wenshu_pos()