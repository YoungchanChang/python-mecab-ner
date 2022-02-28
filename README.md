# mecab_ner

## Table of Contents
  * Installation
  * Quick start
  * Simple Example
  * Practical Example

## Installation

Download using pip via pypi.

```bash
$ pip install 'python-mecab-ner' --upgrade
```

(Mac/homebrew users may need to use ``pip3``)


## Simple Example

```python
from python_mecab_ner.mecab_ner import MecabNer

mecab_ner = MecabNer()
test_sentence = "아이유의 금요일에 만나요를 들으면서 신촌 딸기를 먹을래"

mecab_ner.parse(test_sentence)
# [('아이유', NerFeature(word='아이유', pos='ner', category=Category(large='ner_example_music_singer', small='가수'))), ('의', NerFeature(word='의', pos='JKG', category=None)), ('금요일에 만나요', NerFeature(word='금요일에 만나요', pos='ner', category=Category(large='ner_example_music_song', small='노래'))), ('를', NerFeature(word='를', pos='JKO', category=None)), ('듣', NerFeature(word='듣', pos='VV+EC', category=None)), ('으면서', NerFeature(word='으면서', pos='VV+EC', category=None)), ('신촌 딸기', NerFeature(word='신촌 딸기', pos='ner', category=Category(large='ner_example_fruit', small='과일'))), ('를', NerFeature(word='를', pos='JKO', category=None)), ('먹', NerFeature(word='먹', pos='VV', category=None)), ('을래', NerFeature(word='을래', pos='EC', category=None))]

mecab_ner.morphs(test_sentence)
['아이유', '의', '금요일에 만나요', '를', '듣', '으면서', '신촌 딸기', '를', '먹', '을래']

mecab_ner.ners(test_sentence)
# [('아이유', 'ner_example_music_singer', '가수'), ('금요일에 만나요', 'ner_example_music_song', '노래'), ('신촌 딸기', 'ner_example_fruit', '과일')]
```


## Practical Example

- Set `data path` for your work
- `File name` will become entity set `category large`


```
# Directory
root/
    word_dir.py
    data/
        test_data.txt
```

- Data file must be `txt` format and first line should start your small category
- `First line` will become entity set `category small`

```
# test_data.txt
#인공지능
파이썬
딥러닝
머신 러닝
자연어 처리
버트
#백엔드
로그
http통신
```

- ner : `('자연어 로그', 'programming', '백엔드')` is infered ner.
- if you don't want, set `MecabNer(infer=False)`  

```python
# example code
from python_mecab_ner.mecab_ner import MecabNer

mecab_ner = MecabNer(ner_path="./data")
test_sentence = "자연어 처리를 위해 인공지능을 위한 파이썬을 공부하여 자연어와 관련된 일을 하고 있습니다. http 요청시 자연어 로그를 쌓는 것이 중요합니다."

mecab_ner.parse(test_sentence)
# [('자연어 처리', NerFeature(word='자연어 처리', pos='ner', category=Category(large='programming', small='인공지능'))), ('를', NerFeature(word='를', pos='JKO', category=None)), ('위하', NerFeature(word='위하', pos='VV+EC', category=None)), ('아', NerFeature(word='아', pos='VV+EC', category=None)), ('인공', NerFeature(word='인공', pos='NNP', category=None)), ('지능', NerFeature(word='지능', pos='NNP', category=None)), ('을', NerFeature(word='을', pos='JKO', category=None)), ('위하', NerFeature(word='위하', pos='VV+ETM', category=None)), ('ᆫ', NerFeature(word='ᆫ', pos='VV+ETM', category=None)), ('파이썬', NerFeature(word='파이썬', pos='ner', category=Category(large='programming', small='인공지능'))), ('을', NerFeature(word='을', pos='JKO', category=None)), ('공부', NerFeature(word='공부', pos='NNG', category=None)), ('하', NerFeature(word='하', pos='XSV', category=None)), ('여', NerFeature(word='여', pos='EC', category=None)), ('자연', NerFeature(word='자연', pos='NNG', category=None)), ('어', NerFeature(word='어', pos='NNG', category=None)), ('와', NerFeature(word='와', pos='JC', category=None)), ('관련', NerFeature(word='관련', pos='NNG', category=None)), ('되', NerFeature(word='되', pos='XSV+ETM', category=None)), ('ᆫ', NerFeature(word='ᆫ', pos='XSV+ETM', category=None)), ('일', NerFeature(word='일', pos='NNG', category=None)), ('을', NerFeature(word='을', pos='JKO', category=None)), ('하', NerFeature(word='하', pos='VV', category=None)), ('고', NerFeature(word='고', pos='EC', category=None)), ('있', NerFeature(word='있', pos='VX', category=None)), ('습니다', NerFeature(word='습니다', pos='EF', category=None)), ('.', NerFeature(word='.', pos='SF', category=None)), ('http', NerFeature(word='http', pos='SL', category=None)), ('요청', NerFeature(word='요청', pos='NNG', category=None)), ('시', NerFeature(word='시', pos='NNB', category=None)), ('자연어 로그', NerFeature(word='자연어 로그', pos='ner', category=Category(large='programming', small='백엔드'))), ('를', NerFeature(word='를', pos='JKO', category=None)), ('쌓', NerFeature(word='쌓', pos='VV', category=None)), ('는', NerFeature(word='는', pos='ETM', category=None)), ('것', NerFeature(word='것', pos='NNB', category=None)), ('이', NerFeature(word='이', pos='JKS', category=None)), ('중요', NerFeature(word='중요', pos='NNG', category=None)), ('하', NerFeature(word='하', pos='XSV+EF', category=None)), ('ᄇ니다', NerFeature(word='ᄇ니다', pos='XSV+EF', category=None)), ('.', NerFeature(word='.', pos='SF', category=None))]

mecab_ner.morphs(test_sentence)
# ['자연어 처리', '를', '위하', '아', '인공', '지능', '을', '위하', 'ᆫ', '파이썬', '을', '공부', '하', '여', '자연', '어', '와', '관련', '되', 'ᆫ', '일', '을', '하', '고', '있', '습니다', '.', 'http', '요청', '시', '자연어 로그', '를', '쌓', '는', '것', '이', '중요', '하', 'ᄇ니다', '.']


mecab_ner.ners(test_sentence)
# [('자연어 처리', 'programming', '인공지능'), ('파이썬', 'programming', '인공지능'), ('자연어 로그', 'programming', '백엔드')]
```

## Features
  * Python library to get NER using Mecab