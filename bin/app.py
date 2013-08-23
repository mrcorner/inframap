import web
import time
from os import system

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
		interface = nInterface(splitline[0], splitline[1], splitline[2], splitline[3], splitline[4], splitline[8], splitline[6])
		if listInterfaces.count(interface) == 0:
			listInterfaces.append(interface)
	intfile.close()	
	
	return 1
	
def generatePosFile(nodecolor, edgecolor, edgewidth):
	global listApplications
	global listInterfaces
	#applications and interfaces should be present
	#generates .pos file with timestamp, returns filename
	
	timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
	print("Timestamp generated: " + timestamp)
	
	posfilestring = 'digraph G {\nsize="15,100"\noverlap=false;\nfontname="Myriad Condensed Web";\nsplines=true;\nedge [fontname="Myriad Condensed Web", fontsize=8];\nnode [shape=box, color=skyblue, fontname="Myriad Condensed Web" fontsize=10];\n'
	posfilestring = posfilestring + "{\nnode [shape=plaintext, fontsize=14];\nSource -> ETL -> Database -> Application -> Presentation;\n}\n"
	
	for app in listApplications:
		if app.scope == "Yes":
			posfilestring = posfilestring + '"' + app.name + '"' + ';\n'
		else:
			posfilestring = posfilestring + '"' + app.name + '"' + '[style = filled, color=grey70];\n'
	posfilestring = posfilestring + "\n"
	
	layers = ["Source", "ETL", "Database", "Application", "Presentation"]
	
	
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
			posfilestring = posfilestring + '"' + interface.fromName + '"' + ' -> ' + '"' + interface.toName + '"' + '['+ interface.edgecolortagthroughput() + '];\n'
		else: 
			posfilestring = posfilestring + '"' + interface.fromName + '"' + ' -> ' + '"' + interface.toName + '";\n'
		
		
	posfilestring = posfilestring + "\n}\n"
	
	posfile = open("output/out"+timestamp+".pos",'w+')
	posfile.write(posfilestring)
	posfile.close()
	
	return "output/out"+timestamp+".pos"
	
	
		
class nApplication(object):
	
	def __init__(self, ID, name, scope, layer):
		self.ID = ID
		self.name = name
		self.scope = scope
		self.layer = layer
		
class nInterface(object):
	
	def __init__(self, ID, fromID, fromName, toID, toName, throughput, itype):
		self.ID = ID
		self.fromID = fromID
		self.fromName = fromName
		self.toID = toID
		self.toName = toName
		if throughput <> "":
			self.throughput = int(throughput)
		else:
			self.throughput = 0
		self.itype = itype
		
	def edgecolortagthroughput(self):
		if self.throughput == 0:
			return "colorscheme=set19, color=9"
		elif self.throughput < 100:
			return "colorscheme=set19, color=3"
		elif self.throughput < 1000:
			return "colorscheme=set19, color=6"
		elif self.throughput < 5000:	
			return "colorscheme=set19, color=5"
		else:
			return "colorscheme=set19, color=1"	
			
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
    	print len(listInterfaces)
    	greeting = "Hello" 
        return render.index()
        
    def POST(self):
    	form=web.input(nodecolor="none", edgecolor="none", edgewidth="none")
    	
    	a = readfiles()
    	system("dot -Tsvg -ostatic/out.svg " + generatePosFile(form.nodecolor, form.edgecolor, form.edgewidth))
    	print len(listInterfaces)
    	greeting = "Hello" 
        return render.index()
    	

if __name__ == "__main__":
    app.run()
    
    
