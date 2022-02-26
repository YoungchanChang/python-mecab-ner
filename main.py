from python_mecab_ner import MeCabParser

if __name__ == "__main__":

        test_sentence = "나는 서울대병원에 갔어"

        mecab_parse_results = list(
            MeCabParser(test_sentence).gen_mecab_token_feature())

        for idx, mecab_parse_item in enumerate(mecab_parse_results):
            print(mecab_parse_item)

        mecab_parse_results = list(
            MeCabParser(test_sentence).gen_mecab_compound_token_feature())

        for idx, mecab_parse_item in enumerate(mecab_parse_results):
            print(mecab_parse_item)