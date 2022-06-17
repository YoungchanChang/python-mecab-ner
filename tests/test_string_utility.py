import pytest
from pathlib import Path

from service.string_utility import *


def test_parser_check(parser_check):
    """
    메캅이 한 단어 일 때 분석하는 경우랑, 문장에서 단어로 쓰여서 다르게 파싱되는 경우에 대한 예시
    """
    str_range = "테스트 문장입니다"
    str_pattern = "문장"
    range = subs_str_finder(str_range, str_pattern)
    assert range == (4, 6)

    str_pattern = "테스트"
    range = subs_str_finder(str_range, str_pattern)
    assert range == (0, 3)

    str_range = "문자열 토큰 리스트 지우기"
    str_pattern = "토큰 리스트"
    range = subs_str_finder(str_range, str_pattern)
    token_test = delete_pattern_from_string(str_range, str_pattern, range[0])
    assert token_test == '문자열 ** *** 지우기'
