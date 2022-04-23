from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    large: str
    small: str


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