import web
import time
from os import system
from colorpalette import *

def readfiles():
	global listApplications
	global listInterfaces
	listApplications = []
	listInterfaces = []
	# read applications, interfaces and settings into dictionaries
	import string

	#read applications

	appfile = open("docs/applications.txt")
	for line in appfile:
		splitline = string.split(line, "\t")
		app = nApplication(splitline[0], splitline[2], splitline[1], splitline[17])
		listApplications.append(app)
	appfile.close()
	
	#read interfaces
	
	intfile = open("docs/interfaces.txt")
	for line in intfile:	
		splitline = string.split(line, "\t")
		#20130823 add bidirectional as input
		interface = nInterface(splitline[0], splitline[1], splitline[2], splitline[3], splitline[4], splitline[8], splitline[6], splitline[5])
		if listInterfaces.count(interface) == 0:
			listInterfaces.append(interface)
	intfile.close()	
	
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
			posfilestring = posfilestring + '"' + app.name + '"' + ';\n'
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
	
def findBiDirectionalEdges():
	global listInterfaces
	#remove double interfaces; add troughputs
	#if from -> to and to -> from exist, remove one and make remaining bidirectional

	for interface in listInterfaces:
		for interfacecompare in listInterfaces:
			if interface.ID != interfacecompare.ID:
				if interface.toID == interfacecompare.toID and interface.fromID == interfacecompare.fromID:
					interface.throughput = interface.throughput + interfacecompare.throughput
					listInterfaces.remove(interfacecompare)
				if interface.toID == interfacecompare.fromID and interface.fromID == interfacecompare.toID:	
					interface.bidirectional = "Yes"
					interface.throughput = interface.throughput + interfacecompare.throughput
					listInterfaces.remove(interfacecompare)


class nApplication(object):
	
	def __init__(self, ID, name, scope, layer):
		self.ID = ID
		self.name = name
		self.scope = scope
		self.layer = layer
		
class nInterface(object):
	#20130823 changed color functions, added label function, added bidirectional tag
	def __init__(self, ID, fromID, fromName, toID, toName, throughput, itype, bidirectional):
		self.ID = ID
		self.fromID = fromID
		self.fromName = fromName
		self.toID = toID
		self.toName = toName
		self.bidirectional = bidirectional
		if throughput <> "":
			self.throughput = int(throughput)
		else:
			self.throughput = 0
		self.itype = itype
		
	def edgecolortagthroughput(self):
		if self.throughput == 0:
			return 'color="' + colp(8) + '"'
		elif self.throughput < 1000:
			return 'color="' + colp(2) + '"'
		elif self.throughput < 5000:
			return 'color="' + colp(5) + '"'
		elif self.throughput < 10000:	
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
		else:
			return 'label=">5Gb"'

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

app = web.application(urls, globals())

render = web.template.render('templates/')



class Index(object):
    def GET(self):
    	global listApplications
    	global listInterfaces
    	a = readfiles()
    	system("dot -Tsvg -ostatic/out.svg " + generatePosFile("none", "none", "none"))
    	
        return render.index()
        
    def POST(self):
    	form=web.input(nodecolor="none", edgecolor="none", edgewidth="none")
    	
    	a = readfiles()
    	system("dot -Tsvg -ostatic/out.svg " + generatePosFile(form.nodecolor, form.edgecolor, form.edgewidth))
    	system("dot -Tpdf -ostatic/out.pdf " + generatePosFile(form.nodecolor, form.edgecolor, form.edgewidth))

    	 
        return render.index()
    	

if __name__ == "__main__":
    app.run()
    
    
