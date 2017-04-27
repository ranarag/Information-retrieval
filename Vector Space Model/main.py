import os
import fileinput
from collections import defaultdict
import collections
from math import log, sqrt
import operator
import numpy as np
import readAssessment
import ProcDoc
import Expansion
import timeit

data = {}				# content of document (doc, content)
query = {}				# query
doc_freq ={}

document_path = "../Corpus/SPLIT_DOC_WDID_NEW"
query_path = "../Corpus/QUERY_WDID_NEW"

# document model
data = ProcDoc.read_file(document_path)
doc_wordcount = ProcDoc.doc_preprocess(data)
total_docs = len(doc_wordcount.keys()) * 1.0
[doc_model, doc_freq] = ProcDoc.compute_TFIDF(doc_wordcount)

# query model
query = ProcDoc.read_file(query_path)
query = ProcDoc.query_preprocess(query)
query_wordcount = {}

for q_key, q_content in query.items():
	query_wordcount[q_key] = ProcDoc.word_count(q_content, {})

query_model = defaultdict(dict)	
for q_key, word_count_dict in query_wordcount.items():
	max_freq = np.max(np.array(word_count_dict.values()), axis = 0)
	for word, count in word_count_dict.items():
		if word in doc_freq:
			idf = log(1 + total_docs / doc_freq[word])
			
		else:
			idf = log(1 + total_docs)
			
		query_model[q_key][word] = (1 + log(count)) * idf	

# query process
print "query ..."
start = timeit.default_timer()
assessment = readAssessment.get_assessment()
feedback_model = []
feedback_ranking_list = []
doc_length = {}

for step in range(1):
	query_docs_point_dict = {}
	AP = 0
	mAP = 0
	for q_key, q_words_count_list in query_model.items():
		docs_point = defaultdict(int)
		for doc_key, doc_words_count_dict in doc_model.items():
			relevant_point = 0
			query_length = 1
			
			# calculate each query value for the document
			for doc_word, doc_word_count in doc_words_count_dict.items():
				if not doc_word in q_words_count_list:
					continue
				else:	
					relevant_point += q_words_count_list[doc_word] * doc_word_count
				
			if not doc_key in doc_length:
				doc_length[doc_key] = sqrt((np.array(doc_words_count_dict.values()) ** 2).sum(axis = 0))
				
			# cosine measure
			relevant_point /= (query_length * doc_length[doc_key])
			docs_point[doc_key] = relevant_point
		# sorted each doc of query by point
		docs_point_list = sorted(docs_point.items(), key=operator.itemgetter(1), reverse = True)
		query_docs_point_dict[q_key] = docs_point_list
	# mean average precision	
	mAP = readAssessment.mean_average_precision(query_docs_point_dict, assessment)
	print "mAP:", mAP
	print "feedback:", step
	
	if step < 1:
		feedback_ranking_list = dict(query_docs_point_dict)
	[query_model, feedback_model] = Expansion.extQueryModel(query_model, feedback_ranking_list, doc_model, feedback_model, step + 1)
stop = timeit.default_timer()
print "Result : ", stop - start	