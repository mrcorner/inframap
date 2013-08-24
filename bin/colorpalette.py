#functions to easily pick a color


#function that returns a color from a palette

def colorpal(colorNumber, colorPalette):

	if colorPalette == "default":
		#default palette
		if colorNumber == 0:
			return "#e41a1c"
		if colorNumber == 1:
			return "#377eb8"
		if colorNumber == 2:
			return "#4daf4a"
		if colorNumber == 3:
			return "#984ea3"
		if colorNumber == 4:
			return "#ff7f00"
		if colorNumber == 5:
			return "#ffff33"			
		if colorNumber == 6:
			return "#a65628"
		if colorNumber == 7:
			return "#f781bf"
		if colorNumber == 8:
			return "#999999"						


def colp(colorNumber):
	#returns default color palette color
	return colorpal(colorNumber, "default")


#function that returns a color from a scale