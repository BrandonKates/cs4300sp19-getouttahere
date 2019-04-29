import json
import pickle
import os

from nltk.corpus import stopwords 
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from tqdm import tqdm

from pathlib import Path

def load_data(path):
	print("Reading from %s" % os.path.join(path,'largecity_data.json'))

	data_file = os.path.join(path, 'largecity_data.json')
	data_dict = dict()
	with open(data_file, 'r') as data:
			data_dict = json.load(data)
	return data_dicts

def load_reviews(path):
	print("Reading from %s" % os.path.join(path,'reviews.json'))
	with open(os.path.join(path,'reviews.json'), 'r') as data:
		return json.load(data)

def generate_reviews(data):
	all_reviews = []
	for d_name, destination in data.items():
	    attractions = destination['attractions']
	    for a_name, attraction in attractions.items():
	        if attraction is not None:
	            r_1 = attraction['reviews']
	            if r_1 is not None:
	                if 'result' in r_1.keys():
	                    r_2 = r_1['result']
	                    if len(r_2) > 0:
	                        if 'rating' in r_2.keys() and 'reviews' in r_2.keys():
	                            avg_rating = r_2['rating']
	                            reviews = r_2['reviews']
	                            for review in reviews:
	                                this_review = dict()
	                                this_review['destination'] = d_name
	                                this_review['attraction'] = a_name
	                                this_review['avg_rating'] = avg_rating
	                                this_review['stars'] = review['rating']
	                                this_review['text'] = review['text']
	                                this_review['place_id'] = attraction['place_id']
	                                this_review['type'] = attraction['type']
	                                this_review['description'] = attraction['description']
	                                all_reviews.append(this_review)
	return all_reviews

def preprocess_reviews(reviews):
	stop_words = set(stopwords.words('english'))
	ps = PorterStemmer()
	tokenizer = RegexpTokenizer("\w+")
	for review in reviews:
	    tokens = tokenizer.tokenize(review['text'].lower())
	    filtered_text = ""
	    for w in tokens:
	        if w not in stop_words:
	            filtered_text += " " + ps.stem(w)
	    review['text'] = filtered_text.strip()
	    review['description'] = [ps.stem(w) for w in review['description']]

	with open("reviews.json", "w") as f:
		f.write(json.dumps(reviews))
	return reviews

def generate_destination_corpus(reviews):
	dest_dict = dict()
	for review in reviews:
	    dest = review['destination']
	    attraction = review['attraction']
	    text = review['text']
	    description = " ".join(review['description'])
	    all_text = text + description
	    if dest not in dest_dict:
	        dest_dict[dest] = ''
	    dest_dict[dest] += all_text
	corpus = []
	y = []
	for dest in dest_dict:
	    corpus.append(dest_dict[dest])
	    y.append(dest)
	return corpus, y

def generate_attraction_corpus(reviews):
	dest_dict = dict()
	for review in reviews:
	    dest = review['destination']
	    attraction = review['attraction']
	    text = review['text']
	    description = " ".join(review['description'])
	    label = (dest, attraction)
	    if label not in dest_dict:
	        dest_dict[label] = description
	    dest_dict[label] += " " + text
	corpus = []
	y = []
	for label in dest_dict:
	    corpus.append(dest_dict[label])
	    y.append(label)
	return corpus, y

def tfidf(corpus):
	vectorizer = TfidfVectorizer(
		ngram_range= (1,2), 
		strip_accents = 'unicode', 
		analyzer = 'word', 
		min_df = 0.05)
	X = vectorizer.fit_transform(corpus)
	return vectorizer, X

def kmeans(X, y, k):
	neighborClassifier = KNeighborsClassifier(n_neighbors = k)
	neighborClassifier.fit(X, y)
	def predict(index):
		return neighborClassifier.kneighbors(X[index], k)
	return predict


def run_all_kmeans(X, y, k):
	predictor = kmeans(X, y, k)
	n, d = X.shape
	all_nearest_neighbors = dict()
	for i in tqdm(range(n)):
		distance, neighbors = predictor(i)
		neighbors = neighbors[0]
		all_nearest_neighbors[y[i]] = [y[int(neighbor)] for neighbor in neighbors[1:]]
	return all_nearest_neighbors

def main():
	base_path = Path(__file__).parent
	data_files = (base_path / "../../static/data").resolve()
	try:
		reviews = load_reviews(data_files)
	except:
		reviews = preprocess_reviews(generate_reviews(load_data(data_files)))

	destination_corpus, y_dest = generate_destination_corpus(reviews)
	attraction_corpus, y_att = generate_attraction_corpus(reviews)

	dest_vec, X_dest = tfidf(destination_corpus)
	att_vec, X_att = tfidf(attraction_corpus)

	kmeans_dest = run_all_kmeans(X_dest, y_dest, 6)
	kmeans_att = run_all_kmeans(X_att, y_att, 6)

	print("Writing to %s" % os.path.join(data_files, "kmeans_dest.pickle"))
	pickle.dump(kmeans_dest, open(os.path.join(data_files, "kmeans_dest.pickle"), 'wb'))
	print("Writing to %s" % os.path.join(data_files, "kmeans_att.pickle"))
	pickle.dump(kmeans_att, open(os.path.join(data_files, "kmeans_att.pickle"), 'wb'))

if __name__ == "__main__":
	main()



