from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import numpy as np
import os 
import requests
import re

dirpath = os.getcwd()
data_files = dirpath + "/app/static/data/"
tfidf_files = data_files + "tfidf_data/"
inv_idx = np.load(tfidf_files+"inv_idx.npy").item()
idf = np.load(tfidf_files+"idf_dict.npy").item()
doc_norms = np.load(tfidf_files+"doc_norms.npy").item()
json_data = data_files + "data_jsons/"
urban_rural = np.load(data_files+"urban_cities.npy").item()
# Mapping of cities to their countries
climate = np.load(data_files+"city_climates.npy").item()
ps = PorterStemmer()

project_name = "Kanoe"
net_id = """Alex Styler (ams698), Brandon Kates (bjk224), David Marchena (dpm247),
	Noam Eshed (ne236), Sofia Nieves (sn529)"""

@irsystem.route('/', methods=['GET','POST'])
def search():
	query = request.args.get('search')
	
	if query == None:
		query = ""
	price = request.args.get('price')
	if price == None:
		price = ""
	purpose = request.args.get('purpose')
	if purpose == None:
		purpose = ""
	climate = request.args.get('climate')
	if climate == None:
		climate = ""
	urban = request.args.get('urban')
	if urban == None:
		urban = 1
	urban = int(urban)
	numLocs = request.args.get('numberLocs')
	if numLocs == None or numLocs == '':
		numLocs = 4
	numLocs = int(numLocs)
	
	# Stem query words:
	stem_query = ''
	stem_dict = {}
	
	for term in query.lower().replace(',',' ').split():
		s = ps.stem(term)
		stem_query += str(s + " ")
		stem_dict[s] = term
		
	# What % of the score to deduct for not meeting certain input specs
	urban_weight = 0.2
	climate_weight = 0.5
	
	if len(np.unique(stem_query.split(" "))) == 1:
		data = []
		output_message = ""
	else:
		results = index_search(stem_query, inv_idx, idf, doc_norms)
		print(len(results))
		output_message= ""

		if len(results) == 0:
			output_message = "No Results Found"
		data = []
		for i, (city, score) in enumerate(results):
			# Decrease score if not rural/urban as user specified
			if (urban==0 and is_urban(city)==1) or (urban==2 and is_urban(city)==0):
				score *= (1-urban_weight)
				
			# Decrease score if incorrect climate
			if climate != "" and climate != get_climate(city) and get_climate(city) is not None:
				score *= (1-climate_weight)
				
			results[i] = (city, score)
			
		for city, score in results:
			#city_dict = {}
			data_dict = {}

			# Get attraction information
			city_info = organize_city_info(city, json_data, stem_query, stem_dict, 3, price, purpose)
			city_info['city'] = city
			city_info['score'] = score
			
			data.append(city_info)
			numLocs -= 1
			if numLocs == 0:
				break

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
	with open(folder+str(city) + '.json', 'r') as f:
		data = json.load(f)
		return data[city]
		
def attraction_score(query, desc):
	score = 0
	stemmed_desc = []
	for term in desc:
		stemmed_desc.append(ps.stem(term))

	if len(stemmed_desc) == 0:
		return 0
	for q in query.lower().split():
		for d in stemmed_desc:
			if (q in d) or (d in q):
				score += 1
	score /= len(stemmed_desc)
	return score
	
def organize_city_info(city, folder, query, stemmer, num_attrs, price, purpose):
	data = get_city_info(city, folder)

	num_atts_flag = False
	if int(data['size']) < num_attrs:
		num_attrs = data['size']
		num_atts_flag = True
	output_dict = {}
	output_dict['country'] = data['country']
	if output_dict['country'] != output_dict['country']:	#check if nan
		output_dict['country'] = '(Country Unknown)'
		
	output_dict['attractions'] = []
	
	attractions = data['attractions']
	attrac_scores = []
	for key, value in attractions.items():
		if value is not None:
		
			# Skip attractions out of price range
			a_cost = attractions[key]['cost']
			if price != "" and price != a_cost:
				continue
				
			# Skip if incorrect trip purpose
			a_purpose = attractions[key]['purpose']
			if purpose != "" and purpose != a_purpose:
				continue
				
			attractions[key]['name'] = key
			score = attraction_score(query, value['description'])
			attrac_scores.append((key, score))
	
	# Add attractions with no cost if we don't have enough
	if len(attrac_scores) < num_attrs:
		for key, value in attractions.items():
			if value is not None and key not in [i[0] for i in attrac_scores]:
				if price != "" or purpose != "":
					if attractions[key]['cost'] == "" or attractions[key]['purpose'] == "":
						attractions[key]['name'] = key
						score = attraction_score(query, value['description'])
						attrac_scores.append((key, score))
				else:
					attractions[key]['name']=key
					score = attraction_score(query, value['description'])
					attrac_scores.append((key, score))

	# Sort by decreasing score
	sorted_scores = sorted(attrac_scores, key=lambda x: x[1], reverse=True)
	for i in range(num_attrs):
		(name, score) = sorted_scores[i]
		# Find all matching terms b/w query and description
		desc = attractions[name]['description']
		matches = get_matching_terms(query, desc, stemmer)
		attractions[name]['matches'] = matches
		#attractions[name]['matches'] = (desc, matches)
		output_dict['attractions'].append(attractions[name])
	
	api_key = "AIzaSyCJiRPAPsSLaY46PvyNxzISQMXFZx6h-g8"
	for att in range(len(output_dict['attractions'])):
		place_id = output_dict['attractions'][att]['place_id']
		if place_id is not None and place_id != 'not found':
			#reviews = [{'reviews':["Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."]}]
			reviews = get_reviews(place_id, api_key).get('result')
			output_dict['attractions'][att]['reviews'] = reviews
			
	return output_dict

def get_matching_terms(query, desc, stemmer):
	matches_dict = {}
	
	stemmed_desc = []
	for term in desc:
		stemmed_desc.append(ps.stem(term))
	
	for q in query.lower().split():
		for d in stemmed_desc:
			if (q in d) or (d in q):
				full = stemmer[q]
				if full not in matches_dict:
					matches_dict[full] = 0
				matches_dict[full] += 1
	# Make into tuple list to sort
	matches_scores_list = [(key, matches_dict[key]) for key in matches_dict]
	sorted_tuples = sorted(matches_scores_list, key=lambda x:x[1], reverse=True)

	return [x[0] for x in sorted_tuples]
	
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