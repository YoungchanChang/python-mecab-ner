from dataclasses import dataclass
from typing import Optional
from collections import defaultdict, Counter

core_noun = ["NNG", "NNP"]
core_pos = core_noun + ["VV", "VA"]
neighbor_pos = ["NNG","NNP","NNB","NNBC","NR","NP","VV","VA","VX","VCP","VCN","MM","MAG","MAJ","IC","JKS","JKC","JKG","JKO","JKB","JKV","JKQ","JX","JC","EP","EF","EC","ETN","ETM","XPN","XSN","XSV","XSA","XR","SF","SE","SSO","SSC","SC","SY","SL","SH","SN"]

single_possible_token = core_noun + ['SL']
entity_last_pos = single_possible_token + ["NNB","NNBC","NR","NP","VV","VA","ETN","ETM","XSN","XR","SH","SN",]
forbidden_words = ['’']


@dataclass
class Category:
    large: str
    small: str


class MecabTokenStorage:
    def __init__(self):
        self.core_key_word = defaultdict(Counter)
        self.core_pos_word = defaultdict(Counter) # core pos에 반드시 들어가야 하는 단어.
        self.neighbor_word = Counter() # 가능한 pos 범위만 저장한다. ("가", "XPN")


class CategorySaveStorage:
    def __init__(self):
        self.pos_dict = defaultdict(set) # 포맷과 마지막 값을 확인
        self.word_dict = set() # 마지막 값을 확인
        self.counter_dict = Counter() # 검색용 점수 스코어 단어
        self.counter_near_dict = Counter()  # 검색용 점수 스코어 단어


class CategoryLoadStorage:
    def __init__(self):
        self.pos_dict = defaultdict(dict)
        self.word_dict = list()
        self.counter_dict = Counter()
        self.counter_near_dict = Counter()


@dataclass
class MecabWordCategory:
    category: Category
    start_idx: Optional[int] = None
    end_idx: Optional[int] = None
    entity: Optional[str] = None


@dataclass
class MecabPatternData:
    category: Category
    dictionary_data: str
    pattern: str
    sentence: list
    min_meaning: int = 0
    parse_character: bool = False


@dataclass
class MecabWordFeature:
    word: str
    pos: str
    semantic: str
    has_jongseong: bool
    reading: str
    type : str
    start_pos: str
    end_pos: str
    expression: str
    space: Optional[int] = None # 스페이스 토큰 기준 인덱스
    mecab_token: Optional[int] = None # 메캅 토큰 기준 인덱스
    mecab_compound: Optional[int] = None # 메캅에 합성어, 굴절어 있을 때 인덱스
    begin: Optional[int] = None # 문자열 전체에서 시작 인덱스
    end: Optional[int] = None #  문자열 전체에서  인덱스
    label: Optional[str] = "O" # BIO 태그


@dataclass
class MecabNerFeature:
    word: str
    pos: str
    start_idx: int
    end_idx: int
    category: Optional[Category] = None


@dataclass
class NerFeature:
    word: str
    pos: str
    category: Optional[Category] = None