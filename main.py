import copy
import math
from collections import defaultdict, Counter, deque
from pathlib import Path

from domain.mecab_domain import CategorySaveStorage, MecabTokenStorage, core_pos, neighbor_pos, core_noun
from python_mecab_ner.mecab_ner import MecabNer
from service.mecab_category_storage import set_cat_dict, get_load_storage, \
    NerExtractor, delete_duplicate, get_matched, get_category_entity_list, get_only_entity, CategorySave, \
    get_pos_seq_category, contains, get_bio_mecab_results

from service.mecab_parser import MecabParser, delete_pattern_from_string
from service.mecab_reader import get_ner_item_idx, get_ner_found_list
from service.mecab_storage import MecabStorage
import re
import pickle
import json
from sklearn_crfsuite import metrics
from sklearn.metrics import confusion_matrix


from tests.f1_test import *

# 2. 메캅 정보에서 마지막 엔티티만 추출
# 2-1. 마지막만 저장 / 엔티티가 저장. 엔티티 근처 위치에 core pos 저장.
# lv 1. core_pos는 일치해야함. 앞에 있는 NNG, NNP는 반드시 같은 카테고리에 다른 엔티티에서라도 본 글자여야 될 것.
# lv 2. 2단어 이상일 때 처리. 앞에 한 단어는 반드시 본 단어여야 할 것. ex) 루브르 박물관, 영덕 박물관 등 전부 처리 가능
# lv 3. core_pos는 core_pos_word에서 본 단어여야 할 것. "레몬 티"인 경우, "티"를 같은 범위에서 봤을 때
# lv 4. score 값을 매긴 후에 처리하기. log점수마다 log로 더하기
# lv 4. 생전 처음 보는 단어 core_pos는 일치하지 않아도 됨. 근처 범위에서 score_pos로 score를 매김. NNG, NNP는 일치해야함.

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


if __name__ == "__main__":
    test = "'바보의나눔 이사장직을 맡고 있는 염수정 주교는 “김수환 추기경님께서는 사회의 불의 앞에서는 엄하셨지만, 가난하고 힘없는 이들에게는 너무나 다정다감하고 자애로운 분이셨다”며 “바보의나눔은 추기경님의 따뜻한 사랑을 그리워하고 그 빈자리를 아쉬워하는 사람들을 위해 탄생했다”라고 설명했다.'"
    # category_save = CategorySave(sentence=test)
    test_str = "이라고 써있는 펜던트 보<맛있는 음료수:food>면서 설마 저거 <맛있는 음료수:food> 회전시킨 다음반전이라고 지껄이는건 아니겠지.."


    sentence = "훙레이 대변인은 “한반도 평화와 안정을 지키고 한반도 비핵화를 추진하는 것이 공통의 책임과 의무”라고 말했다."

    mecab_token_storage = defaultdict(MecabTokenStorage)

    # 학습 루프
    cnt_end = 150082 * 0.8
    # cnt_end = 7265 * 0.8
    cnt = 0
    cnt_stop = 5
    # 80%만큼만 추출


    all_value = []
    with open('python_mecab_ner/data/klue-ner-v1.1/NXNE2102008030.json', 'r', encoding='utf-8-sig') as json_file:
        # 키값 추출
        json_data = json.load(json_file)

        for json_document in json_data['document']:
            # 1. 모든 토큰 정보 메캅으로 분해
            ne_all_list = []
            token_all_info = []
            cnt += 1

            if cnt >= cnt_stop:
                break

            for idx, json_document_item in enumerate(json_document['sentence']):
                # cnt += 1
                if cnt >= cnt_end:
                    break
                sentence = json_document_item['form']
                if sentence == '':
                    continue
                category_save = CategorySave(sentence=sentence)
                # t, l = confirm_data(sentence, json_document_item["NE"])

                tf_idf_term = []

                ne_items = json_document_item["NE"]
                for json_document_ne in ne_items:
                    ne_label = json_document_ne['label']
                    ne_item = json_document_ne['form']
                    ne_begin = json_document_ne['begin']
                    ne_end = json_document_ne['end']
                    all_form = f"<{ne_item}:{ne_label}:{ne_begin}-{ne_end}>"
                    ne_all_list.append(all_form)
                    # category_save.set_bi_tag(ne_item, ne_label, ne_begin=ne_begin, ne_end=ne_end)
                    # if category_save.token_info != []:
                    #     token_all_info.append((ne_label, category_save.token_info))
                    zzz = list(MecabParser(sentence=ne_item).gen_mecab_compound_token_feature())
                    kkk = [(x[0], x[1].pos) for x in zzz]
                    print(json_document['id'], ne_label, kkk)
                    pos_seq = " ".join([x[1] for x in kkk])
                    mecab_token_storage[ne_label].core_key_word[pos_seq][(kkk[-1][0], kkk[-1][1])] = 1
                    pos_seq2 = "+".join([x[1] for x in kkk])
                    tf_idf_term.append(pos_seq2)
                all_value.append(tf_idf_term)
            # category_save.set_mecab_token_storage(mecab_token_storage, token_all_info)

    tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda x: x, lowercase=False)
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_value)
    a = 4

    # tfidf_vectorizer.vocabulary_

    import pandas as pd
    df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names())
    print(df)
    2
    import numpy as np

    D = len(tfidf_matrix)
    df = tfidf_matrix.astype(bool).sum(axis=0)
    idf = np.log((D + 1) / (df + 1)) + 1
    tfidf = tf * idf
    tfidf = tfidf / np.linalg.norm(tfidf, axis=1, keepdims=True)
x
    a=  4
    # with open('data_entity.pickle', 'wb') as f:
    #     pickle.dump(mecab_token_storage, f, pickle.HIGHEST_PROTOCOL)
    # with open('data_entity.pickle', 'rb') as f:
    #     data_entity = pickle.load(f)
    #
    # import time
    #
    # a = time.time()
    #
    # # 80%만큼만 추출
    # all_label = []
    # answer = []
    # test = []
    # cnt = 0
    # with open('python_mecab_ner/data/klue-ner-v1.1/NXNE2102008030.json', 'r', encoding='utf-8-sig') as json_file:
    #     # 키값 추출
    #     json_data = json.load(json_file)
    #
    #     for json_document in json_data['document']:
    #         cnt += 1
    #         if cnt <= cnt_stop:
    #             continue
    #
    #         if cnt >= cnt_stop + cnt_stop*0.2:
    #             break
    #
    #         for idx, json_document_item in enumerate(json_document['sentence']):
    #
    #             sentence = json_document_item['form']
    #             if sentence == '':
    #                 continue
    #             # cnt += 1
    #             # if cnt <= cnt_end:
    #             #     continue
    #             category_save = CategorySave(sentence=sentence)
    #
    #             # 1. 모든 토큰 정보 메캅으로 분해
    #             ne_all_list = []
    #             token_all_info = []
    #             for json_document_ne in json_document_item["NE"]:
    #                 ne_label = json_document_ne['label']
    #                 ne_item = json_document_ne['form']
    #                 ne_begin = json_document_ne['begin']
    #                 ne_end = json_document_ne['end']
    #                 all_form = f"<{ne_item}:{ne_label}:{ne_begin}-{ne_end}>"
    #                 ne_all_list.append(all_form)
    #                 category_save.set_bi_tag(ne_item, ne_label, ne_begin=ne_begin, ne_end=ne_end)
    #                 token_all_info.append((ne_label, category_save.token_info))
    #
    #             mecab_token_results = category_save.mecab_parse_tokens
    #             a_mecab_token_label = [x[1].label for x in mecab_token_results]
    #             answer.append(a_mecab_token_label)
    #             mecab_token_from_dictionary = get_bio_mecab_results(data_entity, sentence)
    #             # print([(x[0], x[1].label) for x in mecab_token_from_dictionary if x[1].label != "O"])
    #
    #
    #             a_mecab_dictionary_label = [x[1].label for x in mecab_token_from_dictionary]
    #             answers = []
    #             for token_item, dict_item in zip(mecab_token_results, mecab_token_from_dictionary):
    #                 if token_item[1].label != dict_item[1].label:
    #                     answers.append((dict_item[0], token_item[1].label, dict_item[1].label))
    #             print(answers)
    #
    #             test.append(a_mecab_dictionary_label)
    #             a = 4
    # print(cnt)
    # b = time.time()
    # print(b-a)
    # from seqeval.metrics import classification_report
    #
    # print(classification_report(answer, test))

    # 총 문장 수
    # sentence = "좋은 차를 마셨어"
    # mecab_token_from_dictionary = get_bio_mecab_results(mecab_token_storage, sentence)
    # z = 4

    #
    # test = "아~ 제목을 그냥 탄소 아~ 그리고 인간 원리 다중 우주 아~ 이런 제목을 잡았는데 어~ 뭐 뭐 물리학 하시는 분이나 천문학 하시는 분은 딱을 제목만 보고도 아~ 무슨 얘기할 거다라는 걸 아마 짐작을 하실 것 같습니다."
    #
    # a = get_bio_mecab_results(data_entity, test)
    # print(a)
    # all_label = []
    # answer = []
    # test = []
    # with open('python_mecab_ner/data/klue-ner-v1.1/SANE2100000895.json', 'r', encoding='utf-8-sig') as json_file:
    #     # 키값 추출
    #     json_data = json.load(json_file)
    #
    #     for json_document in json_data['document']:
    #
    #         for idx, json_document_item in enumerate(json_document['sentence']):
    #
    #             sentence = json_document_item['form']
    #             if sentence == '':
    #                 continue
    #             category_save = CategorySave(sentence=sentence)
    #             t, l = confirm_data(sentence, json_document_item["NE"])
    #
    #
    #             # 1. 모든 토큰 정보 메캅으로 분해
    #             ne_all_list = []
    #             token_all_info = []
    #             for json_document_ne in json_document_item["NE"]:
    #                 ne_label = json_document_ne['label'].split("_")[0]
    #                 all_label.append("B-" + ne_label)
    #                 all_label.append("I-" + ne_label)
    #                 ne_item = json_document_ne['form']
    #                 ne_begin = json_document_ne['begin']
    #                 ne_end = json_document_ne['end']
    #                 all_form = f"<{ne_item}:{ne_label}:{ne_begin}-{ne_end}>"
    #                 ne_all_list.append(all_form)
    #                 category_save.set_bi_tag(ne_item, ne_label, ne_begin=ne_begin, ne_end=ne_end)
    #                 token_all_info.append((ne_label, category_save.token_info))
    #
    #             category_save.set_mecab_token_storage(mecab_token_storage, token_all_info)
    #             mecab_token_results = category_save.mecab_parse_tokens
    #             mecab_token_label = [x[1].label for x in mecab_token_results]
    #             answer.append(mecab_token_label)
    #             mecab_token_from_dictionary = get_bio_mecab_results(data_entity, sentence)
    #             mecab_dictionary_label = [x[1].label for x in mecab_token_from_dictionary]
    #             test.append(mecab_dictionary_label)
    #
    #             b = 4


    #
    # ner_text = test.replace("3~5회", f"<3~5회:CV_OCCUPATION>")
    #
    # set_cat_dict(ner_text, data_entity)
    # entity_load_storage, entity_category_allowance = get_load_storage(data_entity)
    #
    # # intent_load_storage, intent_category_allowance = get_load_storage(data_entity)
    # #
    #
    #
    #
    # entity_list = get_category_entity_list(test, entity_load_storage, entity_category_allowance,
    #                                        intent_load_storage,
    #                                        intent_category_allowance, level=1, entity_only=True)
    # #
    # print([(x[0], x[5], x[6]) for x in entity_list])
    # import json
    #
    # with open('python_mecab_ner/data/klue-ner-v1.1/NXNE2102008030.json', 'r', encoding='utf-8-sig') as json_file:
    #     # 키값 추출
    #     json_data = json.load(json_file)
    #
    #     for json_document in json_data['document'][:50]:
    #         for json_document_item in json_document['sentence']:
    #
    #             ne_list = []
    #             for json_document_ne in json_document_item['NE']:
    #                 ner_text = json_document_item['form'].replace(json_document_ne['form'], f"<{json_document_ne['form']}:{json_document_ne['label']}>")
    #                 ne_list.append([f"<{json_document_ne['form']}:{json_document_ne['label']}>"])
    #                 # set_cat_dict(ner_text, category_dictionary)
    #
    #             entity_list = get_category_entity_list(json_document_item['form'], entity_load_storage, entity_category_allowance, intent_load_storage,
    #                                      intent_category_allowance, level=1, entity_only=True)
    #
    #             print(json_document_item['form'])
    #             print([(x[0], x[5], x[6]) for x in entity_list])
    #             print(ne_list)
    #             print("")
    #             print("======")
    #
    #
