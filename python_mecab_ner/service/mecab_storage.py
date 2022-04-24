from collections import defaultdict


NODE_POS = 0
NODE_EXPRESSION = 1
MECAB_WORD_FEATURE = 1
IDX_TOKEN = 0

class MecabStorage:

    """
    메캅 형태소 분석 결과를 원래 문장으로 복원
    """



    def _append(self, data, index, token):

        """
        인덱스
        :param index: 단어가 저장된 인덱스
        :param token: 단어
        """

        data[index].append(token)

    def _mecab_reverse(self, data):

        """
        메캅 결과에서 반환
        :return: 인덱스에 저장된 토큰 반환
        """

        reverse_sentence = list()
        for key in sorted(data):
            reverse_sentence.append("".join(data[key]))
        return reverse_sentence

    def restore_mecab_tokens(self, data, parsed_tokens):

        """
        복합어로 분해되지 않은 토큰들을 원래 문장으로 복원
        :param parsed_tokens: 파싱된 토큰들
        :return: 파싱된 토큰 합친 토큰
        """
        space_mecab_list = []
        for parse_token_item in parsed_tokens:
            space_mecab_token = (parse_token_item.space, parse_token_item.mecab_token)
            if space_mecab_token not in space_mecab_list:
                space_mecab_list.append(space_mecab_token)
                self._append(data, parse_token_item.space, parse_token_item.reading)
        return self._mecab_reverse(data)

    def reverse_compound_tokens(self, parse_compound_tokens):

        """
        복합어로 파싱된 결과를 space_token_idx을 이용해 원래대로 돌려주는 기능
        - 복합어가 아니라면 바로 붙임
        - 복합어는 앞에 복합어가 저장되어있는지 확인
        :param parse_compound_tokens: 복원할 토큰
        :return: 복원된 문장
        """

        data = defaultdict(list)
        tmp_word = None
        tmp_idx = None

        for parse_token_item in parse_compound_tokens:

            if parse_token_item[MECAB_WORD_FEATURE].type is None:
                self._append(data, parse_token_item[MECAB_WORD_FEATURE].space, parse_token_item[MECAB_WORD_FEATURE].word)
                tmp_word = None
                continue

            if tmp_word == parse_token_item[MECAB_WORD_FEATURE].reading and (
                    tmp_idx == parse_token_item[MECAB_WORD_FEATURE].space):
                # 임시 단어와 읽는 단어가 일치하고(ex> Inflect) 같은 스페이스에 있으면 복구하지 않는다.
                continue

            if parse_token_item[MECAB_WORD_FEATURE].type == "Inflect" and parse_token_item[MECAB_WORD_FEATURE].pos not in ["NNG", "NNP", "XSN", "UNA"]:
                reading_value = parse_token_item[MECAB_WORD_FEATURE].reading
            else:
                reading_value = parse_token_item[MECAB_WORD_FEATURE].word

            self._append(data, parse_token_item[MECAB_WORD_FEATURE].space, reading_value)
            tmp_word = reading_value
            tmp_idx = parse_token_item[MECAB_WORD_FEATURE].space

        return self._mecab_reverse(data)