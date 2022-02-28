import pytest
from pathlib import Path


@pytest.fixture(scope="function")
def parser_check():
    data = {"프룬_word" : "프룬",
            "프룬_sentence": "프룬이 먹고 싶어",
            "의창지_word" : "의창지",
            "의창지_sentence" : "의창지를 먹고 싶어",
            "금요일_word" : "금요일에 만나요",
            "금요일_sentence" : "아이유의 금요일에 만나요를 들으면서 라즈베리를 먹을래",}
    return data

@pytest.fixture(scope="function")
def mock_mecab_parser_sentence():
    data = {"병원_sentence" : "나는 서울대병원에 갔어"}
    return data


@pytest.fixture(scope="function")
def mecab_ner_dir():
    python_mecab_ner_dir = Path(__file__).resolve().parent.parent.joinpath("python_mecab_ner", "data", "ner_data")
    data = {"python_mecab_ner": python_mecab_ner_dir}
    return data


