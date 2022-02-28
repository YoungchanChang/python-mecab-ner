from pathlib import Path

from mecab_ner import MecabNer

# 가봉에 가서 감이 먹고싶네
if __name__ == "__main__":
    python_mecab_ner_dir = Path(__file__).resolve().parent.joinpath("python_mecab_ner", "data", "ner_data")
    m_n = MecabNer(ner_path="./data")

    test_sentence = "자연어 처리를 위해 인공지능을 위한 파이썬을 공부하여 자연어와 관련된 일을 하고 있습니다. http 요청시 자연어 로그를 쌓는 것이 중요합니다."

    print(m_n.parse(test_sentence))
    print(m_n.morphs(test_sentence))
    print(m_n.ners(test_sentence))
