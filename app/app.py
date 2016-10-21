from flask import Flask, flash
#from app import app
from flask import render_template
import urllib2
import json
import datetime
import os
from dateutil.parser import parse
from .forms import ReservationForm

app = Flask(__name__)
app.config.from_pyfile('config.py')

reservation_service_url = 'http://172.18.0.2:2080'
num_days = 14
@app.route('/test', methods=['GET'])
def test():
	return render_template('test.html',
                           title='Home')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	form = ReservationForm()
	#POST form for new reservation
	if form.validate_on_submit():
		res_request = urllib2.Request('%s/item/%s/reservation' % (reservation_service_url, form.server_name.data))
                res_request.add_header('Content-Type', 'application/json')
	        print res_request
		date_cmd = 'date -d ' + form.start_date.data
		date_cmd = date_cmd + ' +%Y-%m-%dT%H:%M:%S.%m%:z'
		f = os.popen(date_cmd)
		post_start_date = f.read().rstrip()
		
		date_cmd = 'date -d ' + form.end_date.data
		date_cmd = date_cmd + ' +%Y-%m-%dT%H:%M:%S.%m%:z'
		f = os.popen(date_cmd)
		post_end_date = f.read().rstrip()
		print post_start_date
		print post_end_date

		request_data = {"username": form.user_name.data,"begin": post_start_date,"end": post_end_date, "approved": True} 
               
		#POST request to reservation service, on error redirect to error page 
		try:
			response = urllib2.urlopen(res_request, json.dumps(request_data))
		except urllib2.URLError as e:
			return render_template('error.html',
				title='Error',
				error_reason=e.reason,
				error_msg=e.read())

	#Generate table in UI
    	response = urllib2.urlopen('%s/items' % (reservation_service_url))
	data = json.load(response)
	
	#get current date for start of time range
	today = datetime.date.today()
	
	#create dictionary covering date range
	tabledata = {'date':[today.strftime('%m-%d-%Y')],'servers':{}}
	for i in range(1,num_days):
		delta_days = datetime.timedelta(days=i)
		curday = today + delta_days
		tabledata['date'].append(curday.strftime('%m-%d-%Y')) 

	#convert reservation service response date to dictionary of lists	 
	#for eeach server, determine if it has a reservation and add the username of teh reservation in the table date, otherwise mark as Free
	for item in data:
		tabledata['servers'][item] = []
		if 'reservations' in data[item]:
			username = data[item]['reservations'][0]['username']
			res_start_date = parse(data[item]['reservations'][0]['begin'])
			res_end_date = parse(data[item]['reservations'][0]['end'])
			
			time_start_date = datetime.datetime.strptime(res_start_date.strftime('%m-%d-%Y'), '%m-%d-%Y')
			time_end_date = datetime.datetime.strptime(res_end_date.strftime('%m-%d-%Y'), '%m-%d-%Y')
			for date in tabledata['date']:
				test_date = datetime.datetime.strptime(str(date), '%m-%d-%Y')
				if (time_start_date <= test_date <= time_end_date):
					tabledata['servers'][item].append(username)
				else:
					tabledata['servers'][item].append('Free')
		else:
			for d in range(num_days):
				tabledata['servers'][item].append('Free')
	return render_template('index.html',
                           title='Home',
			   servers=data,
			   tabledata=tabledata,
			   form = form)
#if __name__ == '__main__':
#    app.run(debug=True,host='0.0.0.0')
