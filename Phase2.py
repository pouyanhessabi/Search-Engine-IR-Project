import pickle
from math import log

from Phase1 import read_data, urls


def tf_idf(term: str):
    score = []
    number_of_all_docs = len(urls)
    nt = len(positional_index[term])
    for document in positional_index[term]:
        tf = len(positional_index[term][document])
        score.append((1 + log(tf)) * (log(number_of_all_docs / nt)))
    term_score[term] = sum(score)


read_data()
"""
If file of positional index doesn't create, run codes below
# url_token_content = pre_processing()
# positional_index = construct_positional_index(url_token_content)
"""

"""
Skip pre processing and positional index, only reading file 
"""
pos_index_file = open("data.pkl", "rb")
positional_index = pickle.load(pos_index_file)
pos_index_file.close()
term_score = {}

for term in positional_index:
    tf_idf(term)
