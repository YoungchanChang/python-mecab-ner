import pytest
from pathlib import Path

from service.mecab_reader import MecabDataController, DataUtility
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
    mecab_parser 기본 분해, 복합어 분해 기능 테스트
    1. 복합어로 나누었을 때 개수가 맞는지
    2. 형태소 분석된 토큰 정보가 들어가 있는지
    """

    # 기본 분해
    mecab_parse_results = list(MecabParser(mock_mecab_parser_sentence.get("병원_sentence")).gen_mecab_token_feature())

    assert len(mecab_parse_results) == 7

    for idx, mecab_parse_item in enumerate(mecab_parse_results):
        assert mecab_parse_item.mecab_token_idx == idx

    parse_sentence = " ".join([x.word for x in mecab_parse_results])
    assert parse_sentence == '나 는 서울대 병원 에 갔 어'

    # 복합어 분해 테스트
    mecab_parse_results = list(MecabParser(mock_mecab_parser_sentence.get("병원_sentence")).gen_mecab_compound_token_feature())

    for idx, mecab_parse_item in enumerate(mecab_parse_results):
        assert mecab_parse_item[1].mecab_token_compound_idx == idx

    assert len(mecab_parse_results) == 9

    parse_sentence = " ".join([x[0] for x in mecab_parse_results])
    assert parse_sentence == '나 는 서울 대 병원 에 가 았 어'

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
        # 무조건 small_category는 있어야 한다.
        assert len(content.keys()) >= 1


def test_mecab_data_controller(mecab_ner_dir):

    """
    ner_data를 읽은 뒤, mecab_data로 전환하는 테스트 코드
    - ner_data에서 읽었을 때의 개수와, mecab_data에서 읽었을 때의 개수가 같아야 한다.
    """

    # 사용자 생성 디렉터리 사용
    m_d_w = MecabDataController(ner_path="./test_data", clear_mecab_dir=True)
    m_d_w.write_category()

    for path_item in Path(m_d_w.ner_path).iterdir():
        stroage_data_len = len(DataUtility.read_txt(path_item))
        mecab_path_read = m_d_w.mecab_path.joinpath(path_item.name)
        mecab_data_len = len(DataUtility.read_txt(mecab_path_read))

        if path_item.stem == "test_computer":
            assert stroage_data_len+1 == mecab_data_len

        if path_item.stem == "test_coffee":
            assert stroage_data_len == mecab_data_len

    # 디렉터리를 삭제하지 않으면 기존 파일 그대로
    m_d_w = MecabDataController(clear_mecab_dir=False)
    m_d_w.write_category()

    mecab_data_list = [x.name for x in Path(m_d_w.mecab_path).iterdir()]
    assert "test_computer.txt" in mecab_data_list
    assert "test_coffee.txt" in mecab_data_list

    # 디렉터리를 삭제하면 새로운 테스트 생성
    m_d_w = MecabDataController(clear_mecab_dir=True)
    m_d_w.write_category()

    mecab_data_list = [x.name for x in Path(m_d_w.mecab_path).iterdir()]

    with pytest.raises(AssertionError):
        assert "test_computer.txt" in mecab_data_list
        assert "test_coffee.txt" in mecab_data_list
