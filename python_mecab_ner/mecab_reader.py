from typing import List, Generator
from pathlib import Path
from collections import defaultdict

from domain.mecab_exception import MecabDataReaderException
from mecab_parser import MecabParser


class CategoryData:
    """
    large_cat, small_cat에 word 리스트로 저장
    """
    def __init__(self):
        self.large_cat = defaultdict(list)

    def add(self, small_cat, word):
        self.large_cat[small_cat].extend(word)


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

    def _set_mecab_path(self, ner_path: str) -> None:

        """
        메캅 데이터 경로 생성
        - 경로가 정상 디렉터리인지 확인
        :param ner_path: ner_path 입력 경로
        :param clear_dir: 경로 전부 삭제할 것인지 여부
        """

        if not Path(ner_path).is_dir():
            raise MecabDataReaderException("Please check if directory is proper")

        self.mecab_path = Path(__file__).parent.joinpath("data", self.MECAB_DATA)

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

    @classmethod
    def read_category(cls, datas: List) -> Generator:

        """
        데이터에서 헤더, 내용을 나눠서 반환하는 메소드
        SMALL_CAT로 시작되지 않을시 small_category 리스트로 반환
        """

        small_cat, *words = datas
        small_cat_words = []

        for word in words:
            if cls.SMALL_CAT_DIVIDER in word:
                yield small_cat, sorted(small_cat_words, key=len, reverse=True)
                small_cat = word
                small_cat_words = []
                continue

            if word == '':
                continue

            small_cat_words.append(word)

        yield small_cat, sorted(small_cat_words, key=len, reverse=True)

    @classmethod
    def gen_all_mecab_category_data(cls, path, use_mecab_parser=False) -> Generator:

        """
        경로에 있는 데이터 읽은 뒤 카테고리 데이터셋으로 반환
        :param path: 데이터 읽는 경로. mecab_data or ner_data경로 접근 가능
        :param use_mecab_parser: 메캅 파서 사용시 분해되서 반환.
        :return: 카테고리이름, 데이터 반환
        """

        for path_item in Path(path).iterdir():
            if Path(path_item).suffix != cls.FORMAT_SUFFIX:
                continue

            txt_data = DataUtility.read_txt(path_item)
            large_category = path_item.stem
            c_d = CategoryData()

            if not txt_data[cls.FIRST_WORD].startswith(cls.SMALL_CAT_DIVIDER):
                txt_data.insert(cls.FIRST_WORD, cls.SMALL_CAT_DIVIDER + path_item.stem)

            for small_cat_word in cls.read_category(txt_data):

                small_cat, words = small_cat_word

                if use_mecab_parser:
                    words = [(word, MecabParser(sentence=word).get_word_from_mecab_compound()) for word in words]

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


