import pickle
from math import log, sqrt

import pandas as pd
from hazm import Stemmer


# def tf_idf(term: str):
#     score = []
#     number_of_all_docs = len(urls)
#     nt = len(positional_index[term])
#     for document in positional_index[term]:
#         tf = len(positional_index[term][document])
#         score.append((1 + log(tf)) * (log(number_of_all_docs / nt)))
#     term_score[term] = sum(score)
def read_data():
    df = pd.read_json(path_or_buf='IR_data_news_12k.json', orient='index')
    for index, row in df.iterrows():
        urls.append(row['url'])
        url_title[row['url']] = row['title']
        url_content[row['url']] = row['content']
        # if index > 2000:
        #     break


def get_query(query: str):
    query = query.replace('"', "").split()
    negative_words = []
    positive_words = []
    for word in query:
        if "!" in word:
            negative_words.append(word.replace("!", ""))
        else:
            positive_words.append(word)
    return positive_words, negative_words


def construct_term_idf(term_posting: dict):
    term_idf_dictionary = {}
    for term in positional_index:
        term_idf_dictionary[term] = log(len(urls) / len(term_posting[term]))
    return term_idf_dictionary


def calculate_tf(term: str, document: int):
    return float("{0:.3f}".format(1 + log(len(positional_index[term][document]))))


def construct_document_term_score_for_document():
    """
    Note: this matrix is only for documents, then SCALAR PRODUCT OF TWO VECTORS: documents * query
    document_term_score = {key: document(int) | value: term_score(dict)}
    term_score = {key: term(int) | value: number(int)}
    """
    document_term_score = {}
    for term in positional_index:
        for document in positional_index[term]:
            if document in document_term_score:
                document_term_score[document][term] = len(positional_index[term][document])
            else:
                document_term_score[document] = {term: len(positional_index[term][document])}

    # Log(tf) and sum of them:
    sum_ = []
    for document in document_term_score:
        for term in document_term_score[document]:
            document_term_score[document][term] = float("{0:.3f}".format(1 + log(document_term_score[document][term])))
            sum_.append(pow(document_term_score[document][term], 2))
    # Normalize
    normalized_factor = 1 / sqrt(sum(sum_))
    for document in document_term_score:
        for term in document_term_score[document]:
            document_term_score[document][term] *= normalized_factor

    return document_term_score


def construct_term_query_score(term_posting: dict):
    """
    term_query_score = {key: term(str) | value: query_score(float)}
    """
    term_idf = construct_term_idf(positional_index)
    score = {}
    query_words = query.replace('"', "").split()
    sum_ = 0
    for index in range(len(query_words)):
        query_words[index] = Stemmer().stem(query_words[index])
    for term in term_posting:
        score[term] = (1 + log(query_words.count(term))) * term_idf[term]
        sum_ += pow(score[term], 2)

    normalized_factor = 1 / sqrt(sum_)
    for term in term_posting:
        score[term] *= normalized_factor
    return score


def search_positives_words(positive_words: list):
    term_posting = {}
    for word in positive_words:
        word = Stemmer().stem(word)
        if word not in positional_index:
            print("No result for given query, because of this word: " + word)
            exit()
        else:
            term_posting[word] = positional_index[word]
    return term_posting


def search_negative_words(negative_words: list):
    term_posting = {}
    for word in negative_words:
        word = Stemmer().stem(word)
        if word in positional_index:
            term_posting[word] = positional_index[word]
    return term_posting


def answer_query(words: tuple):
    term_posting = search_positives_words(words[0])
    negative_term_posting = search_negative_words(words[1])
    for term in negative_term_posting:
        if term in term_posting:
            term_posting.pop(term)
    return term_posting.copy()


urls = []
url_title = {}
url_content = {}
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

docs_term_score = construct_document_term_score_for_document()

query = "تحریم های آمریکا علیه ایران و ایران"
term_query_score = construct_term_query_score(answer_query(get_query(query)))

similarity_doc = {}
similar = []
for document_ in docs_term_score:
    for term_ in term_query_score:
        if term_ not in docs_term_score[document_]:
            similarity_doc[document_] = 0
            break
        similar.append(docs_term_score[document_][term_] * term_query_score[term_])
    similarity_doc[document_] = sum(similar)
    similar.clear()

similarity_array = []
for index in range(len(similarity_doc)):
    if index not in similarity_doc:
        similarity_array.append(0)
    else:
        similarity_array.append(similarity_doc[index])

sorted_array = sorted(similarity_array, reverse=True)

for index in range(len(sorted_array)):
    if index > 5:
        break
    if sorted_array[index] == 0:
        break
    print("***\nResult " + str(index))
    doc_id = similarity_array.index(sorted_array[index])
    print("Document ID: " + str(doc_id))
    print("URL: " + str(urls[doc_id]))
    print("Title: " + str(url_title[urls[doc_id]]))
