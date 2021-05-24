from pprint import pprint

from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.augmenting_data.get_keywords import get_keywords_by_termvectors
from zhsf.augmenting_data.get_keywords import cleanning_keywords


def test_get_keywords_by_termvectors():
    ws_settings = Settings()
    es = uf.get_es(ws_settings)
    docId = "d52087753c524bfc8036a84d00a0e561"
    result = get_keywords_by_termvectors(ws_settings, es, docId)

    pprint(cleanning_keywords(result))


if __name__ == '__main__':
    test_get_keywords_by_termvectors()