import copy

import _mecab
from collections import namedtuple
from typing import Generator

from mecab import MeCabError
from python_mecab_ner.domain.mecab_domain import MecabWordFeature


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
    COMPOUND = "Compound"
    INFLECT = "Inflect"

    def __init__(self, dicpath=''):
        argument = ''

        if dicpath != '':
            argument = '-d %s' % dicpath

        self.tagger = _mecab.Tagger(argument)

    def _get_space_token_idx(self, sentence_token: list, mecab_word_feature: MecabWordFeature) -> int:

        """
        스페이스로 토큰 분석한 인덱스 값 반환
        :param mecab_word_feature: 메캅 단어 특성데이터
        :return: 스페이스 토큰 분석한 결과
        """

        for idx_token, sentence_token_item in enumerate(sentence_token):

            index_string = sentence_token_item.find(mecab_word_feature.word)
            if index_string != STRING_NOT_FOUND:

                sentence_token[idx_token] = delete_pattern_from_string(sentence_token_item, mecab_word_feature.word, index_string)

                return idx_token

        return False

    def gen_mecab_token_feature(self, sentence: str) -> Generator:

        """
        메캅으로 형태소 분석한 토큰 제너레이터로 반환
        스페이스로 분석한 토큰의 정보와 형태소로 분석한 토큰의 정보 포함
        """

        lattice = _create_lattice(sentence)
        sentence_split = sentence.split()
        if not self.tagger.parse(lattice):
            raise MeCabError(self.tagger.what())

        for mecab_token_idx, mecab_token in enumerate(lattice):
            mecab_token_feature = _get_mecab_feature(mecab_token)
            mecab_token_feature.mecab_token = mecab_token_idx

            space_token_idx = self._get_space_token_idx(sentence_split, mecab_token_feature)

            if space_token_idx is not False:
                mecab_token_feature.space = space_token_idx
                mecab_token_feature.word = mecab_token_feature.word

                yield mecab_token_feature

    def tokenize_mecab_compound(self, sentence: str) -> Generator:

        """
        메캅으로 분석한 토큰 제너레이터로 반환 결과 중에 복합여, 굴절형태소 있는 경우 토큰화
        """

        exact_idx_string = sentence
        for compound_include_item in self.gen_mecab_token_feature(sentence=sentence):
            if compound_include_item.type in [self.COMPOUND, self.INFLECT]:
                compound_item_list = compound_include_item.expression.split("+")
                for compound_item in compound_item_list:
                    word, pos_tag, _ = compound_item.split("/")
                    compound_include_item.pos = pos_tag

                    exact_idx_string = self.get_exact_idx(compound_include_item, exact_idx_string, word)

                    compound_include_item.word = word
                    copy_compound_include_item = copy.deepcopy(compound_include_item)

                    yield word, copy_compound_include_item

            else:
                exact_idx_string = self.get_exact_idx(compound_include_item,
                                                      exact_idx_string, compound_include_item.word)

                yield compound_include_item.word, compound_include_item

    def get_exact_idx(self, copy_compound_include_item, exact_idx_string, word, change_compound=True):

        if copy_compound_include_item.type == self.INFLECT:

            if copy_compound_include_item.start_pos == copy_compound_include_item.pos:
                exact_token = copy_compound_include_item.reading
            else:
                return exact_idx_string
        else:
            exact_token = word


        index_string = exact_idx_string.find(exact_token)


        if index_string != STRING_NOT_FOUND:
            len_pattern = len(exact_token)
            if change_compound:
                copy_compound_include_item.begin = index_string
                copy_compound_include_item.end = index_string + len_pattern
            exact_idx_string = delete_pattern_from_string(exact_idx_string, exact_token, index_string)
            return exact_idx_string

        return exact_idx_string

    def gen_mecab_compound_token_feature(self, sentence: str) -> Generator:

        """
        :return: 복합어를 분해한 메캅 토큰 순서가 들어간 단어
        """

        for idx, x in enumerate(list(self.tokenize_mecab_compound(sentence=sentence))):
            copy_x = copy.deepcopy(x)
            copy_x[1].mecab_compound = idx
            yield copy_x

    def get_word_from_mecab_compound(self, sentence: str, is_list=False):

        """
        메캅으로 분해된 문장에서 단어만 추출
        :param sentence: 분석하고 싶은 문장
        :param is_list: 리스트로 반환 여부
        :return: 메캅으로 분해된 문장에서 단어만 포함된 문장
        """

        if is_list:
            return [x[self.FIRST_WORD] for x in list(self.gen_mecab_compound_token_feature(sentence=sentence))]

        return " ".join([x[self.FIRST_WORD] for x in list(self.gen_mecab_compound_token_feature(sentence=sentence))])


if __name__ == "__main__":

        test_sentence = "나는 서울대병원에 갔어"

        mecab_parse_results = list(
            MecabParser().gen_mecab_token_feature(test_sentence))

        for idx, mecab_parse_item in enumerate(mecab_parse_results):
            print(mecab_parse_item)

        mecab_parse_results = list(
            MecabParser().gen_mecab_compound_token_feature(test_sentence))

        for idx, mecab_parse_item in enumerate(mecab_parse_results):
            print(mecab_parse_item)