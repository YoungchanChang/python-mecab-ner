# pygifconvt

## Table of Contents
  * [Installation](#installation)
  * [Quick start](#quick-start)
  * [Features](#features)
  
## Installation

Download using pip via pypi.

```bash
$ pip install 'package' --upgrade
  or
$ pip install git+'repository'
```
(Mac/homebrew users may need to use ``pip3``)


## Quick start
```python
from mecab_ner.mecab_parser import MeCabParser
mecab_parse_results = list(MeCabParser("나는 서울대병원에 갔어").gen_mecab_token_feature())
print(mecab_parse_results)

mecab_parse_compound_results = list(MeCabParser("나는 서울대병원에 갔어").gen_mecab_compound_token_feature())
print(mecab_parse_compound_results)
```

## Features
  * Python library to get NER using Mecab