from zhsf.indexing_data import index
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf


def test_read_prepare_data4year():
    ws_settings = Settings()
    year = 2003
    keywords_per_year, cause_per_year, litigant_paragraph_per_year, litigant_per_year, \
            claims_per_year = index.read_prepare_data4year(ws_settings, year)

    print(claims_per_year)
    print(len(claims_per_year))


def test_add_aug_claims_data():
    ws_doc = dict()
    docId = None
    claims_per_year = None
    index.add_aug_claims_data(ws_doc, docId, claims_per_year)


if __name__ == '__main__':
    test_read_prepare_data4year()