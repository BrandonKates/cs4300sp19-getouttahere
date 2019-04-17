from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from nltk.tokenize import RegexpTokenizer
import numpy as np
import os 


dirpath = os.getcwd()
tfidf_files = dirpath + "/app/irsystem/controllers/tfidf_data/"
inv_idx = np.load(tfidf_files+"inv_idx.npy").item()
idf = np.load(tfidf_files+"idf_dict.npy").item()
doc_norms = np.load(tfidf_files+"doc_norms.npy").item()
		
# Mapping of cities to their countries
city_country_dict = np.load(tfidf_files+"city_country_dict.npy").item()
		
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
		
		results = index_search(advanced_query, inv_idx, idf, doc_norms)
		data = []
		count = 0
		for city, score in results[0:5]:
			count += 1
			country = city_country_dict[city]
			if str(country) == 'nan':
				country = ' (Country Unknown)'
			else:
				country = ",  " + country
			data.append(str(count) + ") " + city + str(country))
		
		output_message= "You searched for places with " + advanced_query

	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

def index_search(query, index, idf, doc_norms):
    """ Search the collection of documents for the given query
    Arguments
    =========
    query: string, the query we are looking for.
    index: an inverted index 
    idf: idf values 
    doc_norms: document norms
        
    Returns
    =======
    results, list of tuples (score, doc_id)
        Sorted list of results such that the first element has
        the highest score, and `doc_id` points to the document
        with the highest score.
    
    Note: 
        
    """
    # Initialize output dictionary, keys = cities, vals = scores
    scores_array = {}
    
    # Tokenize the query
    tokenizer = RegexpTokenizer(r"\w+")
    tokens = tokenizer.tokenize(query.lower())
    
    # Calculate tf of query
    q_tf = {}
    for t in tokens:
        if t not in q_tf.keys():
            q_tf[t] = 0
        q_tf[t] += 1
        
    # Calculate tf-idf vector of query
    q_tf_idf = []
    for k in q_tf.keys():
        if k in idf:
            q_tf_idf.append(q_tf[k]*idf[k])
        
    q_norm = np.sqrt(np.sum(np.square(q_tf_idf)))

    # Update the score once per token
    for t in tokens:
        # Skip if there are no docs containing the token
        if t not in index.keys():
            continue
        # Otherwise add the cossim score to output
        for (city, d_tf) in index[t]:
            if city not in scores_array:
                scores_array[city] = 0
            scores_array[city] += q_tf[t]*idf[t]*d_tf*idf[t]
        
    # Normalize
    for key in scores_array.keys():
        scores_array[key] /= doc_norms[key]*q_norm+1

    # Put in output form as list (city, score)
    output_results = []
    for key in scores_array.keys():
        output_results.append((key, scores_array[key]))
    output_results.sort(key = lambda t: t[1], reverse=True)

    return output_results
