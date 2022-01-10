from collections import Counter
import nltk
from nltk.stem.porter import *
from nltk.corpus import stopwords
from nltk import PorterStemmer
import math

nltk.download('stopwords')

class EngineTokenize:

    def __init__(self,indexes):
        self.english_stopwords = frozenset(stopwords.words('english'))
        self.manually_added_stopwords = []
        self.corpus_stopwords = ["category", "references", "also", "external", "links",
                                 "may", "first", "see", "history", "people", "one", "two",
                                 "part", "thumb", "including", "second", "following",
                                 "many", "however", "would", "became"] + self.manually_added_stopwords
        self.RE_WORD = re.compile(r"""[\#\@\w](['\-]?\w){2,24}""", re.UNICODE)
        self.all_stopwords = self.english_stopwords.union(self.corpus_stopwords)
        self.port_stemmer = PorterStemmer()
        self.indexes = indexes

    def tokenize(self, text, isBody=False,stemming=False):
        tokens = [token.group() for token in self.RE_WORD.finditer(text.lower())
                  if token.group() not in self.all_stopwords]  # Taking the relevant tokens.
        lst_of_tuples = []
        if isBody:
            if stemming:
                counter = Counter([self.port_stemmer.stem(token) for token in tokens])  # Using Counter().
                idf = self.indexes['w2idf']
            else:
                counter = Counter(tokens)
                idf = self.indexes['w2idf_not_stem']
            norm_sum = 0
            query_length = len(tokens)
            for token in counter:
                token_tfidf = (counter[token] / query_length) * idf[token]
                lst_of_tuples.append((token, token_tfidf))
                norm_sum += token_tfidf ** 2
            return lst_of_tuples, math.sqrt(norm_sum)
        else:
            counter = Counter(tokens)
            for token in counter:
                lst_of_tuples.append(token)
            return lst_of_tuples

    def stemming(self, text):
        tokens = self.tokenize(text)
        stem_token = Counter([self.port_stemmer.stem(token) for token in tokens])
        return stem_token
