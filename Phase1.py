import pickle
import time

import pandas as pd
from hazm import *


def read_data():
    df = pd.read_json(path_or_buf='IR_data_news_12k.json', orient='index')
    for index, row in df.iterrows():
        urls.append(row['url'])
        url_title[row['url']] = row['title']
        url_content[row['url']] = row['content']
        # if index > 2000:
        #     break


def pre_processing():
    start_time = time.time()
    tokenized_dict = {}
    stopwords = stopwords_list()
    stopwords.append("(")
    stopwords.append(" ")
    stopwords.append(".")
    stopwords.append(")")
    stopwords.append("پیام/")
    stopwords.append("انتها")
    stopwords.append("انت")
    stopwords.append("\\")
    stopwords.append("،")
    stopwords.append("فارس")
    stopwords.append("گزارش")
    stopwords.append("خبرگزاری")
    stemmed_text = []
    for url in url_content:
        tokenized_dict[url] = word_tokenize((Normalizer().normalize(url_content[url])))
        for word in tokenized_dict[url]:
            if word not in stopwords:
                stemmed_text.append(Stemmer().stem(word))
        tokenized_dict[url] = stemmed_text.copy()
        stemmed_text.clear()
    print("Time spent for pre processing: " + str(time.time() - start_time))
    return tokenized_dict


def construct_positional_index(url_tokenized_text):
    """
    term_posting = {key: term(str) | value: posting(dict)}
    posting = {key: doc_id(int) | value: positions(set)}
    positions = set of int
    """
    start_time = time.time()
    term_posting = {}
    for url in url_tokenized_text:
        string = url_tokenized_text[url]
        for position, word in enumerate(string):
            doc_id = urls.index(url)
            if word in term_posting:
                if doc_id not in term_posting[word]:
                    term_posting[word][doc_id] = {position}
                else:
                    positions = set(term_posting[word][doc_id])
                    positions.add(position)
                    term_posting[word][doc_id] = positions
            elif word not in term_posting:
                term_posting[word] = {doc_id: {position}}
    print("Time spent for constructing positional index: " + str(time.time() - start_time))
    return term_posting


def get_query():
    # query = input("Write Query:\n")
    query = "تحریم های آمریکا علیه ایران"
    query = query.replace('"', "").split()
    negative_words = []
    positive_words = []
    for word in query:
        if "!" in word:
            negative_words.append(word.replace("!", ""))
        else:
            positive_words.append(word)
    return positive_words, negative_words


def search_positives_words(positive_words: list):
    term_posting = {}
    for word in positive_words:
        word = Stemmer().stem(word)
        if word not in positional_index:
            print("No result for given query, because of this word: " + word)
            return None
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


def rank_result(term_postings: dict):
    accepted_doc = set()
    doc_id_with_number_of_term = []
    # collect all documents
    for word in term_postings:
        doc_ids = set()
        for doc_id in term_postings[word].keys():
            doc_ids.add(doc_id)
        accepted_doc = accepted_doc.union(doc_ids)
    # filter all documents having words of the query
    for word in term_postings:
        accepted_doc = accepted_doc.intersection(set(term_postings[word].keys())).copy()

    for document in accepted_doc:
        number_of_term = 0
        for term in term_postings:
            number_of_term += len(term_postings[term][document])
        doc_id_with_number_of_term.append((document, number_of_term))
    doc_id_with_number_of_term.sort(key=lambda i: i[1], reverse=True)
    return doc_id_with_number_of_term


def answer_query(words: tuple):
    term_posting = search_positives_words(words[0])
    negative_term_posting = search_negative_words(words[1])
    for term in negative_term_posting:
        if term in term_posting:
            term_posting.pop(term)
    return rank_result(term_posting.copy())


def show_ranked_documents(ranked_docs: list):
    for counter, tuple_ in enumerate(ranked_docs):
        if counter > 4:
            break
        doc_id = tuple_[0]
        print("***\nResult " + str(counter + 1))
        print("Document ID: " + str(doc_id))
        print("URL: " + str(urls[doc_id]))
        print("Title: " + str(url_title[urls[doc_id]]))
        # print("Content:" + url_content[urls[doc_id]])


urls = []
url_title = {}
url_content = {}
read_data()
# url_token_content = pre_processing()
# positional_index = construct_positional_index(url_token_content)
"""
For saving and writing file of positional index dictionary:
# pos_index_file = open("data.pkl", "wb")
# pickle.dump(positional_index, pos_index_file)
# pos_index_file.close()
"""
"""
For opening and reading file of positional index dictionary:
# pos_index_file = open("data.pkl", "rb")
# positional_index = pickle.load(pos_index_file)
# pos_index_file.close()
*** IMPORTANT NOTE: after that comment:"pre_processing()", "construct_positional_index(url_token_content)"
"""
pos_index_file = open("data.pkl", "rb")
positional_index = pickle.load(pos_index_file)
pos_index_file.close()
show_ranked_documents(answer_query(get_query()))
