from pathlib import Path

from mecab_ner import MecabNer
from service.mecab_parser import MecabParser



def test_mecab_ner_current_dir():
    """
    디렉터리 추가 후 데이터 테스트 추가
    """

    # 테스트 데이터 추가
    ner_dir = Path(__file__).resolve().parent.parent
    m_d_w = MecabDataWriter(ner_path=str(ner_dir), clear_mecab_dir=True)
    m_d_w.write_category()


    # 카테고리 리스트에 따라 필터링
    category_list = ["test_mecab_data",]
    m_n = MecabNer(search_category=category_list)
    for entity_item in m_n.get_category_entity("프룬이 먹고 싶어"):
        if entity_item.category.large == "test_mecab_data":
            assert entity_item.entity == "프룬"

    # 테스트 데이터 제거, 원래 테스트 데이터 사용
    python_mecab_ner_dir = Path(__file__).resolve().parent.parent.joinpath("python_mecab_ner", "data", "ner_data")
    m_d_w = MecabDataWriter(str(python_mecab_ner_dir), clear_mecab_dir=True)
    m_d_w.write_category()




def test_mecab_data_write(mecab_ner_dir):

    """
    ner_data를 읽은 뒤, mecab_data로 전환하는 테스트 코드
    - ner_data에서 읽었을 때의 개수와, mecab_data에서 읽었을 때의 개수가 같아야 한다.
    """

    m_n = MecabNer()
    for entity_item in m_n.get_category_entity("가봉에 가서 감이 먹고싶네"):
        print(entity_item)

# location데이터 => small 카테고리가 여러개
# body데이터 => "이"가 들어가있음
# fastfood 처음부터 #이 들어가 있지 않음
# song데이터 영어가 들어가 있음