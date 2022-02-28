import copy
from typing import List, Generator, Iterable
from pathlib import Path

from service.mecab_parser import MecabParser
from service.mecab_storage import MecabStorage
from service.mecab_reader import MecabDataController
from domain.mecab_domain import MecabWordCategory, Category, MecabPatternData, MecabNerFeature, NerFeature

MECAB_READING_WORD = 0
MECAB_FEATURE = 1
WORD_IDX = 0
INFER_FORWARD = 1
INFER_BACKWARD = 2
FULL_WORD = 1
START_IDX = 0
END_IDX = 1
EMPTY_WORD = 0


def find_patterns_idx(pattern, target_tokens: List, parse_character=False) -> List:

    """
    리스트에서 단어 패턴을 찾아서 반환하는 함수
    :param pattern: 찾고자 하는 패턴
    :param target_tokens: 찾아야 하는 토큰 리스트
    :param parse_character: 캐릭터 단위로 분해
    :return: 저장되어 있는 리스트 반환
    """

    if parse_character:
        pattern = list(pattern)

    if isinstance(pattern, str):
        pattern = pattern.split()

    tmp_save_list = []

    for i in range(len(target_tokens) - len(pattern) + 1):
        for j in range(len(pattern)):
            if target_tokens[i + j][MECAB_READING_WORD] != pattern[j]:
                break
        else:
            tmp_save_list.append((i, i+len(pattern)))

    return tmp_save_list



def gen_integrated_entity(blank_list: List) -> Generator:

    """
    1로 채워진 리스트의 시작점과 끝점을 반환
    """

    start_idx = None
    end_idx = None
    is_word_start = False
    for idx, item in enumerate(blank_list):
        if item == FULL_WORD: # 1이 채워진 단어에 대해서 수행
            end_idx = idx # 끝단어를 시작점으로 잡는다.

            if is_word_start is False: # 1로 채워진 단어의 시작이라면, 시작점을 현 인덱스로 저장한다.
                start_idx = idx
                is_word_start = True

            if idx != len(blank_list) - 1: # 인덱스가 끝이 아니라면, 다음 단어를 탐색한다.
                continue

        if (is_word_start is True) and (end_idx is not None):
            yield start_idx, end_idx
            start_idx = None
            end_idx = None
            is_word_start = False # 단어 초기화
            continue


def _get_default_mecab_large_cat(mecab_path):

    """
    지정한 카테고리 없을 시 메캅 경로를 기본 분석 경로로 지정 위한 메소드
    :param mecab_path: 메캅 분석된 데이터 저장 경로
    :return: 저장된 카테고리
    """

    for path_item in Path(mecab_path).iterdir():
        if path_item.suffix == ".txt":
            yield path_item.stem


def _prevent_compound_token(pattern_item: List, mc_p_l: List) -> None:
    """
    - 한 카테고리에서 같은 짧은 단어 추출하는 경우 방지. ex) 양념 치킨 추출 후 치킨 추출
    :param pattern_item: 찾는 패턴
    :param mc_p_l: 문장을 메캅으로 나눈 리스트
    """

    for pattern_idx_item in range(pattern_item[START_IDX], pattern_item[END_IDX], 1):
        mc_p_l[pattern_idx_item] = ("*", mc_p_l[pattern_idx_item][MECAB_FEATURE])


class MecabNer(MecabDataController):
    """
    엔티티 추출하는 클래스
    - 앞에 단어 품사를 통한 추론 기능
    - 메캅 형태소 분석 비교 및 형태소와 문자열 비교 기능
    """

    MIN_MEANING = 2
    NER_POS = "ner"
    INFER_ENTITY_POS_LIST = ["NNG", "NNP"]

    def __init__(self, ner_path: str = None, search_category: List = None, infer=True, clear_mecab_dir=True):

        """
        :param ner_path: ner 경로
        :param search_category: 찾고자 하는 카테고리
        :param infer: 추론 여부
        :param clear_mecab_dir: 기존 디렉터리 삭제 여부
        """

        super().__init__(ner_path=ner_path, clear_mecab_dir=clear_mecab_dir)
        self.search_category = search_category
        self.write_category()

        self.mecab_parsed_list = []

        if search_category is None:
            self.search_category = list(_get_default_mecab_large_cat(mecab_path= self.mecab_path))

        self.infer = infer

    def get_category_entity(self) -> Iterable[MecabWordCategory]:

        """
        문장에서 카테고리별로 엔티티 추출
        :param sentence: 엔티티를 찾고자 하는 문장
        :return: 추출 엔티티
        """

        for mecab_category_item in self.gen_all_mecab_category_data(path=self.mecab_path, use_mecab_parser=False):
            mecab_parsed_copied = copy.deepcopy(self.mecab_parsed_list)
            category, mecab_dictionary_data = mecab_category_item
            if category not in self.search_category:
                continue
            for small_category in mecab_dictionary_data.keys():

                for small_category_item in mecab_dictionary_data.get(small_category):

                    original_data, mecab_data = small_category_item.split(",")

                    category_data = Category(large=category, small=small_category)
                    yield from self._get_pattern(MecabPatternData(category=category_data, dictionary_data=original_data, pattern=mecab_data, sentence=mecab_parsed_copied))
                    yield from self._get_pattern(MecabPatternData(category=category_data, dictionary_data=original_data, pattern=original_data, sentence=mecab_parsed_copied, min_meaning=2, parse_character=True))

    def _get_pattern(self, m_p_d: MecabPatternData) -> Iterable[MecabWordCategory]:
        """
        문장에서 데이터 패턴을 찾는 기능
        - 엔티티의 마지막 단어는 명사형이여야 함. (이가 조사임에도 엔티티로 빠지는 경우 방지)
        :param m_p_d: 찾고자 하는 메캅 데이터 패턴 정보를 담고 있는 클래스
        :return: 문장에서 메캅 단어 정보를 담고 있는 클래스
        """
        space_token_contain_pattern = find_patterns_idx(m_p_d.pattern, m_p_d.sentence, m_p_d.parse_character)

        if (len(m_p_d.pattern) >= m_p_d.min_meaning) and space_token_contain_pattern:
            for pattern_item in space_token_contain_pattern:

                _prevent_compound_token(pattern_item, m_p_d.sentence)

                yield MecabWordCategory(category=m_p_d.category,
                                        start_idx=pattern_item[START_IDX],
                                        end_idx=pattern_item[END_IDX], entity=m_p_d.dictionary_data)

    def infer_entity(self, mecab_category_item: MecabWordCategory) -> MecabWordCategory:

        """
        - mecab_category_item의 앞에 명사형이 올 경우 카테고리 아이템의 인덱스 값 변경
        :param mecab_category_item:  메캅 카테고리 아이템
        :return: 앞 단어 형태소에 따라 변경된 카테고리 아이템
        """

        end_point = 0
        if mecab_category_item.start_idx == 1:
            end_point = -1

        for idx_range in range(mecab_category_item.start_idx - 1, end_point, -1):
            if self.mecab_parsed_list[idx_range][MECAB_FEATURE].pos in self.INFER_ENTITY_POS_LIST:
                mecab_category_item.start_idx = self.mecab_parsed_list[idx_range][MECAB_FEATURE].mecab_token_compound_idx
                continue
            break
        return mecab_category_item


    def fill_entity_in_blank(self, mecab_entity_category_list: List) -> List:

        """
        문장에서 인덱스 값이 있는 경우 1로 채워서 반환
        :param mecab_entity_category_list:
        :return: 메캅 특성의 시작, 끝점이 있는 인덱스는 1로 채워서 반환
        """

        blank_list = [EMPTY_WORD] * len(self.mecab_parsed_list)

        for mecab_entity_category_item in mecab_entity_category_list:
            for i in range(mecab_entity_category_item.start_idx, mecab_entity_category_item.end_idx, 1):
                blank_list[i] = FULL_WORD

        return blank_list

    def gen_infer_mecab_ner_feature(self) -> Iterable[MecabNerFeature]:

        """
        추론 메캅 단어 특성 반환
        :return: 추론된 단어 정식 형태로로 분석하여 변환
        """

        if self.infer:
            mecab_entity_category_list = []
            for category_entity_item in self.get_category_entity():
                mecab_entity_category_list.append(self.infer_entity(category_entity_item))
        else:
            mecab_entity_category_list = list(self.get_category_entity())

        many_entity_index_list = self.fill_entity_in_blank(mecab_entity_category_list)

        for integrated_entity_item in gen_integrated_entity(many_entity_index_list):
            end_idx = integrated_entity_item[END_IDX] + 1
            start_idx = integrated_entity_item[START_IDX]
            mecab_parsed_token = self.mecab_parsed_list[start_idx:end_idx]
            restore_tokens = MecabStorage().reverse_compound_tokens(mecab_parsed_token)
            restore_sentence = " ".join(restore_tokens)
            for entity_category_item in mecab_entity_category_list:
                if entity_category_item.end_idx == end_idx:
                    small_category_replace = entity_category_item.category.small.replace(MecabDataController.SMALL_CAT_DIVIDER, "").strip()
                    yield MecabNerFeature(word=restore_sentence,
                                        pos=self.NER_POS,
                                        start_idx=start_idx,
                                        end_idx=end_idx,
                                        category=Category(large=entity_category_item.category.large, small=small_category_replace))


    def parse(self, sentence: str):
        """
        문장 분해 후 값 돌려주는 기능
        :param sentence: 입력 문장
        :return: 파싱돈 결과
        """

        self.mecab_parsed_list = list(MecabParser(sentence=sentence).gen_mecab_compound_token_feature())

        mecab_cat_list = list(self.gen_infer_mecab_ner_feature())
        cat_idx_list=[]
        [cat_idx_list.extend(list(range(x.start_idx, x.end_idx, 1))) for x in mecab_cat_list]

        parse_result = []
        for idx, mecab_parse_item in enumerate(self.mecab_parsed_list):

            for mecab_item in mecab_cat_list:
                if idx == mecab_item.end_idx:
                    parse_result.append((mecab_item.word,
                                         NerFeature(word=mecab_item.word,
                                                    pos=mecab_item.pos,
                                                    category=mecab_item.category)))
                    break
            if idx in cat_idx_list:
                continue

            parse_result.append((mecab_parse_item[MECAB_FEATURE].word, NerFeature(word=mecab_parse_item[MECAB_FEATURE].word,
                                                                                  pos=mecab_parse_item[MECAB_FEATURE].pos)))

        return parse_result

    def morphs(self, sentence: str):
        return [x[MECAB_READING_WORD] for x in self.parse(sentence=sentence)]

    def ners(self, sentence: str):
        result = [(x[MECAB_FEATURE].word, x[MECAB_FEATURE].category.large, x[MECAB_FEATURE].category.small) for x in self.parse(sentence=sentence) if x[MECAB_FEATURE].pos == "ner"]
        return result