from pathlib import Path

from mecab_reader import MecabDataReader
from python_mecab_ner import MecabParser

if __name__ == "__main__":

        test_sentence = "나는 서울대병원에 갔어"

        mecab_parse_results = list(
            MecabParser(test_sentence).gen_mecab_token_feature())

        for idx, mecab_parse_item in enumerate(mecab_parse_results):
            print(mecab_parse_item)

        mecab_parse_results = list(
            MecabParser(test_sentence).gen_mecab_compound_token_feature())

        for idx, mecab_parse_item in enumerate(mecab_parse_results):
            print(mecab_parse_item)

        storage_path = "./python_mecab_ner/data"

        # clear data
        m_g = MecabDataReader(storage_path=storage_path)

        for data_item in m_g.gen_all_mecab_category_data(m_g.storage_path, use_mecab_parser=True):
            header, content = data_item
            print(header)
            print(content)

            #
            # assert isinstance(large_category, str)
            # assert isinstance(medium_category, str)
            # assert isinstance(data_dict, dict)


