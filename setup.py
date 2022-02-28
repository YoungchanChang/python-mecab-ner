from setuptools import setup, find_packages
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name             = 'python-mecab-ner',
    version          = '1.0.5',
    description      = 'Test package for distribution',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author           = 'Youngchan',
    author_email     = 'gamsunghacker@gmail.com',
    url              = 'https://github.com/YoungchanChang/python-mecab-ner',
    download_url     = '',
    install_requires = ['pybind11 ~= 2.0', "python-mecab-ko ~= 1.0.12"],
    keywords         = ['Text Processing', 'Text Processing :: Linguistic', 'NER', "mecab", "mecab-ko", "mecab-ner"],
    python_requires  = '>=3.7',
    zip_safe=False,
    classifiers      = [
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3 :: Only',
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Science/Research',
        'Natural Language :: Korean',
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.py"],
    }
)

