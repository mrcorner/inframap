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
							 rowx[serlegend.index('Hostname')].value)
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
	
	posfilestring = 'digraph G {overlap=false;\ncompound=true;\nfontname="Myriad Condensed Web";\nsplines=true;\nedge [fontname="Myriad Condensed Web", fontsize=8];\nnode [shape=box, color=skyblue, fontname="Myriad Condensed Web", arrowsize=0.8, fontsize=10];\n'
	
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
					posfilestring = posfilestring + '"' + server.tag() + '" -> "' + toserver.tag() + '";\n'		

	
	for server in listServers:
		if (server.function == "Database" or server.function == "Oracle RAC") and server.AppID == focusapplicationID:
			for toserver in listServers:
				if toserver.function == "Application" and toserver.AppID == focusapplicationID:
					posfilestring = posfilestring + '"' + server.tag() + '" -> "' + toserver.tag() + '";\n'					

	for server in listServers:
		if (server.function == "Sattelite" or server.function == "Webserver") and server.AppID == focusapplicationID:
			for toserver in listServers:
				if toserver.function == "Database" and toserver.AppID == focusapplicationID:
					posfilestring = posfilestring + '"' + server.tag() + '" -> "' + toserver.tag() + '";\n'					


			
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





class nApplication(object):
	
	def __init__(self, ID, name, scope, layer):
		self.ID = int(ID)
		self.name = name
		self.scope = scope
		self.layer = layer

class nServer(object):
	def __init__(self, ID, AppID, function, hostname):
		self.ID = int(ID)
		self.AppID = int(AppID)
		self.function = function	
		self.hostname = hostname	

	def tag(self):
		return str(self.ID) + ". " + self.function + '\n' + self.hostname	
	
		
class nInterface(object):
	#20130823 changed color functions, added label function, added bidirectional tag
	def __init__(self, ID, fromAppID, fromServerID, fromName, toAppID, toServerID, toName, throughput, itype, bidirectional, protocol):
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
		
	


import sys

appFilter = sys.argv[1]

listApplications = []
listInterfaces = []
listServers = []


readfiles()

#print outgoing interfaces
print("#\tSourceName\tSourceServer\tTargetName\tTargetServer\tProtocol \tThroughput")
counter = 0
for interface in listInterfaces:
	outSServer = ""
	outTServer = ""
	if interface.fromName == appFilter:
		for server in listServers:
			if server.ID == interface.fromServerID:
				outSServer = server.hostname
			if server.ID == interface.toServerID:
				outTServer = server.hostname
		counter = counter + 1
		print (str(counter) + "\t" + 
			   interface.fromName + "\t" + 
			   outSServer + "\t" +
			   interface.toName + "\t" +
			   outTServer + "\t" +
			   interface.protocol + "\t" +
			   "%02d" % interface.throughput)
print(" ")
print("#\tSourceName\tSourceServer\tTargetName\tTargetServer\tProtocol \tThroughput")
counter = 0
for interface in listInterfaces:
	outSServer = ""
	outTServer = ""
	if interface.toName == appFilter:
		for server in listServers:
			if server.ID == interface.fromServerID:
				outSServer = server.hostname
			if server.ID == interface.toServerID:
				outTServer = server.hostname
		counter = counter + 1
		print (str(counter) + "\t" + 
			   interface.fromName + "\t" + 
			   outSServer + "\t" +
			   interface.toName + "\t" +
			   outTServer + "\t" +
			   interface.protocol + "\t" +
			   "%02d" % interface.throughput)		
		


