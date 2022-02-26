from typing import List, Generator
from pathlib import Path
from collections import defaultdict

from domain.mecab_domain import Category
from mecab_parser import MecabParser


class MecabDataReader:
    ORIGIN_WORD = 0
    MECAB_WORD = 1
    FORMAT_LIMIT = 2
    FIRST_WORD = 0

    FORMAT_SUFFIX = ".txt"
    HEADER = "#"
    ITEM_BOUNDARY = ","
    MECAB_STORAGE = "mecab_storage"

    def __init__(self, storage_path, mecab_path=None):

        self.storage_path = storage_path
        self.mecab_path = mecab_path

    @classmethod
    def read_category(cls, txt_data: List) -> Generator:
        """
        데이터에서 헤더, 내용을 나눠서 반환하는 메소드
        헤더로 시작되지 않을시 리스트로 반환
        """
        header, *contents = txt_data
        category_list = []

        for data_item in contents:
            if cls.HEADER in data_item:
                yield header, sorted(category_list, key=len, reverse=True)
                header = data_item
                category_list = []
                continue

            if data_item == '':
                continue

            category_list.append(data_item)

        yield header, sorted(category_list, key=len, reverse=True)


    @classmethod
    def gen_all_mecab_category_data(cls, storage_path, use_mecab_parser=False) -> Generator:
        """경로에 있는 데이터 읽은 뒤 카테고리 데이터셋으로 반환"""

        for path_item in Path(storage_path).iterdir():

            txt_data = DataReader.read_txt(path_item)

            c_d = CategoryData()

            if not txt_data[cls.FIRST_WORD].startswith(cls.HEADER):
                yield Category(large=path_item.stem, small=path_item.stem), txt_data
                continue

            for data_item in cls.read_category(txt_data):

                data_header, contents = data_item

                if use_mecab_parser:
                    contents = [(x, MecabParser(sentence=x).get_word_from_mecab_compound()) for x in contents]

                c_d.add(data_header, contents)

            yield Category(large=path_item.stem, small="#"), dict(c_d.data)


class CategoryData:
    def __init__(self):
        self.data = defaultdict(list)

    def add(self, header, data):
        self.data[header].extend(data)


class DataReader:

    @staticmethod
    def read_txt(data_path):
        with open(data_path, "r", encoding='utf-8-sig') as file:
            txt_list = file.read().splitlines()
            return txt_list

    @staticmethod
    def write_txt(data_path: str, txt_list: List, is_sort=False):
        if is_sort:
            txt_list = sorted(list(txt_list), key=len, reverse=True)

        with open(data_path, "a", encoding='UTF8') as file:
            for idx, txt_item in enumerate(txt_list):
                if len(txt_list) == idx+1:
                    data = str(txt_item)
                else:
                    data = str(txt_item) + "\n"
                file.write(data)