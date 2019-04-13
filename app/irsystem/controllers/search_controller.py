from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Get Outta Here: Travel Destination Wizard"
net_id = "ams698, bjk224, dpm247, ne236, sn529"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	price = request.args.get('price')
	group = request.args.get('group')
	climate = request.args.get('climate')
	activities = request.args.get('activities')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + " "  + query + " " + price + " " + group + " " + climate + " " + activities
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



