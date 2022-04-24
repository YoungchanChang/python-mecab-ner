import math
import re
from collections import defaultdict, Counter, deque
import copy

from service.mecab_parser import MecabParser
from service.mecab_reader import get_ner_item_idx, get_ner_found_list
from service.mecab_storage import MecabStorage

entity_last_pos = ["NNG","NNP","NNB","NNBC","NR","NP","VV","VA","MM","MAG","IC","JKG","JKB","JKV","JKQ","JX","JC","ETN","ETM","XPN","XSN","XSV","XSA","XR","SY", "SL","SH","SN",]
intent_last_pos = ["VV", "VA", "XSV", "XSA", "IC", "EP", "EF", "EC",]
duplicate_pos = ["NNG","NNP", "VV", "VA"]


STRICT_CORE = 0
LOOSE_CORE = 1
PART_INFER = 2
BRUTE_INFER = 3


class CategorySaveStorage:
    def __init__(self):
        self.pos_dict = defaultdict(set) # 포맷과 마지막 값을 확인
        self.word_dict = set() # 마지막 값을 확인
        self.counter_dict = Counter() # 검색용 점수 스코어 단어
        self.counter_near_dict = Counter()  # 검색용 점수 스코어 단어


class CategoryLoadStorage:
    def __init__(self):
        self.pos_dict = defaultdict(dict) # 포맷과 마지막 값을 확인
        self.word_dict = list() # 마지막 값을 확인
        self.counter_dict = Counter() # 검색용 점수 스코어 단어
        self.counter_near_dict = Counter()  # 검색용 점수 스코어 단어


def get_only_entity(plain_mecab_result):
    mecab_storage = MecabStorage()
    bio_all_list = []
    bio_item = []
    for plain_mecab_item in plain_mecab_result:
        plain_word, mecab_feature = plain_mecab_item
        if mecab_feature.label.startswith("I"):
            bio_item.append(plain_mecab_item)

        elif mecab_feature.label.startswith("B"):
            if bio_item != []:
                bio_all_list.append(bio_item)
                bio_item = []
            bio_item.append(plain_mecab_item)

        elif mecab_feature.label == "O" and bio_item != []:
            bio_all_list.append(bio_item)
            bio_item = []

    filter_ne_list = []
    for bio_each_item in bio_all_list:
        answer = mecab_storage.reverse_compound_tokens(bio_each_item)
        answer = " ".join(answer)
        begin_idx = bio_each_item[0][1].begin
        end_idx = begin_idx + len(answer)
        label = bio_each_item[0][1].label.replace("B-", "")
        all_form = f"<{answer}:{label}:{begin_idx}-{end_idx}>"
        filter_ne_list.append(all_form)
    return filter_ne_list

def set_bi_tag(sentence, plain_mecab_result, ne_item, label, ne_begin=None, ne_end=None):
    mecab_parser = MecabParser()

    if ne_begin is None:
        ne_begin = sentence.find(ne_item)
        ne_end = sentence.find(ne_item) + len(ne_item)

    document_ne_items = ne_item.split()

    for ne_idx, document_ne_item in enumerate(document_ne_items):
        exact_idx_string = document_ne_item

        if ne_idx == 0:
            status = "B-"
        else:
            status = "I-"

        for plain_idx, plain_mecab_item in enumerate(plain_mecab_result):

            if (exact_idx_string.startswith("*")): #물리학, 한 지점, 천문학잔데 - 잔데 # 하난데 - 하나 인데, 73, 110
                status = "I-"

            exact_idx_string = exact_idx_string.replace("*", "")
            if exact_idx_string == "":
                break



            plain_mecab_word, plain_mecab_feature = plain_mecab_item
            # print(plain_mecab_word)
            if ne_begin >= plain_mecab_item[1].begin and ne_begin <= plain_mecab_feature.end and plain_mecab_feature.label == "O":
                exact_idx_string_return = mecab_parser.get_exact_idx(plain_mecab_feature, exact_idx_string,
                                                              plain_mecab_feature.word, change_compound=False)
                exact_idx_string = exact_idx_string_return
                plain_mecab_result[plain_idx][1].label = status + label
            elif ne_end >= plain_mecab_item[1].begin and ne_end <= plain_mecab_feature.end and plain_mecab_feature.label == "O":
                exact_idx_string_return = mecab_parser.get_exact_idx(plain_mecab_feature, exact_idx_string,
                                                              plain_mecab_feature.word, change_compound=False)
                exact_idx_string = exact_idx_string_return
                plain_mecab_result[plain_idx][1].label = status + label
            elif plain_mecab_feature.begin >= ne_begin and plain_mecab_feature.end <= ne_end and plain_mecab_feature.label == "O":
                exact_idx_string_return = mecab_parser.get_exact_idx(plain_mecab_feature, exact_idx_string,
                                                              plain_mecab_feature.word, change_compound=False)
                exact_idx_string = exact_idx_string_return
                plain_mecab_result[plain_idx][1].label = status + label




def set_cat_dict(ner_text, category_dictionary, entity=True):
    DUPLICATE_DISTANCE = 2
    mecab_parser = MecabParser()

    regex_expression = r"<([^:]+):([\d\w]+)>"
    ner_target_list = re.findall(regex_expression, ner_text)

    plain_text = re.sub(regex_expression, r"\g<1>", ner_text)

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

            counter_near_list = []
            for i in range(max(0, ner_found_item[2][0] - DUPLICATE_DISTANCE), min(len(plain_mecab_result), ner_found_item[2][0] + DUPLICATE_DISTANCE), 1):
                for plan_mecab_item in plain_mecab_result:
                    if plan_mecab_item[1].space == i:
                        counter_near_list.append((plan_mecab_item[1].word, plan_mecab_item[1].pos))
            category_dictionary[ner_found_item[1]].counter_near_dict += Counter(counter_near_list)

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
        data_load_storage[cat].counter_near_dict = category_save.counter_near_dict

    entity_allowed_category = {}
    for k in sorted(dict(data_category_allowance), key=len, reverse=True):
        entity_allowed_category[k] = data_category_allowance[k]

    return data_load_storage, entity_allowed_category


def contains(small, big):
    # 정보의 순서가 중요할 때 사용
    contain_all = []
    for i in range(len(big) - len(small) + 1):
        for j in range(len(small)):
            if big[i + j][1].pos != small[j]:
                break
        else:
            # i와 i + len(small)
            contain_all.append((i, i + len(small)))
    return contain_all


class NerExtractor:
    meaning = ["NNG", "NNP", "VV", "VA"]

    def __init__(self):
        self.mecab_storage = MecabStorage()

    def get_token_core_val(self, mecab_parse_token, pos_seq_range, entity):
        if entity:
            return mecab_parse_token[pos_seq_range[1] - 1]  # 마지막 글자 일치 정책
        else:
            for mecab_token_item in mecab_parse_token[pos_seq_range[0]: pos_seq_range[1]]:
                if mecab_token_item[1].pos in intent_last_pos:
                    return mecab_token_item
        return ("*", "CK")

    def get_token_value(self, mecab_parse_token, pos_seq_range):
        token_found = mecab_parse_token[pos_seq_range[0]:pos_seq_range[1]]
        restored_tokens = self.mecab_storage.reverse_compound_tokens(token_found)
        token_idx = int(sum([x[1].mecab_compound for x in token_found]) / len(token_found))
        return token_found, restored_tokens, token_idx


    def validate_value(self, pos_category_item, mecab_parse_token, data_load_storage, pos_seq_range, strict=True):
        for token_found_item in mecab_parse_token[pos_seq_range[0]: pos_seq_range[1]]:
            if strict:
                if token_found_item[1].pos in self.meaning:
                    dict_found = data_load_storage[pos_category_item].counter_dict.get(
                        (token_found_item[1].word, token_found_item[1].pos), None)
                    if dict_found is None:
                        raise ValueError("Not proper")
            else:
                if token_found_item[1].pos in entity_last_pos:
                    dict_found = data_load_storage[pos_category_item].counter_near_dict.get(
                        (token_found_item[1].word, token_found_item[1].pos), None)
                    if dict_found is None:
                        raise ValueError("Not proper")

    def get_entity(self, mecab_parse_token, data_load_storage, data_category_allowance, not_found_deque, entity=True, strict=False):
        """
        단어 매칭 함수
        """

        if strict:
            key = "strict_core"
        else:
            key = "loose_core"

        data_list = []
        for pos_seq_key, pos_allow_category in data_category_allowance.items(): # 모든 형태소 키값에 대해서 검사 수행
            i_split = pos_seq_key.split("+")
            pos_seq_contain_list = contains(i_split, mecab_parse_token)

            for pos_seq_range in pos_seq_contain_list: # 형태소 키값의 범위에 대해 수행
                token_found = None

                for pos_category_item in pos_allow_category: # 허용된 카테고리만큼 loop
                    data_category_item = data_load_storage[pos_category_item].pos_dict[pos_seq_key]

                    token_core_val = self.get_token_core_val(mecab_parse_token, pos_seq_range, entity)

                    # 마지막 단어가 일치하는 경우에만 진행
                    for category_key, category_item in data_category_item.items():
                        if token_core_val[0] == category_key and token_core_val[1].pos == category_item:

                            try:
                                if strict:
                                    self.validate_value(pos_category_item, mecab_parse_token, data_load_storage,
                                                        pos_seq_range)
                                else:
                                    self.validate_value(pos_category_item, mecab_parse_token, data_load_storage,
                                                        pos_seq_range, strict=False)
                                token_found, restored_tokens, token_idx = self.get_token_value(mecab_parse_token, pos_seq_range)

                                if len(token_found) == 1 and token_found[0][1].type == "Compound":
                                    # 한 단어인데 복합어에 속해있는 경우 스킵
                                    continue

                                data_list.append((pos_category_item, pos_seq_key, token_idx, copy.deepcopy(token_core_val), copy.deepcopy(token_found), restored_tokens, key))
                            except ValueError as ve:
                                ...

                if token_found:
                    for j in range(pos_seq_range[0], pos_seq_range[1], 1):
                        mecab_parse_token[j][1].pos = "CK"
                        mecab_parse_token[j][1].word = "*"
                else:
                    token_found = mecab_parse_token[pos_seq_range[0]: pos_seq_range[1]]
                    not_found_deque.append((pos_seq_key, tuple(token_found), pos_seq_range))
        return data_list

    def set_infer_ner(self, mecab_parse_token, entity_list, entity_load_storage, not_found_entity_deque, brute=False):
        inference_deque = deque()
        infer_list = []

        if brute:
            key = "brute_infer"
        else:
            key = "part_infer"

        # 형태소는 맞지만 마지막 단어가 매칭되지 않은 경우 찾기
        value = True
        while value:
            try:
                value = not_found_entity_deque.popleft()

                if value[2][0] in infer_list and brute:
                    continue

                if mecab_parse_token[value[2][0]][1].pos == "CK":
                    continue


                value_split = value[0].split("+")
                max_score = -math.inf
                entity_key = None

                for entity_load_key, entity_load_storage_item in entity_load_storage.items():
                    score = 0
                    for idx, value_item in enumerate(value_split):
                        if value[1] and value_item in self.meaning:

                            if brute:
                                for i in range(max(0, value[2][0] - 2), min(len(mecab_parse_token), value[2][1] + 2),
                                               1):
                                    score += entity_load_storage[entity_load_key].counter_dict.get(
                                        (mecab_parse_token[i][1].word, mecab_parse_token[i][1].pos), 0)
                            else:
                                if (value[1][idx][1].word, value[1][idx][1].pos) in entity_load_storage[entity_load_key].word_dict:
                                    score += 1
                    if score > max_score:
                        max_score = score
                        entity_key = entity_load_key

                if max_score > 0:

                    if brute:
                        infer_list.extend(list(range(max(0, value[2][0]), min(len(mecab_parse_token), value[2][1]))))

                    token_core_val = self.get_token_core_val(mecab_parse_token, value[2], entity=True)
                    token_found, restored_tokens, token_idx = self.get_token_value(mecab_parse_token, value[2])

                    for j in range(value[2][0], value[2][1], 1):
                        mecab_parse_token[j][1].pos = "CK"
                        mecab_parse_token[j][1].word = "*"

                    entity_list.append((entity_key, value[0], token_idx, copy.deepcopy(token_core_val),
                                        copy.deepcopy(token_found), restored_tokens, key))
                elif brute is False:
                    inference_deque.append(value)
            except IndexError as ie:
                value = False
        return inference_deque


def get_matched(entity_list: list, intent_list: list):
    matched = []
    for entity_item in entity_list:
        max_score = math.inf
        matched_intent = None
        for intent_item in intent_list:
            distance = abs(entity_item[2] - intent_item[2])
            if entity_item[0] == intent_item[0] and distance <= max_score:
                matched_intent = intent_item
                max_score = distance

        if matched_intent:
            if matched_intent[2] > entity_item[2]:
                min_val = entity_item[4][0][1].mecab_compound
            else:
                min_val = matched_intent[4][0][1].mecab_compound

            matched.append([entity_item, matched_intent, min_val])
    return matched


def delete_duplicate(mecab_parse_token, data_list, data_load_storage):

    DUPLICATE_DISTANCE = 5

    """
    중의어 제거하는 함수
    근처에 있는 단어의 word of bag을 전부 더한다.
    """

    duplicate_filter = defaultdict(list)
    for entity_item in data_list:
        duplicate_filter[entity_item[1] + entity_item[3][0]].append(entity_item)

    for duplicate_key, duplicate_value in duplicate_filter.items():
        if len(duplicate_value) >= 2:
            max_score = -math.inf
            max_value = None
            for duplicate_item in duplicate_value:
                mecab_token_idx = duplicate_item[3][1].mecab_compound
                score = 0
                for i in range(max(0,mecab_token_idx-DUPLICATE_DISTANCE), min(len(mecab_parse_token), mecab_token_idx+DUPLICATE_DISTANCE), 1):
                    if i == mecab_token_idx:
                        continue
                    mecab_found_idx = mecab_parse_token[i]

                    if mecab_found_idx[1].pos not in duplicate_pos:
                        continue

                    score += data_load_storage[duplicate_item[0]].counter_dict.get((mecab_found_idx[1].word, mecab_found_idx[1].pos), 0)
                    score += data_load_storage[duplicate_item[0]].counter_near_dict.get(
                        (mecab_found_idx[1].word, mecab_found_idx[1].pos), 0)
                if score > max_score:
                    max_score = score
                    max_value = duplicate_item

            for duplicate_item in duplicate_value:
                if duplicate_item != max_value:
                    data_list.remove(duplicate_item)

def get_category_entity_list(sentence, entity_load_storage, entity_category_allowance, intent_load_storage, intent_category_allowance, level, entity_only=True):
    mecab_parser = MecabParser()
    mecab_storage = MecabStorage()

    mecab_parse_token = list(mecab_parser.gen_mecab_compound_token_feature(sentence))

    ner_extractor = NerExtractor()

    not_found_entity_deque = []
    not_found_intent_deque = []
    entity_list = ner_extractor.get_entity(mecab_parse_token, entity_load_storage, entity_category_allowance, not_found_entity_deque, entity=True, strict=True)

    if level >= LOOSE_CORE:
        entity_not_strict_list = ner_extractor.get_entity(mecab_parse_token, entity_load_storage, entity_category_allowance,
                                               not_found_entity_deque, entity=True, strict=False)
        entity_list.extend(entity_not_strict_list)

    if entity_only is False:
        intent_list = ner_extractor.get_entity(mecab_parse_token, intent_load_storage, intent_category_allowance, not_found_intent_deque, entity=False)

    if level >= PART_INFER:

        not_found_entity_deque = deque(sorted(not_found_entity_deque, key=lambda x: len(x[0]), reverse=True))
        inference_deque = ner_extractor.set_infer_ner(mecab_parse_token, entity_list, entity_load_storage, not_found_entity_deque)

        if level >= BRUTE_INFER:
            brute_inference_deque = ner_extractor.set_infer_ner(mecab_parse_token, entity_list, entity_load_storage,
                                                          inference_deque, brute=True)

    if entity_only:
        duplicate_find_tokens= list(mecab_parser.gen_mecab_compound_token_feature(sentence))
        delete_duplicate(duplicate_find_tokens, entity_list, entity_load_storage)


    if entity_only is False:
        mecab_parse_token = list(mecab_parser.gen_mecab_compound_token_feature(sentence))

        matched_list = get_matched(entity_list, intent_list)
        matched_list = sorted(matched_list, key=lambda x : x[2], reverse=True)
        last_val = len(mecab_parse_token)
        for matched_item in matched_list:
            entity_list.remove(matched_item[0])
            intent_list.remove(matched_item[1])
            token_found = mecab_parse_token[matched_item[2]: last_val]
            restored_tokens = mecab_storage.reverse_compound_tokens(token_found)
            last_val = matched_item[2]
            print(restored_tokens, matched_item[0][6])

    if entity_only:
        return entity_list
    else:
        return matched_list