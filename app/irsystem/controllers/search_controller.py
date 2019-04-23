from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from nltk.tokenize import RegexpTokenizer
import numpy as np
import os 
import requests

dirpath = os.getcwd()
data_files = dirpath + "/app/static/data/"
tfidf_files = data_files + "tfidf_data/"
inv_idx = np.load(tfidf_files+"inv_idx_largecities.npy").item()
idf = np.load(tfidf_files+"idf_dict_largecities.npy").item()
doc_norms = np.load(tfidf_files+"doc_norms_largecities.npy").item()
json_data = data_files + "data_jsons/"
urban_rural = np.load(data_files+"urban_cities.npy").item()
# Mapping of cities to their countries
city_country_dict = np.load(tfidf_files+"city_country_dict.npy").item()
climate = np.load(data_files+"city_climates.npy").item()
	
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
	urban = request.args.get('urban')
	if urban == None:
		print("here")
		urban = 1
	urban = int(urban)
	numLocs = request.args.get('numberLocs')
	if numLocs == None or numLocs == '':
		numLocs = 4
	numLocs = int(numLocs)
	
	advanced_query = query + " " + price + " " + group + " " + climate + " " + activities

	if not advanced_query:
		data = []
		output_message = ''
	else:
		results = index_search(advanced_query, inv_idx, idf, doc_norms)
		data = []
		count = 0
		for city, score in results:
			# Skip if not rural/urban as user specified
			if (urban==0 and is_urban(city)==1) or (urban==2 and is_urban(city)==0):
				continue
			# Skip if incorrect climate
			if climate != "" and climate != get_climate(city) and get_climate(city) is not None:
				continue
			count = count + 1
			#city_dict = {}
			data_dict = {}
			
			# Get country data
			country = str(city_country_dict.get(city))
			if str(country) == 'nan' or str(country) == "None":
				country = ' (Country Unknown)'
			else:
				country = ",  " + country
			data_dict['country'] = country
			
			# Get attraction information
			city_info = organize_city_info(city, json_data, advanced_query, 3)
			city_info['country'] = country
			city_info['city'] = city
			city_info['score'] = score
			
			data.append(city_info)
			numLocs -= 1
			if numLocs == 0:
				break
		output_message= "You searched for places with " + advanced_query

	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

def get_climate(city):
	if city in climate.keys():
		return climate[city]
	else:
		return None
		
def is_urban(city):
	
	urban = urban_rural.get(city)
	if urban is not None:
		return urban
	else:
		return 1
	
def get_city_info(city, folder):
	alphabet = ['A', 'B', 'C','D','E','F','G','H','I','J','K','L','M','N',
						'O','P','Q','R','S','T','U','V','W','X','Y','Z']
	firstletter = city[0]
	if firstletter <= alphabet[0]:
		filename = 'A.json'
	else:
		for i,letter in enumerate(alphabet[1:]):
			if firstletter > alphabet[i] and firstletter <= letter:
				filename = alphabet[i+1]+'.json'
	if firstletter > alphabet[-1]:
		filename='Z.json'
	#print(firstletter, filename)
	
	with open(folder+filename, 'r') as f:
		data = json.load(f)
		return data[city]
		
def attraction_score(query, desc):
	#print(query, '\n', desc)
	score = 1
	for term in desc:
		if term in query.lower():
			score += 1
	score /= len(desc) + 1
	return score
	
	
def organize_city_info(city, folder, query, num_attrs):
	data = get_city_info(city, folder)
	num_atts_flag = False
	if int(data['size']) < num_attrs:
		num_attrs = data['size']
		num_atts_flag = True
		
	output_dict = {}
	output_dict['attractions'] = []
	attractions = data['attractions']
	
	# Get attraction scores
	top_eat = ''
	top_eat_score = 0
	top_do = ''
	top_do_score = 0
	top_drink = ''
	top_drink_score = 0
	fill_in = ['', '', '']
	for key, value in attractions.items():
		if value is not None:
			score = attraction_score(query, value['description'])
			attractions[key]['score'] = score
			if value['type'] == 'see' or value['type'] == 'do':
				if score >= top_do_score:
					top_do_score = score
					top_do = key
			elif value['type'] == 'eat':
				if score >= top_eat_score:
					top_eat_score = score
					top_eat = key
			elif value['type'] == 'drink':
				if score >= top_drink_score:
					top_drink_score = score
					top_drink = key
			# choose 3 random attractions to fill in if no matches
			if fill_in[0] == '':
				fill_in[0] = key
			elif fill_in[1] == '':
				fill_in[1] = key
			else:
				fill_in[2] = key
			
	# If one of the top 3 attractions is empty, pick one at random

	if top_eat == '':
		top_eat = fill_in[0]
	if top_do == '':
		top_do = fill_in[1]
	if top_drink == '':
		top_drink = fill_in[2]
		
	# Append top eat, do, and drink to list
	attractions[top_eat]['name'] = top_eat
	attractions[top_do]['name'] = top_do
	attractions[top_drink]['name'] = top_drink

	output_dict['attractions'].append(attractions[top_eat])
	output_dict['attractions'].append(attractions[top_do])
	output_dict['attractions'].append(attractions[top_drink])
	
	api_key = "AIzaSyCJiRPAPsSLaY46PvyNxzISQMXFZx6h-g8"
	for att in range(len(output_dict['attractions'])):
		place_id = output_dict['attractions'][att]['place_id']
		if place_id is not None and place_id != 'not found':
			reviews = get_reviews(place_id, api_key).get('result')
			output_dict['attractions'][att]['reviews'] = reviews
			
	return output_dict
	
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
            # Fix this mysterious issue in the future
            #idf_t = idf[t]
            
            if idf.get(t) is not None:
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

def get_reviews(place_id, api_key):
	"""Gets reviews for a location based on its google place id"""
	reviews = requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid="+str(place_id)+"&language=en&fields=price_level,rating,review&key=" + api_key).json()
	return reviews
	
	
#zip.close()