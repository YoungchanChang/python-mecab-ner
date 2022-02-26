from pathlib import Path

from mecab_reader import MecabDataReader, MecabDataWriter
from python_mecab_ner import MecabParser

if __name__ == "__main__":

    m_d_w = MecabDataWriter("./test_data")
    m_d_w.write_category()
