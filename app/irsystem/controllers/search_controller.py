from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import numpy as np
import os 

dirpath = os.getcwd()
tfidf_files = dirpath + "/app/irsystem/controllers/tfidf_data/"

vocab = np.load(tfidf_files+"tfidf_vocab.npy").item()
city_country_dict = np.load(tfidf_files+"city_country_dict.npy").item()
cities = np.load(tfidf_files+"city_names.npy")
tf_idf = np.load(tfidf_files+"tfidf_matrix.npz")['arr_0']

project_name = "Kanoe"
net_id = "ams698, bjk224, dpm247, ne236, sn529"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if query == None:
		query = ""
	price = request.args.get('price')
	if price == None:
		price = ""
	group = request.args.get('group')
	if group == None:
		group = ""
	climate = request.args.get('climate')
	if climate == None:
		climate = ""
	activities = request.args.get('activities')
	if activities == None:
		activities = ""
	
	advanced_query = query + " " + price + " " + group + " " + climate + " " + activities
	
	if not advanced_query:
		data = []
		output_message = ''
	else:
        # Read in pre-computed tf-idf and data tables
		
		query_vec = vectorize_query(advanced_query, vocab)
		if query_vec is None:
			output_message = "Your search did not return any results. Please try a new query."
			data = []
		else:
			data = []
			scores = cos_sim(query_vec, tf_idf)
			idx =  np.argmax(scores)
			idxs = (np.argsort(-1*scores))[:5]
			best_cities = cities[idxs]
			for count, i in enumerate(idxs):
				country = city_country_dict[cities[i]]
				if str(country) == 'nan':
					country = ' (Country Unknown)'
				else:
					country = ",  " + country
				data.append(str(count+1) + ")  " + cities[i] + str(country))

			output_message= "Your search: " + advanced_query


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
    