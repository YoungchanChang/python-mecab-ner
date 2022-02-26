from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    large_category: str
    small_category: str


@dataclass
class MecabWordCategory:
    category: Category
    start_idx: Optional[int] = None
    end_idx: Optional[int] = None
    entity: Optional[str] = None


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
    space_token_idx: Optional[int] = None
    mecab_token_idx: Optional[int] = None