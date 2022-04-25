from collections import Counter
from sklearn.metrics import classification_report
from sklearn.metrics import precision_score, recall_score, f1_score
from service.mecab_category_storage import get_only_entity, CategorySave
from service.mecab_parser import MecabParser

test = [['B-LOC', 'O', 'B-LOC', 'O', 'O', 'O', 'O', 'O', 'B-ORG', 'B-ORG', 'O'], ['B-LOC', 'O', 'B-LOC', 'O', 'O', 'O', 'O', 'O', 'B-ORG', 'B-ORG', 'O']]
test2 = [['B-LOC', 'O', 'B-LOC', 'O', 'O', 'O', 'O', 'O', 'B-ORG', 'B-ORG', 'O'], ['B-LOC', 'O', 'B-LOC', 'O', 'O', 'O', 'O', 'O', 'B-ORG', 'O', 'O']]
labels = ['B-LOC', 'B-ORG', 'B-PER', 'I-PER', 'B-MISC', 'I-ORG', 'I-LOC', 'I-MISC']

from seqeval.metrics import classification_report

print(classification_report(test, test2))


def confirm_data(sentence, all_document_ne):

    category_save = CategorySave(sentence=sentence)
    ne_all_list = []
    for json_document_ne in all_document_ne:
        ne_label = json_document_ne['label']
        ne_item = json_document_ne['form']
        ne_begin = json_document_ne['begin']
        ne_end = json_document_ne['end']
        all_form = f"<{ne_item}:{ne_label}:{ne_begin}-{ne_end}>"
        ne_all_list.append(all_form)
        category_save.set_bi_tag(ne_item, ne_label, ne_begin=ne_begin, ne_end=ne_end)

    if ne_all_list != []:
        new_list = get_only_entity(category_save.mecab_parse_tokens)
        total_length = len(new_list)
        if ne_all_list != new_list:
            s1 = set(new_list) - set(ne_all_list)
            diff_length = len(s1)

            print(sentence, ne_all_list, new_list)
            return total_length, diff_length
        return total_length, 0
    return 0, 0