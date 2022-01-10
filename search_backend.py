from tqdm import tqdm
import numpy as np
from collections import Counter
from threading import Thread
from Engine.tokenize import EngineTokenize
from Engine.files_handler import ReadPostingsCloud


class SearchFunctions:

    def __init__(self):
        self.reader = ReadPostingsCloud("search_engine_buceket")
        self.indexes = {
            "title": self.reader.get_inverted_index(source_idx=f"postings_gcp_title/index.pkl", dest_file=f"index.pkl"),
            "body": self.reader.get_inverted_index(source_idx=f"postings_gcp_body/index.pkl", dest_file=f"index.pkl"),
            "body_not_stem": self.reader.get_inverted_index(source_idx=f"postings_gcp_body_not_stem/index.pkl",
                                                       dest_file=f"index.pkl"),
            "anchor": self.reader.get_inverted_index(source_idx=f"postings_gcp_anchor/index.pkl", dest_file=f"index.pkl"),
            "docs_norm": self.reader.get_pickle_file("docs_norm.pkl", "docs_norm.pkl"),
            "docs_length": self.reader.get_pickle_file("id_length.pkl", "id_length.pkl"),
            "w2idf": self.reader.get_pickle_file("w2idf.pkl", "w2idf.pkl"),
            "docs_norm_not_stem": self.reader.get_pickle_file("docs_norm_not_stem.pkl", "docs_norm_not_stem.pkl"),
            "w2idf_not_stem": self.reader.get_pickle_file("w2idf_not_stem.pkl", "w2idf_not_stem.pkl"),
            "id_to_title": self.reader.get_pickle_file("id_title_index.pkl", "id_title_index.pkl"),
            "page_rank": self.reader.get_pickle_file("pagerank.pkl", "pagerank.pkl"),
            "pageviews": self.reader.get_pickle_file("pageviews.pkl", "pageviews.pkl"),
        }
        self.tokenize_engine = EngineTokenize(
            {
                'w2idf': self.indexes['w2idf'],
                'w2idf_not_stem': self.indexes['w2idf_not_stem'],
            }
        )

        self.body_res: list = []
        self.title_res: list = []

    def main_engine_search(self, query: str) -> list:
        threads_lst = [
            Thread(target=self.body, args=[query, True]),
            Thread(target=self.title, args=[query, True])
        ]

        for trd in threads_lst:
            trd.start()
        threads_lst[0].join()
        threads_lst[1].join()
        id_titles = {x[0]:x[1] for x in self.title_res}
        res = []
        for i,val in enumerate(self.body_res):
            id = val[0]
            if id in id_titles:
                res.append((id,self.body_res[i][1]+id_titles[id]))
            else:
                res.append((id, self.body_res[i][1]))
        res = sorted(res,key=lambda x:x[1],reverse=True)[:100]
        return [(item[0], self.indexes["id_to_title"][item[0]]) for item in res if item[0] in self.indexes["id_to_title"]]

    def body(self, query: str, main_search: bool = True) -> list:
        dict = {}
        sim_results = []
        if main_search:
            query_tokenized, query_norm = self.tokenize_engine.tokenize(query,
                                                                   isBody=True,
                                                                   stemming=True)
            index_name = 'body'
            docs_norm = "docs_norm"
            index_body = self.indexes[index_name]
        else:
            query_tokenized, query_norm = self.tokenize_engine.tokenize(query,
                                                                   isBody=True)
            index_name = 'body_not_stem'
            docs_norm = "docs_norm_not_stem"
            index_body = self.indexes[index_name]
        for w_pl in query_tokenized:
            w, query_tfidf = w_pl
            doc_w_pl = self.reader.read_posting_list(index_body, w, index_name,isBody=True)
            for postings_list_item in tqdm(doc_w_pl[:10000]):
                id, tfidf = postings_list_item
                try:
                    tfidf = tfidf/self.indexes["docs_length"][id] if main_search else tfidf
                except KeyError:
                    continue
                if id not in dict:
                    dict[id] = np.dot(tfidf, query_tfidf)
                else:
                    dict[id] = dict[id] + np.dot(tfidf, query_tfidf)
        for doc_id in dict:
            sim_results.append((doc_id, dict[doc_id] / np.dot(self.indexes[docs_norm][doc_id], query_norm)))
        res = sorted(sim_results, key=lambda x: x[1], reverse=True)
        if main_search:
            self.body_res = res
            return res
        res = [(i[0], self.indexes['id_to_title'][i[0]]) for i in res]
        return res[:100]

    def title(self, query, main_search=False):
        res = []
        query = self.tokenize_engine.tokenize(query)
        for w in query:
            pl = self.reader.read_posting_list(self.indexes["title"], w, 'title')
            res += [did[0] for did in pl if did[0] in self.indexes["id_to_title"]]
        res = sorted(Counter(res).items(), key=lambda x: x[1], reverse=True)
        if main_search:
            self.title_res = res
            return res
        res = [(item[0], self.indexes["id_to_title"][item[0]]) for item in res]
        return res

    def anchor_text(self, query:str, main_search=False) -> list:
        res = []
        query = self.tokenize_engine.tokenize(query)
        for w in query:
            pl = self.reader.read_posting_list(self.indexes["anchor"], w, 'anchor')
            res += [did[0] for did in pl if did[0] in self.indexes["id_to_title"]]
        res = sorted(Counter(res).items(), key=lambda x: x[1], reverse=True)
        if main_search:
            self.anchor_res = res
            return res
        return [(item[0], self.indexes["id_to_title"][item[0]]) for item in res]

    def pagerank(self, wiki_ids):
        res = []
        for article_id in wiki_ids:
            res.append(self.indexes["page_rank"][article_id])
        return res

    def pageviews(self, wiki_ids):
        res = []
        for article_id in wiki_ids:
            res.append(self.indexes["pageviews"][article_id])
        return res
