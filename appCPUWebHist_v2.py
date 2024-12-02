# Help resources
# https://www.youtube.com/watch?v=BomCx0jbwPY
# https://www.youtube.com/watch?v=VKg1Dnz7GN0
# https://www.hackster.io/mjrobot/from-data-to-graph-a-web-journey-with-flask-and-sqlite-4dba35
# https://toorshia.github.io/justgage/

# https://towardsdatascience.com/python-webserver-with-flask-and-raspberry-pi-398423cc6f5d
# https://www.hackster.io/mjrobot/from-data-to-graph-a-web-journey-with-flask-and-sqlite-4dba35

# location: C:\Users\user\Desktop\Project_DataAnalytics\Sensors_Database\cpuWebHist_V2
#----------------------------------------------------------------------------
# Created By  : Nandkishor Motiram Dhawale
# Created Date: 20241128
# Last Modification Date: 20241128
# version ='1.0'
# ---------------------------------------------------------------------------
"""Module documentation goes here
   This is an programm to querry  recorded data from a table in SQLite and post it on the web browser running on a local server
   including graphs/charts formats. 
"""

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)
import sqlite3
import time
from datetime import datetime
conn=sqlite3.connect(r'C:\Users\nmdha\hello\sensorsData.db')
curs=conn.cursor()

# Retrieve LAST data from database
def getLastData():
	conn=sqlite3.connect(r'C:\Users\nmdha\hello\sensorsData.db')
	curs=conn.cursor()
	for row in curs.execute("SELECT * FROM CPU_data ORDER BY timestamp DESC LIMIT 1"):
		time = str(row[0])
		cpu_percent = row[1]
		cpu_count = row[2]
	#conn.close()
	return time, cpu_percent, cpu_count

# Get 'x' samples of historical data
def getHistData (numSamples):
	conn=sqlite3.connect(r'C:\Users\nmdha\hello\sensorsData.db')
	curs=conn.cursor()
	curs.execute("SELECT * FROM CPU_data ORDER BY timestamp DESC LIMIT "+str(numSamples))
	data = curs.fetchall()
	time = []
	cpu_percent = []
	cpu_count = []
	for row in reversed(data):
		time.append(row[0])
		cpu_percent.append(row[1])
		cpu_count.append(row[2])
		cpu_percent, cpu_count = testeData(cpu_percent, cpu_count)
	return time, cpu_percent, cpu_count

# Test data for cleanning possible "out of range" values
def testeData(cpu_percent, cpu_count):
	n = len(cpu_percent)
	for i in range(0, n-1):
		if (cpu_percent[i] < 0 or cpu_percent[i] >100):
			cpu_percent[i] = cpu_percent[i-2]
		if (cpu_count[i] < 0 or cpu_count[i] >8):
			cpu_count[i] = cpu_count[i-2]
	return cpu_percent, cpu_count


# Get Max number of rows (table size)
def maxRowsTable():
	conn=sqlite3.connect(r'C:\Users\nmdha\hello\sensorsData.db')
	curs=conn.cursor()
	for row in curs.execute("select COUNT(cpu_percent) from  CPU_data"):
		maxNumberRows=row[0]
	return maxNumberRows

# Get sample frequency in minutes
def freqSample():
	time, cpu_count, cpu_count = getHistData (2)
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp0 = datetime.strptime(time[0], fmt)
	tstamp1 = datetime.strptime(time[1], fmt)
	freq = tstamp1-tstamp0
	freq = int(round(freq.total_seconds()//60))
	return (freq)

# define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
        numSamples = 100

global freqSamples
freqSamples = freqSample()

global rangeTime
rangeTime = 100
				
		
# main route 
@app.route("/")
def index():
	time, cpu_percent, cpu_count = getLastData()
	templateData = {
	  'time'		: time,
      'cpu_percent'		: cpu_percent,
      'cpu_count'			: cpu_count,
      'freq'		: freqSamples,
      'rangeTime'		: rangeTime
	}
	return render_template('index.html', **templateData)


@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples 
    global freqSamples
    global rangeTime
    rangeTime = int (request.form['rangeTime'])
    if (rangeTime < freqSamples):
        rangeTime = freqSamples + 1
    numSamples = rangeTime//freqSamples
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    
    time, cpu_percent, cpu_count = getLastData()
    
    templateData = {
	  'time'		: time,
      'cpu_percent'		: cpu_percent,
      'cpu_count'			: cpu_count,
      'freq'		: freqSamples,
      'rangeTime'	: rangeTime
	}
    return render_template('index.html', **templateData)
	
	
@app.route('/plot/cpu_percent')
def plot_cpu_percent():
	time, cpu_percent, cpu_count = getHistData(numSamples)
	ys = cpu_percent
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("CPU PERCENTAGE [%]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(int(numSamples))
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/cpu_count')
def plot_cpu_count():
	time, cpu_percent, cpu_count = getHistData(numSamples)
	ys = cpu_count
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("CPU COUNT []")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(int(numSamples))
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=150, debug=False)