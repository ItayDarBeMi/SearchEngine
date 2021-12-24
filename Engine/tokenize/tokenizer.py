import sys
from collections import Counter, OrderedDict
import itertools
from itertools import islice, count, groupby
import pandas as pd
import os
import re
from operator import itemgetter
import nltk
from nltk.stem.porter import *
from nltk.corpus import stopwords
from nltk import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from time import time
from timeit import timeit
from pathlib import Path
import pickle
import numpy as np


nltk.download('stopwords')


class Tokenizer:

    def __init__(self, corpus_path: str) -> None:
        self.df = pd.read_parquet(corpus_path)[:500]
        self.eng_stopwords = frozenset(stopwords.words('english'))
        self.corpus_stopwords = ['category', 'references', 'also', 'links', 'extenal', 'see', 'thumb']
        self.stopwords = self.eng_stopwords.union(self.corpus_stopwords)
        self.RE_WORD = re.compile(r"""[\#\@\w](['\-]?\w){2,24}""", re.UNICODE)
        self.port_stemmer = PorterStemmer()

    def term_doc_frequency(self):
        '''
        Do: for each term, save list of all the documents that is in
        Returns: {term: [(id,number),...]}
        '''
        term_doc = {}
        all_corpus_count = self.count_all_corpus()
        for id in all_corpus_count:
            for term in all_corpus_count[id]:
                if term in term_doc:
                    term_doc.append((id,all_corpus_count[id][term]))
                else:
                    term_doc = [(id,all_corpus_count[id][term])]
        return term_doc

    def count_all_corpus(self):
        all_postings_list = {}
        for i in range(self.df.shape[0]):
            text = self.df.iloc[i]['text']
            id = self.df.iloc[i]['id']
            all_postings_list[id] = self.count_words(
                text=text
            )
        return all_postings_list

    def count_words(self, text):
        tokens = [token.group() for token in self.RE_WORD.finditer(text.lower()) if token.group() not in self.stopwords]
        stem_token = Counter([self.port_stemmer.stem(token) for token in tokens])
        return stem_token