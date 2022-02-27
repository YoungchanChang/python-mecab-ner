import copy

import _mecab
from collections import namedtuple
from typing import Generator

from mecab import MeCabError
from domain.mecab_domain import MecabWordFeature


def delete_pattern_from_string(string, pattern, index, nofail=False):
    """ 문자열에서 패턴을 찾아서 *로 변환해주는 기능 """

    # raise an error if index is outside of the string
    if not nofail and index not in range(len(string)):
        raise ValueError("index outside given string")

    # if not erroring, but the index is still not in the correct range..
    if index < 0:  # add it to the beginning
        return pattern + string
    if index > len(string):  # add it to the end
        return string + pattern

    len_pattern = len(pattern)
    blank_pattern = len(pattern) * "*"
    # insert the new string between "slices" of the original
    return string[:index] + blank_pattern + string[index + len_pattern:]

STRING_NOT_FOUND = -1

Feature = namedtuple('Feature', [
    'pos',
    'semantic',
    'has_jongseong',
    'reading',
    'type',
    'start_pos',
    'end_pos',
    'expression',
])


def _create_lattice(sentence):
    lattice = _mecab.Lattice()
    lattice.add_request_type(_mecab.MECAB_ALLOCATE_SENTENCE)  # Required
    lattice.set_sentence(sentence)

    return lattice


def _get_mecab_feature(node) -> MecabWordFeature:
    # Reference:
    # - http://taku910.github.io/mecab/learn.html
    # - https://docs.google.com/spreadsheets/d/1-9blXKjtjeKZqsf4NzHeYJCrr49-nXeRF6D80udfcwY
    # - https://bitbucket.org/eunjeon/mecab-ko-dic/src/master/utils/dictionary/lexicon.py

    # feature = <pos>,<semantic>,<has_jongseong>,<reading>,<type>,<start_pos>,<end_pos>,<expression>
    values = node.feature.split(',')
    assert len(values) == 8

    values = [value if value != '*' else None for value in values]
    feature = dict(zip(Feature._fields, values))
    feature['has_jongseong'] = {'T': True, 'F': False}.get(feature['has_jongseong'])

    return MecabWordFeature(node.surface, **feature)


class MecabParser:

    """
    문장을 형태소 분석하는 클래스.
    형태소 분석시 형태소 분석 토큰, 스페이스 분석 토큰의 인덱스 위치도 함께 저장
    """

    FIRST_WORD = 0
    type_list = ["Compound", "Inflect"]

    def __init__(self, sentence: str, dicpath=''):
        argument = ''

        if dicpath != '':
            argument = '-d %s' % dicpath

        self.tagger = _mecab.Tagger(argument)
        self.sentence = sentence
        self.sentence_token = self.sentence.split()

    def _get_space_token_idx(self, mecab_word_feature: MecabWordFeature) -> int:

        """ 스페이스로 토큰 분석한 인덱스 값 반환 """

        for idx_token, sentence_token_item in enumerate(self.sentence_token):

            index_string = sentence_token_item.find(mecab_word_feature.word)
            if index_string != STRING_NOT_FOUND:

                self.sentence_token[idx_token] = delete_pattern_from_string(sentence_token_item, mecab_word_feature.word, index_string)

                return idx_token

        return False

    def gen_mecab_token_feature(self) -> Generator:

        """
        메캅으로 형태소 분석한 토큰 제너레이터로 반환
        스페이스로 분석한 토큰의 정보와 형태소로 분석한 토큰의 정보 포함
        """

        lattice = _create_lattice(self.sentence)

        if not self.tagger.parse(lattice):
            raise MeCabError(self.tagger.what())

        for mecab_token_idx, mecab_token in enumerate(lattice):
            mecab_token_feature = _get_mecab_feature(mecab_token)
            mecab_token_feature.mecab_token_idx = mecab_token_idx

            space_token_idx = self._get_space_token_idx(mecab_token_feature)

            if space_token_idx is not False:
                mecab_token_feature.space_token_idx = space_token_idx
                mecab_token_feature.word = mecab_token_feature.word.lower()

                yield mecab_token_feature

    def tokenize_mecab_compound(self) -> Generator:

        """
        메캅으로 분석한 토큰 제너레이터로 반환 결과 중에 복합여, 굴절형태소 있는 경우 토큰화
        """

        for compound_include_item in self.gen_mecab_token_feature():
            if compound_include_item.type in self.type_list:
                compound_item_list = compound_include_item.expression.split("+")
                for compound_item in compound_item_list:
                    word, pos_tag, _ = compound_item.split("/")
                    yield word, compound_include_item

            else:
                yield compound_include_item.word, compound_include_item

    def gen_mecab_compound_token_feature(self):
        for idx, x in enumerate(list(self.tokenize_mecab_compound())):
            copy_x = copy.deepcopy(x)
            copy_x[1].mecab_token_compound_idx = idx
            yield copy_x

    def get_word_from_mecab_compound(self, is_list=False):

        """ 메캅 특성에서 단어만 검출"""

        if is_list:
            return [x[self.FIRST_WORD] for x in list(self.gen_mecab_compound_token_feature())]

        return " ".join([x[self.FIRST_WORD] for x in list(self.gen_mecab_compound_token_feature())])


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