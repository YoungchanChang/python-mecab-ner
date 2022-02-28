from pathlib import Path

from service.mecab_reader import MecabDataController
from service.mecab_parser import MecabParser


def test_parser_check(parser_check):
    """
    메캅이 한 단어 일 때 분석하는 경우랑, 문장에서 단어로 쓰여서 다르게 파싱되는 경우에 대한 예시
    """
    result = MecabParser(parser_check.get("프룬_word")).get_word_from_mecab_compound()
    assert result == "프 루 ᆫ"
    result = MecabParser(parser_check.get("프룬_sentence")).get_word_from_mecab_compound()
    assert result == "프 룬 이 먹 고 싶 어"

    result = MecabParser(parser_check.get("의창지_word")).get_word_from_mecab_compound()
    assert result == "의창 하 지"

    result = MecabParser(parser_check.get("의창지_sentence")).get_word_from_mecab_compound()
    assert result == '의창 지 를 먹 고 싶 어'

    result = MecabParser(parser_check.get("금요일_word")).get_word_from_mecab_compound()
    assert result == '금 요일 에 만나 요'

    result = MecabParser(parser_check.get("금요일_sentence")).get_word_from_mecab_compound()
    assert result == '아이유 의 금 요일 에 만나 요 를 듣 으면서 라즈베리 를 먹 을래'


def test_gen_mecab_token_feature(mock_mecab_parser_sentence: dict):

    """
    mecab_parser의 주요 기능 테스트
    1. 복합어로 나누었을 때 개수가 맞는지
    2. 형태소 분석된 토큰 정보가 들어가 있는지
    """

    mecab_parse_results = list(MecabParser(mock_mecab_parser_sentence.get("compound_count_2")).gen_mecab_token_feature())

    assert len(mecab_parse_results) == 7

    for idx, mecab_parse_item in enumerate(mecab_parse_results):
        assert mecab_parse_item.mecab_token_idx == idx


    mecab_parse_results = list(MecabParser(mock_mecab_parser_sentence.get("compound_count_2")).gen_mecab_compound_token_feature())

    assert len(mecab_parse_results) == 9


def test_mecab_data_read(mecab_ner_dir):

    """
    메캅 MecabDataReader 테스트
    - 첫 카테고리가 MecabDataReader.HEADER (ex) #) 로 시작하면 딕셔너리 형태이여야 한다.
    - 첫 카테고리가 그냥 리스트라면 large_category와 small_category데이터가 같아야 한다. 그리고 #는 포함되지 않아야 한다.
    """


    FIRST_WORD = 0

    m_g = MecabDataController(ner_path=str(mecab_ner_dir["python_mecab_ner"]))

    for data_item in m_g.gen_all_mecab_category_data(m_g.ner_path, use_mecab_parser=True):
        category, content = data_item

        if category.large == category.small:
            assert (m_g.SMALL_CAT_DIVIDER + category.small) == list(content.keys())[FIRST_WORD]


def test_mecab_data_write(mecab_ner_dir):

    """
    ner_data를 읽은 뒤, mecab_data로 전환하는 테스트 코드
    - ner_data에서 읽었을 때의 개수와, mecab_data에서 읽었을 때의 개수가 같아야 한다.
    """

    m_d_w = MecabDataWriter(ner_path=str(mecab_ner_dir["python_mecab_ner"]), clear_mecab_dir=True)
    m_d_w.write_category()

    for path_item in Path(m_d_w.ner_path).iterdir():
        stroage_data_len = len(MecabDataController.read_txt(path_item))
        mecab_path_read = Path(path_item).parent.parent.joinpath(m_d_w.MECAB_DATA, path_item.name)
        mecab_data_len = len(MecabDataController.read_txt(mecab_path_read))
        assert stroage_data_len+1 >= mecab_data_len

