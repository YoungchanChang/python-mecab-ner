from mecab_reader import MecabDataReader
from python_mecab_ner.mecab_parser import MecabParser


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


def test_mecab_data_read():

    """
    메캅 MecabDataReader 테스트
    첫 카테고리가 MecabDataReader.HEADER (ex) #) 로 시작하면 딕셔너리 형태이여야 한다.
    첫 카테고리가 그냥 리스트라면 large_category와 small_category데이터가 같아야 한다. 그리고 #는 포함되지 않아야 한다.
    """

    from pathlib import Path
    BASE_DIR_PATH = Path(__file__).resolve().parent.parent.joinpath("python_mecab_ner", "data")

    FIRST_WORD = 0

    m_g = MecabDataReader(storage_path=str(BASE_DIR_PATH))

    for data_item in m_g.gen_all_mecab_category_data(m_g.storage_path, use_mecab_parser=True):
        category, content = data_item

        if isinstance(content, dict):
            for contet_key_item in content.keys():
                assert contet_key_item.startswith(MecabDataReader.HEADER)
        elif isinstance(content, list):
            assert category.large == category.small
            if content[FIRST_WORD].startswith(MecabDataReader.HEADER):
                raise AssertionError
