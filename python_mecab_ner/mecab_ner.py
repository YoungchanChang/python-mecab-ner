import copy
from typing import List, Generator
from pathlib import Path

from mecab_parser import MecabParser
from mecab_storage import MeCabStorage
from mecab_reader import MecabDataController
from domain.mecab_domain import MecabWordCategory, Category, MecabPatternData, MecabNerFeature, NerFeature

MECAB_WORD_FEATURE = 0
INFER_FORWARD = 1
INFER_BACKWARD = 2


def find_patterns_idx(pattern, find_tokens: List, parse_character=False) -> List:

    if parse_character:
        pattern = list(pattern)

    if isinstance(pattern, str):
        pattern = pattern.split()

    tmp_save_list = []

    for i in range(len(find_tokens)-len(pattern)+1):
        for j in range(len(pattern)):
            if find_tokens[i+j][MECAB_WORD_FEATURE] != pattern[j]:
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
        if item == MecabNer.FULL_WORD: # 1이 채워진 단어에 대해서 수행
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


class MecabNer(MecabDataController):
    """
    엔티티 추출하는 클래스
    - 앞에 단어 품사를 통한 추론 기능
    - 뒤에 단어 품사를 통한 추론 기능
    - 메캅 형태소 분석 비교 및 형태소와 문자열 비교 기능
    """

    MIN_MEANING = 2
    START_IDX = 0
    END_IDX = 1
    ONE_WORD = 1
    MECAB_FEATURE_IDX = 1
    WORD_IDX = 0
    ENTITY = 0
    EMPTY_WORD = 0
    FULL_WORD = 1
    ENTITY_POS_LIST = ["NNG", "NNP", "NNB", "NNBC", "NR", "NP", "XSN", "XR", "SL", "SH", "SN", "UNKNOWN"]

    def __init__(self, ner_path: str = None, search_category: List = None, infer=True, clear_mecab_dir=True):
        super().__init__(ner_path=ner_path, clear_mecab_dir=clear_mecab_dir)
        self.search_category = search_category
        self.write_category()

        self.mecab_parsed_list = []
        if search_category is None:
            self.search_category = list(self._get_category_list())
        self.infer = infer

    def _get_category_list(self):
        for path_item in Path(self.mecab_path).iterdir():
            if path_item.suffix == ".txt":
                yield path_item.stem

    def get_category_entity(self) -> Generator:
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
                    yield from self.get_pattern(MecabPatternData(category=category_data, dictionary_data=original_data, pattern=mecab_data, sentence=mecab_parsed_copied))
                    yield from self.get_pattern(MecabPatternData(category=category_data, dictionary_data=original_data,pattern=original_data, sentence=mecab_parsed_copied, min_meaning=2, parse_character=True))




    def get_pattern(self, m_p_d: MecabPatternData) -> Generator:
        """
        문장에서 데이터 패턴을 찾는 기능
        - 엔티티의 마지막 단어는 명사형이여야 함. (이가 조사임에도 엔티티로 빠지는 경우 방지)
        :param m_p_d: 찾고자 하는 메캅 데이터 패턴 정보를 담고 있는 클래스
        :return: 문장에서 메캅 단어 정보를 담고 있는 클래스
        """
        space_token_contain_pattern = find_patterns_idx(m_p_d.pattern, m_p_d.sentence, m_p_d.parse_character)

        if (len(m_p_d.pattern) >= m_p_d.min_meaning) and space_token_contain_pattern:
            for pattern_item in space_token_contain_pattern:

                pattern_end_pos = m_p_d.sentence[pattern_item[self.END_IDX] - 1][self.MECAB_FEATURE_IDX].pos

                if pattern_end_pos not in self.ENTITY_POS_LIST:
                    continue

                self._prevent_compound_token(pattern_item, m_p_d.sentence)

                yield MecabWordCategory(category=m_p_d.category,
                                        start_idx=pattern_item[self.START_IDX],
                                        end_idx=pattern_item[self.END_IDX], entity=m_p_d.dictionary_data)

    def infer_entity(self, mecab_parsed_list: List, mecab_category_item: MecabWordCategory) -> MecabWordCategory:
        """ pos에 따라 start_index 변경"""

        end_point = 0
        if mecab_category_item.start_idx == 1:
            end_point = -1

        for idx_range in range(mecab_category_item.start_idx - 1, end_point, -1):
            if mecab_parsed_list[idx_range][MecabNer.MECAB_FEATURE_IDX].pos in ["NNG", "NNP"]:
                mecab_category_item.start_idx = mecab_parsed_list[idx_range][1].mecab_token_compound_idx
                continue
            break
        return mecab_category_item

    def _prevent_compound_token(self, pattern_item: List, mc_p_l: List) -> None:
        """
        - 한 카테고리에서 같은 짧은 단어 추출하는 경우 방지. ex) 양념 치킨 추출 후 치킨 추출
        :param pattern_item: 찾는 패턴
        :param mc_p_l: 문장을 메캅으로 나눈 리스트
        """

        for pattern_idx_item in range(pattern_item[self.START_IDX], pattern_item[self.END_IDX], self.ONE_WORD):
            mc_p_l[pattern_idx_item] = ("*", mc_p_l[pattern_idx_item][self.MECAB_FEATURE_IDX])


    def fill_entity_in_blank(self, mecab_entity_category_list: List) -> List:
        """
        문장에서 인덱스 값이 있는 경우
        :param mecab_entity_category_list:
        :param length:
        :return:
        """
        blank = [MecabNer.EMPTY_WORD] * len(self.mecab_parsed_list)

        for mecab_entity_category_item in mecab_entity_category_list:
            for i in range(mecab_entity_category_item.start_idx, mecab_entity_category_item.end_idx, 1):
                blank[i] = self.FULL_WORD

        return blank

    def gen_mecab_category_entity(self):


        mecab_entity_category_list = []
        for category_entity_item in self.get_category_entity():
            mecab_entity_category_list.append(self.infer_entity(self.mecab_parsed_list, category_entity_item))

        many_entity_index_list = self.fill_entity_in_blank(mecab_entity_category_list)

        for integrated_entity_item in gen_integrated_entity(many_entity_index_list):
            end_idx = integrated_entity_item[1] + 1
            start_idx = integrated_entity_item[0]
            mecab_parsed_token = self.mecab_parsed_list[start_idx:end_idx]
            restore_tokens = MeCabStorage().reverse_compound_tokens(mecab_parsed_token)
            restore_sentence = " ".join(restore_tokens)
            for entity_category_item in mecab_entity_category_list:
                if entity_category_item.end_idx == end_idx:
                    small_category_replace = entity_category_item.category.small.replace("#", "").strip()
                    yield MecabNerFeature(word=restore_sentence,
                                        pos="ner",
                                        start_idx=start_idx,
                                        end_idx=end_idx,
                                        category=Category(large=entity_category_item.category.large, small=small_category_replace))

    def parse(self, sentence: str):
        self.mecab_parsed_list = list(MecabParser(sentence=sentence).gen_mecab_compound_token_feature())

        mecab_cat_list = list(self.gen_mecab_category_entity())
        cat_idx_list=[]
        [cat_idx_list.extend(list(range(x.start_idx, x.end_idx, 1))) for x in mecab_cat_list]

        parse_result = []
        for idx, mecab_parse_item in enumerate(self.mecab_parsed_list):
            for mecab_item in mecab_cat_list:
                if idx == mecab_item.end_idx:
                    parse_result.append((mecab_item.word, mecab_item))
                    break
            if idx in cat_idx_list:
                continue
            parse_result.append((mecab_parse_item[1].word, NerFeature(word=mecab_parse_item[self.MECAB_FEATURE_IDX].word, pos=mecab_parse_item[self.MECAB_FEATURE_IDX].pos)))
        return parse_result

    def morphs(self, sentence: str):
        return [x[self.WORD_IDX] for x in self.parse(sentence=sentence)]

    def ners(self, sentence: str):
        result = [(x[self.MECAB_FEATURE_IDX].word, x[self.MECAB_FEATURE_IDX].category.large, x[self.MECAB_FEATURE_IDX].category.small) for x in self.parse(sentence=sentence) if x[self.MECAB_FEATURE_IDX].pos == "ner"]
        return result