from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import numpy as np
import os 

dirpath = os.getcwd()
tfidf_files = dirpath + "/app/irsystem/controllers/tfidf_data/"

project_name = "Kanoe: Travel Destination Wizard"
net_id = "ams698, bjk224, dpm247, ne236, sn529"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	advanced_query = request.args.get('price')
	print(advanced_query)
	if not query:
		data = []
		output_message = ''
	else:
        # Read in pre-computed tf-idf and data tables
		with np.load(tfidf_files+"tfidf_matrix.npz") as tf_idf:
			tf_idf = tf_idf['arr_0']
			vocab = np.load(tfidf_files+"tfidf_vocab.npy").item()
			cities = np.load(tfidf_files+"city_names.npy")
			
			query_vec = vectorize_query(query, vocab)
			
			if query_vec is None:
				output_message = "Your search did not return any results. Please try a new query."
				data = []
			else:
				scores = cos_sim(query_vec, tf_idf)
				idx =  np.argmax(scores)
				data = [cities[idx]]
				output_message = "Your search: " + query
			
			#data = range(5)
			#output_message = ''

	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

def vectorize_query(q, vocab):
    q_vec = np.zeros(len(vocab))
    for term in q.split(" "):
        index = vocab.get(term)
        if index is not None:
            q_vec[index] += 1
    
    if sum(q_vec) == 0:
        return None
    
    q_vec /= sum(q_vec)
    return q_vec

def cos_sim(q, docs):
    return np.dot(q.T, docs.T)
    