from domain.mecab_domain import MecabWordFeature
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
        token_all_info.append(category_save.token_info)

    assert token_all_info == [[('훙레이', MecabWordFeature(word='훙레이', pos='NNP', semantic='인명', has_jongseong=False, reading='훙레이', type=None, start_pos=None, end_pos=None, expression=None, space=0, mecab_token=0, mecab_compound=0, begin=0, end=3, label='B-PS_NAME'))], [('대변', MecabWordFeature(word='대변', pos='NNG', semantic=None, has_jongseong=True, reading='대변인', type='Compound', start_pos=None, end_pos=None, expression='대변/NNG/*+인/NNG/*', space=1, mecab_token=1, mecab_compound=1, begin=4, end=6, label='B-CV_POSITION')), ('인', MecabWordFeature(word='인', pos='NNG', semantic=None, has_jongseong=True, reading='대변인', type='Compound', start_pos=None, end_pos=None, expression='대변/NNG/*+인/NNG/*', space=1, mecab_token=1, mecab_compound=2, begin=6, end=7, label='I-CV_POSITION'))], [('한', MecabWordFeature(word='한', pos='NNG', semantic='지명', has_jongseong=False, reading='한반도', type='Compound', start_pos=None, end_pos=None, expression='한/NNG/*+반도/NNG/*', space=2, mecab_token=4, mecab_compound=5, begin=10, end=11, label='B-LCG_BAY')), ('반도', MecabWordFeature(word='반도', pos='NNG', semantic='지명', has_jongseong=False, reading='한반도', type='Compound', start_pos=None, end_pos=None, expression='한/NNG/*+반도/NNG/*', space=2, mecab_token=4, mecab_compound=6, begin=11, end=13, label='I-LCG_BAY'))], [('한', MecabWordFeature(word='한', pos='NNG', semantic='지명', has_jongseong=False, reading='한반도', type='Compound', start_pos=None, end_pos=None, expression='한/NNG/*+반도/NNG/*', space=6, mecab_token=11, mecab_compound=13, begin=26, end=27, label='B-LCG_BAY')), ('반도', MecabWordFeature(word='반도', pos='NNG', semantic='지명', has_jongseong=False, reading='한반도', type='Compound', start_pos=None, end_pos=None, expression='한/NNG/*+반도/NNG/*', space=6, mecab_token=11, mecab_compound=14, begin=27, end=29, label='I-LCG_BAY'))], [('비핵', MecabWordFeature(word='핵', pos='NNG', semantic=None, has_jongseong=False, reading='비핵화', type='Compound', start_pos=None, end_pos=None, expression='비핵/NNG/*+화/NNG/*', space=7, mecab_token=12, mecab_compound=15, begin=30, end=32, label='B-AF_WEAPON'))]]

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
