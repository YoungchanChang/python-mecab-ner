import pytest
from pathlib import Path


@pytest.fixture(scope="function")
def mock_mecab_parser_sentence():
    data = {"compound_count_2" : "나는 서울대병원에 갔어"}
    return data


@pytest.fixture(scope="function")
def mecab_ner_dir():
    python_mecab_ner_dir = Path(__file__).resolve().parent.parent.joinpath("python_mecab_ner", "data", "ner_data")
    data = {"python_mecab_ner": python_mecab_ner_dir}
    return data


