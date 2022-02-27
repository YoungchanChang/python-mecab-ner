from collections import defaultdict


NODE_POS = 0
NODE_EXPRESSION = 1
MECAB_WORD_FEATURE = 1
IDX_TOKEN = 0

class MeCabStorage:

    """ 메캅 형태소 분석 결과를 원래대로 돌려주는 기능 """

    def __init__(self):
        self.data = defaultdict(list)

    def _append(self, index, sentence):

        """ 인덱스를 키값으로 추가 """

        self.data[index].append(sentence)

    def _mecab_reverse(self):
        reverse_sentence = list()
        for key in sorted(self.data):
            reverse_sentence.append("".join(self.data[key]))
        return reverse_sentence

    def restore_mecab_tokens(self, parse_token):
        for parse_token_item in parse_token:
            self._append(parse_token_item.space_token_idx, parse_token_item.word)
        return self._mecab_reverse()

    def reverse_compound_tokens(self, parse_token):
        """
        복합어로 파싱된 결과를 space_token_idx을 이용해 원래대로 돌려주는 기능
        :param parse_token: 복원할 토큰
        :return: 복원된 문장
        """
        tmp_word = None
        tmp_idx = None

        for parse_token_item in parse_token:
            if parse_token_item[MECAB_WORD_FEATURE].type is None:
                self._append(parse_token_item[MECAB_WORD_FEATURE].space_token_idx, parse_token_item[MECAB_WORD_FEATURE].word)
                tmp_word = None
                continue

            if tmp_word == parse_token_item[MECAB_WORD_FEATURE].word and (
                    tmp_idx == parse_token_item[MECAB_WORD_FEATURE].space_token_idx):
                continue
            self._append(parse_token_item[MECAB_WORD_FEATURE].space_token_idx, parse_token_item[MECAB_WORD_FEATURE].word)
            tmp_word = parse_token_item[MECAB_WORD_FEATURE].word
            tmp_idx = parse_token_item[MECAB_WORD_FEATURE].space_token_idx

        return self._mecab_reverse()