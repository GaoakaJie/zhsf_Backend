from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.cleaning_data.cleaning_data_with_clt import make_clt2path

from zhsf.test.cleaning_data.test_cleaning_data_with_ncl import get_more_value_date


@uf.timing_deco
def test_clt():
    ws_settings = Settings()
    
    clt2path = make_clt2path(ws_settings)

    result = get_more_value_date(clt2path)
    return result


if __name__ == '__main__':
    result = test_clt()

    ws_settings = Settings()
    uf.write_json_file(result, ws_settings.test_outputs + '法院-文书名称-当事人全名相同案件.json')