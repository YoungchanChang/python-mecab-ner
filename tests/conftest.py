import pytest


@pytest.fixture(scope="function")
def mock_mecab_parser_sentence():
    data = {"compound_count_2" : "나는 서울대병원에 갔어"}
    return data