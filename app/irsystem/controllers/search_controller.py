from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Kanoe"
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
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

