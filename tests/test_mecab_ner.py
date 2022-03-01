from domain.mecab_domain import NerFeature, Category
from mecab_ner import MecabNer, gen_integrated_entity
from service.mecab_parser import MecabParser



def test_mecab_ner_simple():
    """
    디렉터리 추가 후 데이터 테스트 추가
    1. 기본 기능 테스트
    """
    m_n = MecabNer()
    test_sentence = "아이유의 금요일에 만나요를 들으면서 신촌 딸기를 먹을래"
    parse_result = m_n.parse(test_sentence)
    assert len(parse_result) == 10
    assert parse_result == [('아이유', NerFeature(word='아이유', pos='ner', category=Category(large='ner_example_music_singer', small='가수'))), ('의', NerFeature(word='의', pos='JKG', category=None)), ('금요일에 만나요', NerFeature(word='금요일에 만나요', pos='ner', category=Category(large='ner_example_music_song', small='노래'))), ('를', NerFeature(word='를', pos='JKO', category=None)), ('듣', NerFeature(word='듣', pos='VV+EC', category=None)), ('으면서', NerFeature(word='으면서', pos='VV+EC', category=None)), ('신촌 딸기', NerFeature(word='신촌 딸기', pos='ner', category=Category(large='ner_example_fruit', small='과일'))), ('를', NerFeature(word='를', pos='JKO', category=None)), ('먹', NerFeature(word='먹', pos='VV', category=None)), ('을래', NerFeature(word='을래', pos='EC', category=None))]

    morphs_result = m_n.morphs(test_sentence)
    assert morphs_result == ['아이유', '의', '금요일에 만나요', '를', '듣', '으면서', '신촌 딸기', '를', '먹', '을래']

    ners_result = m_n.ners(test_sentence)
    assert ners_result == [('아이유', 'ner_example_music_singer', '가수'), ('금요일에 만나요', 'ner_example_music_song', '노래'), ('신촌 딸기', 'ner_example_fruit', '과일')]


def test_mecab_ner_search_category():
    """
    디렉터리 추가 후 데이터 테스트 추가
    2. search_category테스트
    """
    m_n = MecabNer(search_category=["ner_example_music_singer"])
    test_sentence = "아이유의 금요일에 만나요를 들으면서 신촌 딸기를 먹을래"
    parse_result = m_n.parse(test_sentence)
    assert len(parse_result) == 15

    morphs_result = m_n.morphs(test_sentence)
    assert morphs_result == ['아이유', '의', '금', '요일', '에', '만나', '요', '를', '듣', '으면서', '신촌', '딸기', '를', '먹', '을래']

    ners_result = m_n.ners(test_sentence)
    assert ners_result == [('아이유', 'ner_example_music_singer', '가수')]

    m_n = MecabNer(search_category=["ner_example_music_singer", "ner_example_fruit"])
    test_sentence = "아이유의 금요일에 만나요를 들으면서 신촌 딸기를 먹을래"
    parse_result = m_n.parse(test_sentence)
    assert len(parse_result) == 14

    morphs_result = m_n.morphs(test_sentence)
    assert morphs_result == ['아이유', '의', '금', '요일', '에', '만나', '요', '를', '듣', '으면서', '신촌 딸기', '를', '먹', '을래']

    ners_result = m_n.ners(test_sentence)
    assert ners_result == [('아이유', 'ner_example_music_singer', '가수'), ('신촌 딸기', 'ner_example_fruit', '과일')]


def test_mecab_ner_infer():
    """
    디렉터리 추가 후 데이터 테스트 추가
    3. 추론 기능 테스트
    """
    m_n = MecabNer(infer=False)
    test_sentence = "아이유의 금요일에 만나요를 들으면서 신촌 딸기를 먹을래"
    parse_result = m_n.parse(test_sentence)
    assert len(parse_result) == 11

    morphs_result = m_n.morphs(test_sentence)
    assert morphs_result == ['아이유', '의', '금요일에 만나요', '를', '듣', '으면서', '신촌', '딸기', '를', '먹', '을래']

    ners_result = m_n.ners(test_sentence)
    assert ners_result == [('아이유', 'ner_example_music_singer', '가수'), ('금요일에 만나요', 'ner_example_music_song', '노래'), ('딸기', 'ner_example_fruit', '과일')]

    m_n = MecabNer(search_category=["ner_example_music_singer", "ner_example_fruit"], infer=False)
    test_sentence = "아이유의 금요일에 만나요를 들으면서 신촌 딸기를 먹을래"
    parse_result = m_n.parse(test_sentence)
    assert len(parse_result) == 15

    morphs_result = m_n.morphs(test_sentence)
    assert morphs_result == ['아이유', '의', '금', '요일', '에', '만나', '요', '를', '듣', '으면서', '신촌', '딸기', '를', '먹', '을래']

    ners_result = m_n.ners(test_sentence)
    assert ners_result == [('아이유', 'ner_example_music_singer', '가수'), ('딸기', 'ner_example_fruit', '과일')]


def test_get_category_entity():
    """
    순수하게 엔티티만 가져오는 기능 테스트
    """

    test_sentence = "아이유의 금요일에 만나요를 들으면서 신촌 딸기를 먹을래"

    m_n = MecabNer()
    m_n.mecab_parsed_list = list(MecabParser(sentence=test_sentence).gen_mecab_compound_token_feature())


    mecab_category_list = list(m_n.get_category_entity())

    assert mecab_category_list[0].entity == "아이유"
    assert mecab_category_list[0].category.large == "ner_example_music_singer"
    assert mecab_category_list[0].category.small == "#가수"

    assert mecab_category_list[1].entity == "딸기"
    assert mecab_category_list[1].category.large == "ner_example_fruit"
    assert mecab_category_list[1].category.small == "#과일"

    assert mecab_category_list[2].entity == "금요일에 만나요"
    assert mecab_category_list[2].category.large == "ner_example_music_song"
    assert mecab_category_list[2].category.small == "#노래"


def test_infer_mecab_ner_feature():
    """
    엔티티에서 데이터 추론하는 기능 테스트
    """

    test_sentence = "아이유의 금요일에 만나요를 들으면서 신촌 딸기를 먹을래"

    m_n = MecabNer()
    m_n.mecab_parsed_list = list(MecabParser(sentence=test_sentence).gen_mecab_compound_token_feature())


    mecab_category_list = list(m_n.gen_infer_mecab_ner_feature())

    assert mecab_category_list[0].word == "아이유"
    assert mecab_category_list[0].category.large == "ner_example_music_singer"
    assert mecab_category_list[0].category.small == "가수"

    assert mecab_category_list[1].word == "금요일에 만나요"
    assert mecab_category_list[1].category.large == "ner_example_music_song"
    assert mecab_category_list[1].category.small == "노래"

    assert mecab_category_list[2].word == "신촌 딸기"
    assert mecab_category_list[2].category.large == "ner_example_fruit"
    assert mecab_category_list[2].category.small == "과일"

    many_entity_index_list = m_n.fill_entity_in_blank(mecab_category_list)

    assert many_entity_index_list == [1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0]

    z = list(gen_integrated_entity(many_entity_index_list))

    assert z == [(0, 0), (2, 6), (10, 11)]
