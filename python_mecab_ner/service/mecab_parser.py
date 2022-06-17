import copy

import _mecab
from collections import namedtuple
from typing import Generator

from mecab import MeCabError
from python_mecab_ner.domain.mecab_domain import MecabWordFeature
from service.unicode import *
from service.string_utility import *

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


def get_exact_idx(mecab_word_feature_item, exact_idx_string, word, change_compound=True):

    """
    형태소 분석 문자가 문자열에서 정확히 어떤 인덱스에 위치하는지 반환
    :param mecab_word_feature_item: 형태소 분석 문자
    :param exact_idx_string: 문자열
    :param word: 찾고자 하는 단어
    :param change_compound: 복합어 여부
    :return: 인덱스 위치
    """

    exact_token = word

    index_string = exact_idx_string.find(exact_token)

    len_pattern = len(exact_token)
    if index_string != STRING_NOT_FOUND:
        if change_compound:
            mecab_word_feature_item.begin = index_string
            mecab_word_feature_item.end = index_string + len_pattern
        exact_idx_string = delete_pattern_from_string(exact_idx_string, exact_token, index_string)
        return exact_idx_string

    # 자모단위로 검색
    jaso_exact_idx_string = to_jaso(exact_idx_string)
    jaso_exact_token = to_jaso(exact_token)

    if len(jaso_exact_token) == 1:  # ㄹ같이 받침으로 된 경우
        return exact_idx_string

    jamo_first_range = subs_str_finder(jaso_exact_idx_string, jaso_exact_token)

    if jamo_first_range:
        get_original_jamo = join_jamos(jaso_exact_token)
        exact_idx_string_return = join_jamos(jaso_exact_idx_string)
        begin = jamo_first_range[0]
        end = begin + len(get_original_jamo)
        exact_idx_string_return = exact_idx_string_return[0:begin] + "*" * len(get_original_jamo) + exact_idx_string_return[end:]
        mecab_word_feature_item.begin = jamo_first_range[0]
        mecab_word_feature_item.end = jamo_first_range[0] + len(get_original_jamo)

        return exact_idx_string_return.replace(NO_JONGSUNG, "")

    return exact_idx_string


class MecabParser:

    """
    문장을 형태소 분석하는 클래스.
    형태소 분석시 형태소 분석 토큰, 스페이스 분석 토큰의 인덱스 위치도 함께 저장
    """

    FIRST_WORD = 0
    COMPOUND = "Compound"
    INFLECT = "Inflect"

    def __init__(self, sentence: str, dicpath=''):
        argument = ''

        if dicpath != '':
            argument = '-d %s' % dicpath

        self.sentence = sentence
        self.sentence_token = sentence.split()
        self.tagger = _mecab.Tagger(argument)

    def _get_space_token_idx(self, mecab_word_feature: MecabWordFeature) -> int:

        """
        스페이스로 토큰 분석한 인덱스 값 반환
        :param mecab_word_feature: 메캅 단어 특성데이터
        :return: 스페이스 토큰 분석한 결과
        """

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
            mecab_token_feature.mecab_token = mecab_token_idx

            space_token_idx = self._get_space_token_idx(mecab_token_feature)

            if space_token_idx is not False:
                mecab_token_feature.space = space_token_idx
                mecab_token_feature.word = mecab_token_feature.word

                yield mecab_token_feature

    def tokenize_mecab_compound(self) -> Generator:

        """
        메캅으로 분석한 토큰 제너레이터로 반환 결과 중에 복합여, 굴절형태소 있는 경우 토큰화
        """

        exact_idx_string = self.sentence
        for compound_include_item in self.gen_mecab_token_feature():
            if compound_include_item.type in [self.COMPOUND, self.INFLECT]:
                compound_item_list = compound_include_item.expression.split("+")
                infect_begin = None
                infect_end = None
                for idx, compound_item in enumerate(compound_item_list):
                    word, pos_tag, _ = compound_item.split("/")

                    if compound_include_item.type == MecabParser.INFLECT:  # 굴절어일 경우에 대한 처리

                        if len(word) > len(compound_include_item.reading): # "당은"에 형태소 분석이 "민주당은"으로 잘못 분해됨
                            word = compound_include_item.reading

                        len_pattern = len(compound_include_item.reading)

                        if idx == 0:
                            index_string = exact_idx_string.find(compound_include_item.reading)
                            exact_idx_string = delete_pattern_from_string(exact_idx_string,
                                                                          compound_include_item.reading, index_string)
                            infect_begin = index_string
                            infect_end = index_string + len_pattern

                        compound_include_item.begin = infect_begin
                        compound_include_item.end = infect_end

                    else:

                        exact_idx_string = get_exact_idx(compound_include_item, exact_idx_string, word)

                    compound_include_item.pos = pos_tag
                    compound_include_item.word = word
                    copy_compound_include_item = copy.deepcopy(compound_include_item)

                    yield word, copy_compound_include_item

            else:
                exact_idx_string = get_exact_idx(compound_include_item,
                                                      exact_idx_string, compound_include_item.word)

                yield compound_include_item.word, compound_include_item

    def gen_mecab_compound_token_feature(self) -> Generator:

        """
        :return: 복합어를 분해한 메캅 토큰 순서가 들어간 단어
        """

        for idx, x in enumerate(list(self.tokenize_mecab_compound())):
            copy_x = copy.deepcopy(x)
            copy_x[1].mecab_compound = idx
            yield copy_x

    def get_word_from_mecab_compound(self, is_list=False):

        """
        메캅으로 분해된 문장에서 단어만 추출
        :param sentence: 분석하고 싶은 문장
        :param is_list: 리스트로 반환 여부
        :return: 메캅으로 분해된 문장에서 단어만 포함된 문장
        """

        if is_list:
            return [x[self.FIRST_WORD] for x in list(self.gen_mecab_compound_token_feature())]

        return " ".join([x[self.FIRST_WORD] for x in list(self.gen_mecab_compound_token_feature())])


if __name__ == "__main__":

        test_sentence = "나는 서울대병원에 갔어"

        mecab_parse_results = list(
            MecabParser(sentence=test_sentence).gen_mecab_token_feature())

        for idx, mecab_parse_item in enumerate(mecab_parse_results):
            print(mecab_parse_item)

        mecab_parse_results = list(
            MecabParser(sentence=test_sentence).gen_mecab_compound_token_feature())

        for idx, mecab_parse_item in enumerate(mecab_parse_results):
            print(mecab_parse_item)