from collections import defaultdict

from domain.mecab_domain import MecabTokenStorage
from service.mecab_category_storage import CategorySave, get_only_entity


def test_set_bio_category():

    """bio 태그 저장하는 테스트 코드"""

    sentence = "훙레이 대변인은 “한반도 평화와 안정을 지키고 한반도 비핵화를 추진하는 것이 공통의 책임과 의무”라고 말했다."
    all_document_ne = [
        {
            "id": 1,
            "form": "훙레이",
            "label": "PS_NAME",
            "begin": 0,
            "end": 3
        },
        {
            "id": 2,
            "form": "대변인",
            "label": "CV_POSITION",
            "begin": 4,
            "end": 7
        },
        {
            "id": 3,
            "form": "한반도",
            "label": "LCG_BAY",
            "begin": 10,
            "end": 13
        },
        {
            "id": 4,
            "form": "한반도",
            "label": "LCG_BAY",
            "begin": 26,
            "end": 29
        },
        {
            "id": 5,
            "form": "핵",
            "label": "AF_WEAPON",
            "begin": 31,
            "end": 32
        }
    ]
    category_save = CategorySave(sentence=sentence)
    category_tokens = [x[0] for x in category_save.mecab_parse_tokens]

    assert category_tokens == ['훙레이', '대변', '인', '은', '“', '한', '반도', '평화', '와', '안정', '을', '지키', '고', '한', '반도', '비핵', '화', '를', '추진', '하', '는', '것', '이', '공통', '의', '책임', '과', '의무', '”', '이', '라고', '말', '하', '았', '다', '.']

    ne_all_list = []
    token_all_info = []
    for json_document_ne in all_document_ne:
        ne_label = json_document_ne['label']
        ne_item = json_document_ne['form']
        ne_begin = json_document_ne['begin']
        ne_end = json_document_ne['end']
        all_form = f"<{ne_item}:{ne_label}:{ne_begin}-{ne_end}>"
        ne_all_list.append(all_form)
        category_save.set_bi_tag(ne_item, ne_label, ne_begin=ne_begin, ne_end=ne_end)
        token_all_info.append((ne_label, category_save.token_info))

    assert token_all_info[0][0] == 'PS_NAME'

    assert ne_all_list == ['<훙레이:PS_NAME:0-3>', '<대변인:CV_POSITION:4-7>', '<한반도:LCG_BAY:10-13>', '<한반도:LCG_BAY:26-29>', '<핵:AF_WEAPON:31-32>']

    pos = [x[1].label for x in category_save.mecab_parse_tokens]

    assert pos == ['B-PS_NAME', 'B-CV_POSITION', 'I-CV_POSITION', 'O', 'O', 'B-LCG_BAY', 'I-LCG_BAY', 'O', 'O', 'O', 'O', 'O', 'O', 'B-LCG_BAY', 'I-LCG_BAY', 'B-AF_WEAPON', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']

    new_list = get_only_entity(category_save.mecab_parse_tokens)

    assert new_list == ['<훙레이:PS_NAME:0-3>', '<대변인:CV_POSITION:4-7>', '<한반도:LCG_BAY:10-13>', '<한반도:LCG_BAY:26-29>', '<핵:AF_WEAPON:30-31>']

    total_length = len(new_list)
    s1 = set(new_list) - set(ne_all_list)
    diff_length = len(s1)

    assert total_length == 5
    assert diff_length == 1

    mecab_token_storage = defaultdict(MecabTokenStorage)
    category_save.set_mecab_token_storage(mecab_token_storage, token_all_info)

    assert mecab_token_storage['PS_NAME'].core_pos_word.most_common()[0] == (('훙레이', 'NNP'), 1)
