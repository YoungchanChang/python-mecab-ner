from pathlib import Path

from mecab_ner import MecabNer

# 가봉에 가서 감이 먹고싶네
if __name__ == "__main__":
    python_mecab_ner_dir = Path(__file__).resolve().parent.joinpath("python_mecab_ner", "data", "ner_data")
    m_n = MecabNer(str(python_mecab_ner_dir), infer=False)

    test_sentence = "금요일에 만나요를 들을래"
    print(m_n.parse(test_sentence))
    print(m_n.morphs(test_sentence))
    print(m_n.ners(test_sentence))
