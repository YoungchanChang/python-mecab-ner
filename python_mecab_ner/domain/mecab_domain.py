from dataclasses import dataclass
from typing import Optional
from collections import defaultdict, Counter

@dataclass
class Category:
    large: str
    small: str


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
    space: Optional[int] = None
    mecab_token: Optional[int] = None
    mecab_compound: Optional[int] = None
    begin: Optional[int] = None
    end: Optional[int] = None
    label: Optional[str] = "O"


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