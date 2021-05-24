from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.augmenting_data.get_litigant import get_roles


def test_is_right_order4roles():
    ws_settings = Settings()

    roles = uf.read_json_file(ws_settings.litigant_roles)
    print(roles)
    print(get_roles.is_right_order4roles(roles))


if __name__ == '__main__':
    test_is_right_order4roles()