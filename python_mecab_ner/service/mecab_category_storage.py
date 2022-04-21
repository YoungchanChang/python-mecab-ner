import re
from collections import defaultdict, Counter

from service.mecab_parser import MecabParser
from service.mecab_reader import get_ner_item_idx, get_ner_found_list

entity_last_pos = ["NNG","NNP","NNB","NNBC","NR","NP","VV","VA","MM","MAG","IC","JKG","JKB","JKV","JKQ","JX","JC","ETN","ETM","XPN","XSN","XSV","XSA","XR","SL","SH","SN",]
intent_last_pos = ["VV", "VA", "XSV", "XSA", "IC", "EP", "EF", "EC",]

class CategorySaveStorage:
    def __init__(self):
        self.pos_dict = defaultdict(set) # 포맷과 마지막 값을 확인
        self.word_dict = set() # 마지막 값을 확인
        self.counter_dict = Counter() # 검색용 점수 스코어 단어


class CategoryLoadStorage:
    def __init__(self):
        self.pos_dict = defaultdict(dict) # 포맷과 마지막 값을 확인
        self.word_dict = list() # 마지막 값을 확인
        self.counter_dict = Counter() # 검색용 점수 스코어 단어


def set_cat_dict(ner_text, category_dictionary, entity=True):
    mecab_parser = MecabParser()
    ner_target_list = re.findall(r"<([\d\w|가-힣|\s]+):([\d\w]+)>", ner_text)

    plain_text = re.sub(r"<([\d\w|가-힣|\s]+):([\d\w]+)>", r"\g<1>", ner_text)

    nert_item_idx = get_ner_item_idx(ner_text, ner_target_list)

    plain_mecab_result = list(mecab_parser.gen_mecab_compound_token_feature(plain_text))

    ner_found_list = get_ner_found_list(nert_item_idx, plain_mecab_result)

    for ner_found_item in ner_found_list:
        ner_token_val = ner_found_item[3]
        pos_seq = "+".join([x[1] for x in ner_token_val])

        token_core_val = []
        if entity:
            if ner_token_val[-1][1] in entity_last_pos:
                token_core_val = ner_token_val[-1]
        else:
            for ner_token_item in ner_token_val:
                if ner_token_item[1] in intent_last_pos:
                    token_core_val = ner_token_item
                    break

        if token_core_val != []:
            category_dictionary[ner_found_item[1]].pos_dict[pos_seq].add(token_core_val)
            category_dictionary[ner_found_item[1]].word_dict.add(ner_token_val[-1])
            category_dictionary[ner_found_item[1]].counter_dict += Counter(ner_token_val)


def get_load_storage(data_entity):
    data_load_storage = defaultdict(CategoryLoadStorage)
    data_category_allowance = defaultdict(list)
    for i in data_entity.items():
        cat, category_save = i
        tmp_pos_dict = {}
        for k in sorted(dict(category_save.pos_dict), key=len, reverse=True):
            tmp_pos_dict[k] = dict(category_save.pos_dict[k])
            data_category_allowance[k].append(cat)
        data_load_storage[cat].pos_dict = tmp_pos_dict
        data_load_storage[cat].word_dict = list(category_save.word_dict)
        data_load_storage[cat].counter_dict = category_save.counter_dict

    entity_allowed_category = {}
    for k in sorted(dict(data_category_allowance), key=len, reverse=True):
        entity_allowed_category[k] = data_category_allowance[k]

    return data_load_storage, data_category_allowance