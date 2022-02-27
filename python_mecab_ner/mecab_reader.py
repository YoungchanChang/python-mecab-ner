from typing import List, Generator
from pathlib import Path
from collections import defaultdict

from domain.mecab_exception import MecabDataReaderException
from mecab_parser import MecabParser


class CategoryData:
    def __init__(self):
        self.data = defaultdict(list)

    def add(self, header, data):
        self.data[header].extend(data)


class MecabDataReader:
    FIRST_WORD = 0
    MECAB_DATA = "mecab_data"

    FORMAT_SUFFIX = ".txt"
    HEADER = "#"

    def __init__(self, ner_path: str = None, clear_mecab_dir=False):
        self.ner_path = ner_path or "./"
        self._set_mecab_path(self.ner_path, clear_mecab_dir)

    def _set_mecab_path(self, path, clear_dir) -> None:
        """ 경로 검증 """
        if not Path(path).is_dir():
            raise MecabDataReaderException("Please check if directory is proper")

        self.mecab_path = Path(__file__).parent.joinpath("data", MecabDataWriter.MECAB_DATA)

        if clear_dir:
            self._clear_dir()

        if not Path(self.mecab_path).exists():
            Path(self.mecab_path).mkdir()

    def _clear_dir(self):
        """메캅 관련 디렉터리 전부 삭제하는 메소드"""
        try:
            for path_item in Path(self.mecab_path).iterdir():
                Path(path_item).unlink()
            Path(self.mecab_path).rmdir()
        except FileNotFoundError:
            pass

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
            if Path(path_item).suffix != cls.FORMAT_SUFFIX:
                continue
            txt_data = cls.read_txt(path_item)
            c_d = CategoryData()

            if not txt_data[cls.FIRST_WORD].startswith(cls.HEADER):
                txt_data.insert(cls.FIRST_WORD, cls.HEADER + path_item.stem)

            for data_item in cls.read_category(txt_data):

                data_header, contents = data_item

                if use_mecab_parser:
                    contents = [(x, MecabParser(sentence=x).get_word_from_mecab_compound()) for x in contents]

                c_d.add(data_header, contents)

            yield path_item.stem, dict(c_d.data)

    @staticmethod
    def read_txt(path):
        """텍스트 파일 읽는 메소드"""
        with open(path, "r", encoding='utf-8-sig') as file:
            txt_list = file.read().splitlines()
            return txt_list


class MecabDataWriter(MecabDataReader):
    MECAB_WORD = 1
    ORIGIN_WORD = 0

    ITEM_BOUNDARY = ","
    CATEGORY_SPLITER = "_"



    def write_category(self) -> None:
        """카테고리별로 데이터 저장하는 메소드"""

        for data_item in self.gen_all_mecab_category_data(storage_path=self.ner_path, use_mecab_parser=True):
            category, content = data_item

            file_name = category + self.FORMAT_SUFFIX
            mecab_write_path = self.mecab_path.joinpath(file_name)

            for content_key_item in content.keys():
                mecab_write_list = [content_key_item,]
                mecab_write_list.extend([str(x[self.ORIGIN_WORD]) + self.ITEM_BOUNDARY + str(x[self.MECAB_WORD]) for x in
                             content[content_key_item]])
                MecabDataWriter.write_txt(path=str(mecab_write_path), txt_list=mecab_write_list)


    @staticmethod
    def write_txt(path: str, txt_list: List, is_sort=False):
        """텍스트 파일 쓰는 메소드"""
        if is_sort:
            txt_list = sorted(list(txt_list), key=len, reverse=True)

        with open(path, "a", encoding='UTF8') as file:
            for idx, txt_item in enumerate(txt_list):
                data = str(txt_item) + "\n"
                file.write(data)