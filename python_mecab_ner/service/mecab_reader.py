from typing import List, Generator
from pathlib import Path
from collections import defaultdict

from python_mecab_ner.domain.mecab_exception import MecabDataReaderException
from python_mecab_ner.service.mecab_parser import MecabParser, delete_pattern_from_string


class CategoryData:
    """
    large_cat, small_cat에 word 리스트로 저장
    """
    def __init__(self):
        self.large_cat = defaultdict(list)

    def add(self, small_cat, word):
        self.large_cat[small_cat].extend(word)


def get_ner_item_idx(ner_text: str, ner_target_list: list) -> list:
    nert_item_idx = []

    ner_text_copy = ner_text
    for ner_tuple_item in ner_target_list:
        word_token_start = 0
        ner_target_item = f"<{ner_tuple_item[0]}:{(ner_tuple_item[1])}>"
        ner_target_start = ner_text_copy.find(ner_target_item)
        ner_text_copy = delete_pattern_from_string(ner_text_copy, ner_target_item, ner_target_start)  # <북미:OG>
        nert_target_end = ner_target_start + len(ner_target_item)
        range_idx = []
        for idx, a_item in enumerate(ner_text.split()):
            word_token_end = word_token_start + len(a_item)
            if ner_target_start >= word_token_start and ner_target_start <= word_token_end:
                range_idx.append(idx)
            elif nert_target_end >= word_token_start and nert_target_end <= word_token_end:
                range_idx.append(idx)
            elif word_token_start >= ner_target_start and word_token_end <= nert_target_end:
                range_idx.append(idx)
            word_token_start = word_token_end + 1

        nert_item_idx.append([ner_tuple_item[0], ner_tuple_item[1], range_idx])
    return nert_item_idx


def get_ner_found_list(nert_item_idx: list, plain_mecab_result: list):
    ner_found_list = []
    for ner_item in nert_item_idx:
        tmp_ner_list = []

        str_item = ner_item[0]
        save_last_token = "*"
        for plain_mecab_item in plain_mecab_result:

            if str_item.replace("*", "").replace(" ", "") == "":
                break

            if plain_mecab_item[1].type == "Inflect":
                reading_value = plain_mecab_item[1].reading
            else:
                reading_value = plain_mecab_item[1].word

            reading_idx = str_item.find(reading_value)
            # 토큰 인덱스 범위 안에 들어가고, 문자열을 찾을 때
            if (plain_mecab_item[1].space in ner_item[2]) and (reading_idx != -1):
                str_item = delete_pattern_from_string(str_item, reading_value, reading_idx)
                tmp_ner_list.append((reading_value, plain_mecab_item[1].pos))
                save_last_token = reading_value

        # 마지막 단어값이 토큰의 마지막 단어와 일치할 때 수행
        if ner_item[0][-1] == save_last_token[-1]:
            ner_item.append(tmp_ner_list)
            ner_found_list.append(ner_item)
    return ner_found_list

class DataUtility:

    """
    데이터 읽고 쓰기 유틸리티
    """

    @staticmethod
    def read_txt(path):
        """텍스트 파일 읽는 메소드"""
        with open(path, "r", encoding='utf-8-sig') as file:
            txt_list = file.read().splitlines()
            return txt_list

    @staticmethod
    def write_txt(path: str, txt_list: List, is_sort=False):
        """텍스트 파일 쓰는 메소드"""
        if is_sort:
            txt_list = sorted(list(txt_list), key=len, reverse=True)

        with open(path, "a", encoding='UTF8') as file:
            for idx, txt_item in enumerate(txt_list):
                data = str(txt_item) + "\n"
                file.write(data)


class MecabDataController:

    """
    데이터 읽고 쓰는 기능
    """

    FIRST_WORD = 0
    MECAB_WORD = 1
    ORIGIN_WORD = 0

    MECAB_DATA = "mecab_data"
    ITEM_BOUNDARY = ","
    CATEGORY_SPLITER = "_"
    FORMAT_SUFFIX = ".txt"
    SMALL_CAT_DIVIDER = "#"

    def __init__(self, ner_path: str = None, clear_mecab_dir=True):

        """
        :param ner_path: ner 데이터 경로
        :param clear_mecab_dir: 기존 메캅 디렉터리 삭제 여부
        """

        self.ner_path = ner_path or "./"
        self._clear_mecab_dir = clear_mecab_dir
        self._set_mecab_path(self.ner_path)
        self.mecab_parser = MecabParser()

    def _set_mecab_path(self, ner_path: str) -> None:

        """
        메캅 데이터 경로 생성
        - 경로가 정상 디렉터리인지 확인
        :param ner_path: ner_path 입력 경로
        :param clear_dir: 경로 전부 삭제할 것인지 여부
        """

        if not Path(ner_path).is_dir():
            raise MecabDataReaderException("Please check if directory is proper")

        self.mecab_path = Path(__file__).parent.parent.joinpath("data", self.MECAB_DATA)

        if self._clear_mecab_dir:
            self._clear_dir()

        if not Path(self.mecab_path).exists():
            Path(self.mecab_path).mkdir()

    def _clear_dir(self):

        """
        메캅 데이터 저장 디렉터리 데이터 전부 삭제하는 메소드
        - ner_example인 경우 제외
        """

        try:
            for path_item in Path(self.mecab_path).iterdir():

                if path_item.stem.startswith("ner_example"): # 예시코드 삭제 방지 코드
                    continue

                Path(path_item).unlink()

        except FileNotFoundError:
            pass

    def read_category(self, datas: List) -> Generator:

        """
        데이터에서 헤더, 내용을 나눠서 반환하는 메소드
        SMALL_CAT로 시작되지 않을시 small_category 리스트로 반환
        """

        small_cat, *words = datas
        small_cat_words = []

        for word in words:
            if self.SMALL_CAT_DIVIDER in word:
                yield small_cat, sorted(small_cat_words, key=len, reverse=True)
                small_cat = word
                small_cat_words = []
                continue

            if word == '':
                continue

            small_cat_words.append(word)

        yield small_cat, sorted(small_cat_words, key=len, reverse=True)

    def gen_all_mecab_category_data(self, path, use_mecab_parser=False) -> Generator:

        """
        경로에 있는 데이터 읽은 뒤 카테고리 데이터셋으로 반환
        :param path: 데이터 읽는 경로. mecab_data or ner_data경로 접근 가능
        :param use_mecab_parser: 메캅 파서 사용시 분해되서 반환.
        :return: 카테고리이름, 데이터 반환
        """

        for path_item in Path(path).iterdir():
            if Path(path_item).suffix != self.FORMAT_SUFFIX:
                continue

            txt_data = DataUtility.read_txt(path_item)
            large_category = path_item.stem
            c_d = CategoryData()

            if not txt_data[self.FIRST_WORD].startswith(self.SMALL_CAT_DIVIDER):
                txt_data.insert(self.FIRST_WORD, self.SMALL_CAT_DIVIDER + path_item.stem)

            for small_cat_word in self.read_category(txt_data):

                small_cat, words = small_cat_word

                if use_mecab_parser:
                    words = [(word, self.mecab_parser.get_word_from_mecab_compound(sentence=word)) for word in words]

                c_d.add(small_cat, words)

            yield large_category, dict(c_d.large_cat)

    def write_category(self) -> None:

        """
        카테고리별로 데이터 저장하는 메소드
        ner_path에서 데이터 읽어서 mecab_path에 데이터 저장
        """

        for data_item in self.gen_all_mecab_category_data(path=self.ner_path, use_mecab_parser=True):
            category, content = data_item

            file_name = category + self.FORMAT_SUFFIX
            mecab_write_path = self.mecab_path.joinpath(file_name)

            if file_name.startswith("ner_example"): # 예시코드 실행시 추가 방지 코드
                continue

            for content_key_item in content.keys():
                mecab_write_list = [content_key_item,]
                mecab_write_list.extend([str(x[self.ORIGIN_WORD]) + self.ITEM_BOUNDARY + str(x[self.MECAB_WORD]) for x in
                             content[content_key_item]])
                DataUtility.write_txt(path=str(mecab_write_path), txt_list=mecab_write_list)


