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
