import web
import time
import xlrd
from os import system
from colorpalette import *

# run:  python ./bin/app.py

def readfiles():
	global listApplications
	global listInterfaces
	global listServers
	listApplications = []
	listInterfaces = []
	listServers = []
	# read applications, interfaces and settings into dictionaries
	import string

	
	book = xlrd.open_workbook("bin/appoverview.xlsx")

	#read applications
	appsheet = book.sheet_by_name("Applications")
	applegend = [i.value for i in appsheet.row(0)]
	for rx in range(1, appsheet.nrows):
		rowx = appsheet.row(rx)
		if rowx[applegend.index('Name')].value != "":
			app = nApplication(rowx[applegend.index('ID')].value, 
				               rowx[applegend.index("Name")].value, 
				               rowx[applegend.index("Scope")].value, 
				               rowx[applegend.index("Layer")].value)
			listApplications.append(app)

	
	#read interfaces
	intsheet = book.sheet_by_name("Interfaces")
	intlegend = [i.value for i in intsheet.row(0)]
	for rx in range(1, intsheet.nrows):	
		rowx = intsheet.row(rx)
		if rowx[intlegend.index('SourceName')].value != "":
			interface = nInterface(rowx[intlegend.index('ID')].value, 
							   	   rowx[intlegend.index('SourceApp')].value, 
							   	   rowx[intlegend.index('SourceServer')].value,
							   	   rowx[intlegend.index('SourceName')].value, 
							   	   rowx[intlegend.index('TargetApp')].value,
							   	   rowx[intlegend.index('TargetServer')].value, 
							   	   rowx[intlegend.index('TargetName')].value, 
							       rowx[intlegend.index('Throughput Day')].value, 
							       rowx[intlegend.index('Type')].value, 
							       rowx[intlegend.index('BiDirectional')].value,
							       rowx[intlegend.index('Function')].value,							       
							       rowx[intlegend.index('Detail type')].value)
			if listInterfaces.count(interface) == 0:
				listInterfaces.append(interface)


	#read servers
	#added 20131004
	#ServerID	AppID	App name P	Hostname	Functie
	#def __init__(self, ID, AppID, function, hostname):
	sersheet = book.sheet_by_name("Servers")
	serlegend = [i.value for i in sersheet.row(0)]
	for rx in range(1, sersheet.nrows):
		rowx = sersheet.row(rx)
		if rowx[serlegend.index('App name')].value != "":
			server = nServer(rowx[serlegend.index('ServerID')].value, 
							 rowx[serlegend.index('AppID')].value,
							 rowx[serlegend.index('Functie')].value,
							 rowx[serlegend.index('Hostname')].value,
							 rowx[serlegend.index('App name')].value,
							 rowx[serlegend.index('Scope')].value)
			if listServers.count(server) == 0:
				listServers.append(server)
	
	
	return 1
	
def generatePosFile(nodecolor, edgecolor, edgewidth):
	global listApplications
	global listInterfaces
	#applications and interfaces should be present
	#generates .pos file with timestamp, returns filename
	
	findBiDirectionalEdges()

	timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
	#print("Timestamp generated: " + timestamp)
	
	posfilestring = 'digraph G {\nsize="15,100"\noverlap=false;\nfontname="Myriad Condensed Web";\nsplines=true;\nedge [fontname="Myriad Condensed Web", fontsize=8];\nnode [shape=box, color=skyblue, fontname="Myriad Condensed Web", arrowsize=0.8, fontsize=10];\n'
	posfilestring = posfilestring + "{\nnode [shape=plaintext, fontsize=10];\nSource -> ETL -> Datawarehouse -> Application -> Presentation;\n}\n"
	
	for app in listApplications:
		if app.scope == "Yes":
			posfilestring = posfilestring + '"' + app.name + '"' + '[URL = "http://localhost:8080/?focusapp=' + str(app.ID) + '"];\n'
		else:
			posfilestring = posfilestring + '"' + app.name + '"' + '[style = filled, color="'+ colp(8) +'"];\n'
	posfilestring = posfilestring + "\n"
	
	layers = ["Source", "ETL", "Datawarehouse", "Application", "Presentation"]
	
	
	for layer in layers:
		posfilestring = posfilestring + "{ rank=same; " + layer + '; '
		for app in listApplications:
			#print app.layer
			if app.layer == layer:
				posfilestring = posfilestring + ' "' + app.name +'"; '
		posfilestring = posfilestring + "\n}\n"
				
		
	for interface in listInterfaces:
		if edgecolor == "type":
			posfilestring = posfilestring + '"' + interface.fromName + '"' + ' -> ' + '"' + interface.toName + '"' + '['+ interface.edgecolortagtype() + '];\n'
		elif edgecolor == "throughput":
			#posfilestring = posfilestring + '"' + interface.fromName + '"' + ' -> ' + '"' + interface.toName + '"' + '[penwidth='+ str(0.1 + (int(interface.throughput) / 1000))  +'];\n'
			posfilestring = posfilestring + '"' + interface.fromName + '"' + ' -> ' + '"' + interface.toName + '"' + '['+ interface.edgecolortagthroughput() + interface.edgelabel() + interface.bidirectionallabel() + '];\n'
		else: 
			posfilestring = posfilestring + '"' + interface.fromName + '"' + ' -> ' + '"' + interface.toName + '";\n'
		
		
	posfilestring = posfilestring + "\n}\n"
	
	posfile = open("output/out"+timestamp+".pos",'w+')
	posfile.write(posfilestring)
	posfile.close()
	
	return "output/out"+timestamp+".pos"
	
def generateAllServerPos():
	global listApplications
	global listInterfaces
	global listServers

	timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())

	posfilestring = 'digraph G {\n\n overlap=true;\ncompound=true;\nfontname="Myriad Condensed Web";\nsplines=true;\nedge [fontname="Myriad Condensed Web", fontsize=8];\nnode [shape=box, color=skyblue, fontname="Myriad Condensed Web", arrowsize=0.8, fontsize=10];\n'

	for server in listServers:
		if server.inscope == "Yes":
			posfilestring = posfilestring + '"' + server.apptag() + '";\n'
		else:
			posfilestring = posfilestring + '"' + server.apptag() + '" [style = filled, color="'+ colp(8) +'"];\n'

	for interface in listInterfaces:
		serveronetag = "Error"
		servertwotag = "Error"
		for serverone in listServers:
			if serverone.ID == interface.fromServerID:
				serveronetag = serverone.apptag()
		for servertwo in listServers:
			if servertwo.ID == interface.toServerID:
				servertwotag = servertwo.apptag()				

		posfilestring = posfilestring + '"' + serveronetag + '" -> "' + servertwotag + '";\n'

	posfilestring = posfilestring + "\n}\n"
	
	posfile = open("output/out"+timestamp+".pos",'w+')
	posfile.write(posfilestring)
	posfile.close()
	
	return "output/out"+timestamp+".pos"

def generateServerLevelPos(focusapplicationID):
	global listApplications
	global listInterfaces
	global listServers
	#applications and interfaces should be present
	#generates .pos file with timestamp, returns filename
	
	#findBiDirectionalEdges()
	#removed - detailed picture should show all interfaces

	timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
	#print("Timestamp generated: " + timestamp)
	
	posfilestring = 'digraph G {\nsize="15,20";\n overlap=true;\ncompound=true;\nfontname="Myriad Condensed Web";\nsplines=true;\nedge [fontname="Myriad Condensed Web", fontsize=8];\nnode [shape=box, color=skyblue, fontname="Myriad Condensed Web", arrowsize=0.8, fontsize=10];\n'
	
	posfilestring = posfilestring + 'subgraph cluster_0 {\nstyle=filled;\ncolor=lightgrey;\nnode [style=filled,color=white];\n'

	#find app name
	for app in listApplications:
		if app.ID == focusapplicationID:
			posfilestring = posfilestring + 'label = "' + app.name + '";\n'


	firstservertag = ""
	for server in listServers:
		if server.AppID == focusapplicationID:
			if firstservertag == "":
				firstservertag = server.tag()
			posfilestring = posfilestring + '"' + server.tag() + '";'
			posfilestring = posfilestring + "\n"

	#close subgraph
	posfilestring = posfilestring + "\n}\n"

	#create internal connections
	#all webservers to application servers
	#all application servers to database servers

	for server in listServers:
		if server.function == "Application" and server.AppID == focusapplicationID:
			for toserver in listServers:
				if toserver.function == "Webserver" and toserver.AppID == focusapplicationID:
					posfilestring = posfilestring + '"' + server.tag() + '" -> "' + toserver.tag() + '"[weight=100];\n'		

	
	for server in listServers:
		if (server.function == "Database" or server.function == "Oracle RAC") and server.AppID == focusapplicationID:
			for toserver in listServers:
				if toserver.function == "Application" and toserver.AppID == focusapplicationID:
					posfilestring = posfilestring + '"' + server.tag() + '" -> "' + toserver.tag() + '"[weight=100];\n'					

	for server in listServers:
		if (server.function == "Sattelite" or server.function == "Webserver") and server.AppID == focusapplicationID:
			for toserver in listServers:
				if toserver.function == "Database" and toserver.AppID == focusapplicationID:
					posfilestring = posfilestring + '"' + server.tag() + '" -> "' + toserver.tag() + '"[weight=100];\n'					


			
	#add outside connections
	for interface in listInterfaces:
		if interface.toAppID == focusapplicationID:
			thisservertag = firstservertag
			for server in listServers:
				if server.ID == interface.toServerID:
					thisservertag = server.tag()
			for app in listApplications:
				if app.ID == interface.fromAppID:
					posfilestring = posfilestring + '"' + app.name + '" [style = filled, color="#999999" fontsize=8 height=0.2];\n'
					posfilestring = posfilestring + '"' + app.name + '" -> "' + thisservertag + '"[color="#00FF00"];\n'

	for interface in listInterfaces:
		if interface.fromAppID == focusapplicationID:
			thisservertag = firstservertag
			for server in listServers:
				if server.ID == interface.fromServerID:
					thisservertag = server.tag()			
			for app in listApplications:
				if app.ID == interface.toAppID:
					posfilestring = posfilestring + '"' + app.name + '" [style = filled, color="#999999" fontsize=8 height=0.2];\n'					
					posfilestring = posfilestring + '"' +  thisservertag + '" -> "' +  app.name + '"[color="#FF0000"];\n'

	#close graph
	posfilestring = posfilestring + "\n}\n"
	
	posfile = open("output/out"+timestamp+".pos",'w+')
	posfile.write(posfilestring)
	posfile.close()
	
	return "output/out"+timestamp+".pos"

def htmloutput(appfocus):

	htmlstring = '<html><head><title>Infrastructure map</title>'



	#htmlstring = htmlstring + '<script language="JavaScript" type="text/javascript"><!-- function breakout_of_frame() { if (top.location != location) { top.location.href = document.location.href ; } } --> </script>'
	htmlstring = htmlstring + '<STYLE type="text/css">'
	htmlstring = htmlstring + 'table{ font-size: 10px; font-family: verdana; background: #fff; border: solid black}'
	htmlstring = htmlstring + 'tr#header { background: #999;}'
	htmlstring = htmlstring + 'body { font-size: 12px; font-family: verdana;}'
	htmlstring = htmlstring + '</style></head>'
	htmlstring = htmlstring + '<body onload="if (top.location != location) { top.location.href = document.location.href ; }"><embed src="static/out.svg" type="image/svg+xml"/>'

	if appfocus != "none":
		#print outgoing interfaces
		htmlstring = htmlstring + '<br>Outgoing data:<br><table width="800" border="1"><tr id="header"><td>#</td><td>SourceName</td><td>SourceServer</td><td>TargetName</td><td>TargetServer</td><td>Protocol</td><td>Throughput</td></tr>'

		counter = 0
		for interface in listInterfaces:
			outSServer = ""
			outTServer = ""
			if interface.fromAppID == appfocus:
				for server in listServers:
					if server.ID == interface.fromServerID:
						outSServer = server.hostname
					if server.ID == interface.toServerID:
						outTServer = server.hostname
				counter = counter + 1
				htmlstring = htmlstring + ('<tr><td>%02d' % counter + "</td><td>" + 
			   		interface.fromName + "</td><td>" + 
			   		outSServer + "</td><td>" +
			   		interface.toName + "</td><td>" +
			   		outTServer + "</td><td>" +
			   		interface.protocol + "</td><td>" +
			   		"%02d" % interface.throughput + '</td></tr>')

		htmlstring = htmlstring + '</table><br>'


		htmlstring = htmlstring + 'Incoming data:<br><table width="800" border="1"><tr id="header"><td>#</td><td>SourceName</td><td>SourceServer</td><td>TargetName</td><td>TargetServer</td><td>Protocol</td><td>Throughput</td></tr>'
		#counter = 0
		for interface in listInterfaces:
			outSServer = ""
			outTServer = ""
			if interface.toAppID == appfocus:
				for server in listServers:
					if server.ID == interface.fromServerID:
						outSServer = server.hostname
					if server.ID == interface.toServerID:
						outTServer = server.hostname
				counter = counter + 1
				htmlstring = htmlstring + ('<tr><td>%02d' % counter + "</td><td>" + 
			   		interface.fromName + "</td><td>" + 
			   		outSServer + "</td><td>" +
			   		interface.toName + "</td><td>" +
			   		outTServer + "</td><td>" +
			   		interface.protocol + "</td><td>" +
			   		"%02d" % interface.throughput + '</td></tr>')

		htmlstring = htmlstring + '</table><br><br>'

		#repeat, list legenda for interfaces
		counter = 0
		
		for interface in listInterfaces:
			if interface.fromAppID == appfocus:
				counter = counter + 1
				htmlstring = htmlstring + '%02d' % counter + ". " + interface.interfacefunction + "<br>"		

		for interface in listInterfaces:
			if interface.toAppID == appfocus:
				counter = counter + 1
				htmlstring = htmlstring + '%02d' % counter + ". " + interface.interfacefunction + "<br>"	


		htmlstring = htmlstring + '<br><br><a href="http://localhost:8080/">Back</a>'

	htmlstring = htmlstring + '</body></html>'

	return htmlstring

def findBiDirectionalEdges():
	global listInterfaces
	#remove double interfaces; add troughputs
	#remove internal interfaces
	#if from -> to and to -> from exist, remove one and make remaining bidirectional

	#first, remove application internal interfaces
	for interface in reversed(listInterfaces):
		print '{}{} {} {}'.format("Interface ", interface.ID, interface.toAppID, interface.fromAppID )
		if interface.toAppID == interface.fromAppID:
			listInterfaces.remove(interface)
			print '{}{}'.format("Removed: ", interface.ID)

	#add throughputs for double interfaces
	#make interfaces bidirectional
	for interface in reversed(listInterfaces):
		for interfacecompare in reversed(listInterfaces):
			if interface.ID != interfacecompare.ID:
				if interface.toAppID == interfacecompare.toAppID and interface.fromAppID == interfacecompare.fromAppID:
					interface.throughput = interface.throughput + interfacecompare.throughput
					listInterfaces.remove(interfacecompare)
				if interface.toAppID == interfacecompare.fromAppID and interface.fromAppID == interfacecompare.toAppID:	
					listInterfaces.remove(interface)
					interface.bidirectional = "Yes"
					interface.throughput = interface.throughput + interfacecompare.throughput
					listInterfaces.append(interface)
					print '{}{}'.format("About to remove interface: ", interfacecompare.ID)
					print '{}{}'.format("compared with ", interface.ID) 
					listInterfaces.remove(interfacecompare)

class nApplication(object):
	
	def __init__(self, ID, name, scope, layer):
		self.ID = int(ID)
		self.name = name
		self.scope = scope
		self.layer = layer

class nServer(object):
	def __init__(self, ID, AppID, function, hostname, appname, inscope):
		self.ID = int(ID)
		self.AppID = int(AppID)
		self.function = function	
		self.hostname = hostname
		self.appname = appname
		self.inscope = inscope	

	def tag(self):
		return str(self.ID) + ". " + self.function + '\n' + self.hostname

	def apptag(self):
		if self.inscope == "Yes":
			return str(self.ID) + ". " + self.appname + "\n" + self.function + '\n' + self.hostname		
		else:
			return self.appname + "\n" + self.hostname	
		
class nInterface(object):
	#20130823 changed color functions, added label function, added bidirectional tag
	def __init__(self, ID, fromAppID, fromServerID, fromName, toAppID, toServerID, toName, throughput, itype, bidirectional, interfacefunction, protocol):
		self.ID = int(ID)
		self.fromAppID = int(fromAppID)
		if fromServerID != '':
			self.fromServerID = int(fromServerID)
		else:
			self.fromServerID = 0
		self.fromName = fromName
		self.toAppID = int(toAppID)
		if toServerID != '':
			self.toServerID = int(toServerID)
		else:
			self.toServerID = 0
		self.toName = toName
		self.bidirectional = bidirectional
		if throughput <> "":
			self.throughput = int(throughput)
		else:
			self.throughput = 0
		self.itype = itype
		self.protocol = protocol
		self.interfacefunction = interfacefunction
		
	def edgecolortagthroughput(self):
		if self.throughput == 0:
			return 'color="' + colp(8) + '"'
		elif self.throughput < 1000:
			return 'color="' + colp(2) + '"'
		elif self.throughput < 5000:
			return 'color="' + colp(5) + '"'
		elif self.throughput < 25000:	
			return 'color="' + colp(4) + '"'
		else:
			return 'color="' + colp(0) + '"'	
			
	def edgecolortagtype(self):
		if self.itype == "Database":
			return "colorscheme=dark28, color=1"
		elif self.itype == "FTP":
			return "colorscheme=dark28, color=2"
		elif self.itype == "Fileshare":
			return "colorscheme=set19, color=3"
		elif self.itype == "Extractor":
			return "colorscheme=set19, color=4"
		else:
			return "colorscheme=set19, color=9"	

	def edgelabel(self):
		if self.throughput == 0:
			return ''
		elif self.throughput < 1000:
			return 'label="<1Gb"'
		elif self.throughput < 5000:
			return 'label="<5Gb"'
		elif self.throughput < 25000:	
			return 'label="<25Gb"'			
		else:
			return 'label=">25Gb"'

	def bidirectionallabel(self):
		if self.bidirectional == "Yes":
			return 'dir="both"'	
		else:
			return ''		
		

urls = (
  '/', 'Index'
)

listApplications = []
listInterfaces = []
listServers = []

app = web.application(urls, globals())

render = web.template.render('templates/')

class Index(object):
    def GET(self):
    	global listApplications
    	global listInterfaces
    	global focusapp
    	a = readfiles()
    	backurl = "<b>Hello</b>"

    	form = web.input(focusapp="none")
    	print form.focusapp
    	if form.focusapp == "none":
    		#system("dot -Tsvg -ostatic/out.svg " + generateAllServerPos())
    		#system("dot -Tpdf -ostatic/servermap.pdf " + generateAllServerPos())
    		system("dot -Tsvg -ostatic/out.svg " + generatePosFile("none", "throughput", "none"))
    		system("dot -Tpdf -ostatic/inframap.pdf " + generatePosFile("none", "throughput", "none"))
    		return htmloutput("none")
    	else:
    		system("dot -Tsvg -ostatic/out.svg " + generateServerLevelPos(int(form.focusapp)))
    		return htmloutput(int(form.focusapp))

    def POST(self):
    	form=web.input(mode="overview", nodecolor="none", edgecolor="none", edgewidth="none")
    	
    	a = readfiles()
    	system("dot -Tsvg -ostatic/out.svg " + generatePosFile(form.nodecolor, form.edgecolor, form.edgewidth))
    	system("dot -Tpdf -ostatic/out.pdf " + generatePosFile(form.nodecolor, form.edgecolor, form.edgewidth))
    	return render.index()
    	

if __name__ == "__main__":
    app.run()
    
    
