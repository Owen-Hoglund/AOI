
'''############################################################################################################
#
#					Desktop AOI Program - V1.0
#
#					John Bonfitto - System Design And Development
#					Feb. 20, 2023 - MM.DD,YYYY
#
#					Cheap and dirty AOI program for looking for any missing components on PCBs
#
#					To Do:
#
#					1. GUI to turn on/Off Modes and Features(Teach, Find, etc..)
#					2. Implement Zoom
#					3. Add crosshairs for initial alignment of PCB to camera
#					4. Implement the alignment routine to get X-Y offsets before we do pattern search
#					5. Research and add additional/more specific pattern matching algorithms
#
#
#########################################################################################################
'''

import cv2
import imutils as imutils
import numpy as np
from PIL import ImageChops
from matplotlib import pyplot as plt
from os import listdir
import time

###########################################################################
#
#			import all the saved component files
#
########################################################################
from os.path import isfile, join

mypath="c:\AOI\\Files"
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]


#cv2.NamedWindow("HD Webcam C6155", 1)


'''
				Jmb - Some initialization stuff

'''
drag = False
drag_start = (0,0)
drag_end = (0,0)
save_drag_start = (0,0)
save_drag_end = (0,0)
RED=(0,0,255)
BLUE=(255,0,0)
GREEN=(0,255,0)


##############################################################################
##
##			JMb - This came with the original code snippet I stole.  I am not
#			really using this now so we can clean it up later
##
###############################################################################
patterns = []
regions = []
show_regions = False
show_mask = True
#show_mask = False
black = 0xFE



######################################################################################################################
#
#				JMB - Teach components and save the image file(teach_components = True)
#				or Find Components(teach_components = False)
#
#				Eventually this will be selected in the GUI
#
#############################################################################
# teach_components = True
teach_components = False


####################################################################
#
#				Use webcam as template,(use_camera = True) or saved image use_camera = False
#
#				Eventually this will be selected in the GUI
#
#############################################################################
#use_camera = True
use_camera = False

####################################################################
#
#				Try alignment feature
#
#				JMB - right now just for debug.  Eventually this can be
#				selected in the GUI but I'm guessing we will want to do this before ths start of
#				search
#
#############################################################################
#align_camera = True
align_camera = False



############################################################################################
#
#					JMB - 2/23/23 Teach or Find components with webcam
#
#########################################################################################
def show_webcam():
	global drag_start, drag_end, img, patterns, regions, show_regions, show_mask, draw, bSave, save_drag_start, save_drag_end
	zoom = False
	#cam = cv2.VideoCapture(0)
	#cam = cv2.VideoCapture(1)
	#cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
	#cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
	#ret_val, img = cam.read()

	#find_alignment_mark()			## jmb turnm on for debugging debug
	#############################################################
	#
	#		Call pattern_match?
	#
	########################################################
	print('teach_components = ',teach_components)
	if teach_components == False:
		pattern_match_All()
	else:
		teach()			#call teach()



################################################################################
##
##				Teach components by using mouse to drag a rectangle around it, then when the right mouse button is
#				released save the image file
#
##############################################################################

def teach():
	global drag_start, drag_end, img, patterns, regions, show_regions, show_mask, draw, bSave, save_drag_start, save_drag_end
	zoom = False
	#cam = cv2.VideoCapture(0)
	cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # jmb 2/24/23 much much faster!
	#cam = cv2.VideoCapture(1)
	cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
	ret_val, img = cam.read()

	windowname = 'Teach Components'
	cv2.namedWindow(windowname)
	cv2.setMouseCallback(windowname, on_mouse, 0)


	while True:
		####################################################################################
		#
		#			Grab Image from Camera
		#
		####################################################################################
		ret_val, image = cam.read()

		####################################################################################
		#
		#			Draw last rectangle
		#
		####################################################################################
		cv2.rectangle(img=image, pt1=save_drag_start, pt2=save_drag_end, color=BLUE, thickness=2, lineType=8, shift=0)
		cv2.imshow(windowname, image)

		######################################################################################
		##
		##				Must call waitKey() for image to be displayed
		##
		#####################################################################################
		char = chr(cv2.waitKey(1) & 255)
		#cv2.waitKey(1)

	cv2.destroyAllWindows()


	########################################################################################
	##
	##		JMB - eventually we want to play around with zoom, etc..for now don't worry about it
	##
	###################################################################################
	"""
	#cv2.setMouseCallback('John B AOI', on_mouse, 1)
	#while(True):
	while True:
		####################################################################################
		#
		#			Grab Image from Camera
		#
		####################################################################################
		ret_val, img = cam.read()

		####################################################################################
		#
		#			Draw last rectangle
		#
		####################################################################################
		cv2.rectangle(img=img, pt1=save_drag_start, pt2=save_drag_end, color=black, thickness=1, lineType=8, shift=0)

		#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		char = chr(cv2.waitKey(1) & 255)
		if (char == 'q'):
			break
		elif (char == 27):
			break
		elif (char == 't'):
			cv2.imwrite("output.jpg", img)
		elif (char == 'd'):
			show_regions = not show_regions
		elif (char == 's'):
			show_mask = not show_mask
		elif (char =='z'):
			zoom = not zoom
		#diff = cv2.absdiff(ref_image,img)
		img = cv2.cvtColor(img,cv2.COLOR_RGB2RGBA)

		#debug
		#component_file = mypath + '//304-166.jpg'
		#FindComponent(original_image, component_file)
		#FindComponent(img, component_file,BLUE)
		#cv2.waitKey(0)

		#show_mask = False
		if (show_mask):
			#small = cv2.resize(mask, (0, 0), fx=0.25, fy=0.25)	#scale from 1280x720 to 320x180
			#small2 = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)  # scale from 1280x720 to 320x180
			#mask_inv = cv2.bitwise_not(mask)
			#diff = cv2.bitwise_and(img,img,mask=mask)

			diff = cv2.bitwise_and(img, img, mask=None)
			#diff = cv2.bitwise_and(img,img,mask=mask_inv)
			for i in range(len(patterns)):
				sub = img[(int)(regions[i][1])-10:(int)(regions[i][1])+(int)(regions[i][3])+10,(int)(regions[i][0])-10:(int)(regions[i][0])+(int)(regions[i][2])+10]

				if (show_regions==True):
					cv2.rectangle(diff,((int)(regions[i][0])-10,(int)(regions[i][1])-10), ((int)(regions[i][2])+(int)(regions[i][0])+10,(int)(regions[i][3])+(int)(regions[i][1])+10), (0,255,0), 1)


				#res = cv2.matchTemplate(sub,patterns[i],cv2.TM_CCOEFF_NORMED)
				res=.79

				h,w = patterns[i].shape[0:2]
				threshold = 0.80
				loc = np.where (res >= threshold)
				for pt in zip(*loc[::-1]):
					cv2.rectangle(diff,(pt[0]+(int)(regions[i][0])-10,pt[1]+(int)(regions[i][1])-10), (pt[0] + (int)(regions[i][0])+w-10, pt[1]+(int)(regions[i][1])+h-10), (0,0,0), -1)
					cv2.rectangle(diff,drag_start, drag_end, (255,0,0), 1)
			if (zoom):
				sub = img[320:454,544:680]
				resized_image = cv2.resize(sub, (0,0),fx=4,fy=4)
				diff[119:655,340:884] = resized_image
		else:
			diff = img
		cv2.imshow('John B AOI', diff)
	cv2.destroyAllWindows()
"""



################################################################################
##
##			on_mouse routine allow us to track mouse buttons and position.  I use this during the teach routine
##
##############################################################################
def on_mouse(event, x, y, flags, params):
	#global drag, drag_start, drag_end, img, patterns, regions, draw, bSave, save_drag_start, save_drag_end
	global drag, drag_start, drag_end, patterns, img, regions, save_drag_start, save_drag_end
	if event == cv2.EVENT_LBUTTONDOWN:
		drag_start = (x, y)
		drag_end = (x, y)
		save_drag_start = (x,y)
		save_drag_end = (x,y)
		drag = True
		#draw = True
		#bSave = False
	elif event == cv2.EVENT_LBUTTONUP:
		drag = False
		drag_end = (x, y)
		save_drag_end = (x, y)
		#draw = False
		#cv2.line(img=img, pt1=x, pt2=y, color=black, thickness=1, lineType=8, shift=0)
		if (drag_end[1]-drag_start[1])>10 and (drag_end[0]-drag_start[0])>10:
			crop = img[drag_start[1]:drag_end[1],drag_start[0]:drag_end[0]]
			if(align_camera):
				name = (str)(drag_start[0]) + '-' + (str)(drag_start[1]) + '-Align.jpg'
			else:
				name = (str)(drag_start[0])+'-'+(str)(drag_start[1])+'.jpg'
			cv2.imwrite(mypath+'/'+name,crop)
			pattern = cv2.imread(mypath+"/"+name,1)
			patterns.append(cv2.cvtColor(pattern,cv2.COLOR_RGB2RGBA))
			pre = (name.split('.',1))[0]
			rectparts = pre.split('-')
			h,w = pattern.shape[0:2]
			rectparts.append(w)
			rectparts.append(h)
			regions.append(rectparts)

			#cv2.rectangle(img=img, pt1=drag_start, pt2=drag_end, color=black, thickness=1, lineType=8, shift=0)
			drag_start = (0,0)
			drag_end = (0,0)
			#bSave=True
			#cv2.rectangle(img=img, pt1=save_drag_start, pt2=save_drag_end, color=black, thickness=1, lineType=8, shift=0)
			#cv2.line(img=img, pt1=10, pt2=20, color=black, thickness=1, lineType=8, shift=0)
	elif event == cv2.EVENT_MOUSEMOVE and drag==True:
		drag_end = (x,y)
		save_drag_end = (x,y)
		print('drag end = ',x,y)
		#if ((draw == True) and (bSave == False)):
		#cv2.rectangle(img=img, pt1=save_drag_start, pt2=save_drag_end, color=black, thickness=1, lineType=8, shift=0)




################################################################################
##
##				JMB 2/25/23 Debug - Align routine
#
##############################################################################

def align():
	global drag_start, drag_end, img, patterns, regions, show_regions, show_mask, draw, bSave, save_drag_start, save_drag_end
	zoom = False
	#cam = cv2.VideoCapture(0)
	cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # jmb 2/24/23 much much faster!
	#cam = cv2.VideoCapture(1)
	cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
	ret_val, img = cam.read()

	windowname = 'Alignment'
	cv2.namedWindow(windowname)
	cv2.setMouseCallback(windowname, on_mouse, 0)



	while True:
		####################################################################################
		#
		#			Grab Image from Camera
		#
		####################################################################################
		ret_val, image = cam.read()

		####################################################################################
		#
		#			Draw last rectangle
		#
		####################################################################################
		cv2.rectangle(img=image, pt1=save_drag_start, pt2=save_drag_end, color=BLUE, thickness=2, lineType=8, shift=0)
		cv2.imshow(windowname, image)

		######################################################################################
		##
		##				Must call waitKey() for image to be displayed
		##
		#####################################################################################
		char = chr(cv2.waitKey(1) & 255)
		#cv2.waitKey(1)

	cv2.destroyAllWindows()




##############################################################################################
#
#			JMB - Find alignment mark
#
#			If we search for an alignment mark and get the X Offset and Y Offset , we can accomodate for small x-Y
#			movement in the board vby adding in the offsets
#			In debug status
#
##########################################################################################


def find_alignment_mark():
	xpos = 0				#componentposition rray index
	ypos = 1
	height = 0
	width = 1
	LEFT = 0
	RIGHT = 1
	UP = 2
	DOWN = 3

	FORTY_FIVE_DEGREES = 4
	NEG_FORTY_FIVE_DEGREES = 5

	ONE_THIRTY_FIVE_DEGREES = 6
	NEG_ONE_THIRTY_FIVE_DEGREES = 7

	offsetx = 0
	offsety = 0
	offset = 0

	direction = LEFT

	maxsearch = 10		#50 pixels in any direction

	#print('Before VideoCapture')
	#cam = cv2.VideoCapture(1)
	cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)			#jmb 2/24/23 much much faster!
	#print('After VideoCapture')
	cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
	while True:
		##########################################################################
		#
		#			JMB - 2/23/23 Grab the live part image to use when looking for components
		#
		####################################################################
		#print('Before cam.read')
		ret_val, live_img = cam.read()
		#print('After cam.read')
		#############################################################################
		#
		#			Loop through all the saved image files
		#
		##############################################################################

		#while True:
		#for i in onlyfiles:
			#pattern = cv2.imread(mypath + "/" + i, 1)  # read a component file

		#componentfile = mypath + "/" + i

		#"c:\AOI\\Files
		componentfile = mypath + "\\1022-50-Align.jpg"
		print('Alignemnt File = ', componentfile)

		component_image = cv2.imread(componentfile)

		#cv2.imshow("Reference", component_image)
		#cv2.waitKey(0)
		#component_image = cv2.cvtColor(crop_img, cv2.COLOR_RGB2RGBA)

		#############################################################################
		#
		#			Call GetComponentXYFromFile(componentfile) to get the component X,Y
		#			from the filename
		#
		############################################################################
		componentposition =GetComponentXYFromFile(componentfile)


		#print('From Function ComponentXLocation = ', componentposition[0])
		#print('From Function ComponentYLocation = ', componentposition[1])

		componentposition=[1022,50]

		print('From Function ComponentXLocation = ', componentposition[0])
		print('From Function ComponentYLocation = ', componentposition[1])

		#componentfile[xpos] = 1022
		#componentfile[ypos] = 50

		show_mask = True
		zoom = False
		show_regions = True
		if (show_mask):
			################################################################################
			#
			#			Read the original saved image file from when we taught the components
			#			Eventually we want to use the live image
			############################################################################
			if (use_camera):
				saved_image = live_img
			else:
				savedfile = mypath + '\\original image\\saved_image.jpg'
				saved_image = cv2.imread(savedfile)
				cv2.waitKey(300)			#delay 300 msecs for viewing

			x = componentposition[xpos]
			y = componentposition[ypos]


			height, width = saved_image.shape[0:2]

			##################################################################################
			#
			#				Get the component X,Y Position from the file
			#
			###############################################################################
			#componentposition = GetComponentXYFromFile(componentfile)

			##################################################################################
			#
			#				Get the component Dimensions(Height, Width) from the file
			#
			###############################################################################
			#componentdimenions = GetComponentDimensionsFromImage(component_image)
			componentdimenions = GetComponentDimensionsFromFile(componentfile)
			component_height, component_width = componentdimenions[0:2]

			component_height = 24		#debug just set
			component_width = 25

			c_xpos = componentposition[xpos] + offsetx
			c_ypos = componentposition[ypos] + offsety

			print('c_xpos = ', c_xpos)


			##############################################################################
			##
			##		Create the cropped image from the saved image by taking all the pixels from the
			# 		starting y,x position and adding the component height and width
			###############################################################################
			#crop_img = saved_image[componentposition[ypos]:componentposition[ypos] + component_height,
					   #componentposition[xpos]:componentposition[xpos] + component_width]

			crop_img = saved_image[c_ypos:c_ypos + component_height,c_xpos:c_xpos + component_width]

			ch, cw = crop_img.shape[0:2]


			##############################################################################
			##
			##			JMB - Compute error using the Mean Squared Error - MSE Method
			##
			##############################################################################
			err = np.sum((crop_img.astype("float") - component_image.astype("float")) ** 2)
			err /= float(crop_img.shape[0] * crop_img.shape[1])

			print('err = ', err)
			#cv2.waitKey(300)



			xStart = c_xpos
			xEnd = xStart + component_width
			yStart = c_ypos
			yEnd = yStart + component_height

			###################################################################################
			#
			#		Draw the rectangle around the expected location on the image and show it
			#
			#############################################################################
			# windowname = 'Find Component' + component_file
			windowname = 'Find Component'
			if(use_camera):
				windowname+=' Live Mode'
			else:
				windowname += ' Simulate Mode'


			color = GREEN
			if err > 8000:
				color = RED
			cv2.rectangle(saved_image, (xStart, yStart), (xEnd, yEnd), color, 2)

			# cv2.imshow('Find Component', original_image)
			cv2.imshow(windowname, saved_image)

			# component_file

			#############################################################################
			#
			#			Display as topmost window for 100ms
			#
			#########################################################################ggg
			# cv2.setWindowProperty('Find Component', cv2.WND_PROP_TOPMOST, 1)

			cv2.setWindowProperty(windowname, cv2.WND_PROP_TOPMOST, 1)
			cv2.waitKey(100)


			print('offset x = ',offsetx)
			print('offset y = ', offsety)
			print('offset = ', offset)
			print('Direction = ', direction)

			if err > 8000:
				if(direction == LEFT):
					offsetx -= 1
					offset = offsetx
				if (direction == RIGHT):
					offsetx += 1
					offset = offsetx
				if (direction == UP):
					offsety -= 1
					offset = offsety
				if (direction == DOWN):
					offsety += 1
					offset = offsety
				if (direction == FORTY_FIVE_DEGREES):
					offsetx += 1
					offsety -= 1
					offset = offsety
				if (direction == NEG_FORTY_FIVE_DEGREES):
					offsetx -= 1
					offsety += 1
					offset = offsety
				if (direction == ONE_THIRTY_FIVE_DEGREES):
					offsetx += 1
					offsety += 1
					offset = offsety
				if (direction == NEG_ONE_THIRTY_FIVE_DEGREES):
					offsetx -= 1
					offsety -= 1
					offset = offsety

				if(abs(offset)>maxsearch):
					offsetx = 0
					offsety = 0
					offset = 0
					if(direction == LEFT):
						direction = RIGHT
					elif(direction == RIGHT):
						direction=UP
					elif (direction == UP):
						direction = DOWN
					elif (direction == DOWN):
						direction = FORTY_FIVE_DEGREES
					elif (direction == FORTY_FIVE_DEGREES):
						direction = NEG_FORTY_FIVE_DEGREES
					elif (direction == NEG_FORTY_FIVE_DEGREES):
						direction = ONE_THIRTY_FIVE_DEGREES
					elif (direction == ONE_THIRTY_FIVE_DEGREES):
						direction = NEG_ONE_THIRTY_FIVE_DEGREES
					elif (direction == NEG_ONE_THIRTY_FIVE_DEGREES):
						break
			else:
				cv2.waitKey(0)

'''				
			######################################################################################
			##
			##			Call FindComponnet and draw a box on the image where we expect it to be
			##			We can uise either a saved_image or the ive image
			##
			#################################################################################
			if err < 8000:
				FindComponent(saved_image,componentfile,GREEN)
				cv2.waitKey(0)
				#windowname = 'Find Component' + componentfile
				#time.sleep(1)
				#cv2.destroyWindow(windowname)
			else:
				###################################################################################
				#
				#			JMbn 2/23/23 If we fail, Draw a RED box around expected location
				#			and open a new window to show the image we expected to find
				#			Right now we will pause and wait for a key so we can see what happened
				#
				##################################################################################
				FindComponent(saved_image, componentfile, RED)
				offsetx-=10
				#component_image = cv2.resize(component_image, (0,0),fx=4,fy=4)
				#cv2.imshow("Missing Component", component_image)
				#cv2.setWindowProperty('Missing Component', cv2.WND_PROP_TOPMOST, 1)
				#cv2.waitKey(0)
				#cv2.destroyWindow("Missing Component")
				cv2.waitKey(500)
				#cv2.destroyAllWindows()
			#time.sleep(1)
'''
	#time.sleep(2)				#JMB Debug - delay 2 seconds and repeat so we can test over and over again for ropbustness
	#cv2.destroyAllWindows()
cv2.waitKey(0)
cv2.destroyAllWindows()





##############################################################################################
#
#			JMB - Find all Components
#
##########################################################################################


def pattern_match_All():
	xpos = 0				#component position array index
	ypos = 1
	height = 0
	width = 1

	#print('Before VideoCapture')
	#cam = cv2.VideoCapture(1)
	cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)			#jmb 2/24/23 much much faster!
	#print('After VideoCapture')
	cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
	while True:
		##########################################################################
		#
		#			JMB - 2/23/23 Grab the live part image to use when looking for components
		#
		####################################################################
		#print('Before cam.read')
		ret_val, live_img = cam.read()
		#print('After cam.read')
		#############################################################################
		#
		#			Loop through all the saved image files
		#
		##############################################################################

		#while True:
		for i in onlyfiles:
			#pattern = cv2.imread(mypath + "/" + i, 1)  # read a component file

			componentfile = mypath + "/" + i
			print('Name to Process = ', componentfile)

			component_image = cv2.imread(componentfile)

			#############################################################################
			#
			#			Call GetComponentXYFromFile(componentfile) to get the component X,Y
			#			from the filename
			#
			############################################################################
			componentposition =GetComponentXYFromFile(componentfile)
			#print('From Function ComponentXLocation = ', componentposition[0])
			#print('From Function ComponentYLocation = ', componentposition[1])


			show_mask = True
			zoom = False
			show_regions = True
			if (show_mask):
				################################################################################
				#
				#			Read the original saved image file from when we taught the components
				#			Eventually we want to use the live image
				############################################################################
				if (use_camera):
					saved_image = live_img
				else:
					savedfile = mypath + r'\original image\saved_image.jpg'
					saved_image = cv2.imread(savedfile)
					cv2.waitKey(300)			#delay 300 msecs for viewing

				x = componentposition[xpos]
				y = componentposition[ypos]


				height, width = saved_image.shape[0:2]

				##################################################################################
				#
				#				Get the component X,Y Position from the file
				#
				###############################################################################
				componentposition = GetComponentXYFromFile(componentfile)

				##################################################################################
				#
				#				Get the component Dimensions(Height, Width) from the file
				#
				###############################################################################
				#componentdimenions = GetComponentDimensionsFromImage(component_image)
				componentdimenions = GetComponentDimensionsFromFile(componentfile)
				component_height, component_width = componentdimenions[0:2]
				print('component_height = ', component_height)
				print('component_width = ', component_width)

				##############################################################################
				##
				##		Create the cropped image from the saved image by taking all the pixels from the
				# 		starting y,x position and adding the component height and width
				###############################################################################
				crop_img = saved_image[componentposition[ypos]:componentposition[ypos] + component_height,
						   componentposition[xpos]:componentposition[xpos] + component_width]

				#cv2.imshow("cropped", crop_img)
				#cv2.waitKey(0)
				#crop_img = cv2.cvtColor(crop_img, cv2.COLOR_RGB2RGBA)

				ch, cw = crop_img.shape[0:2]

				print('cropped image height = ', ch)
				print('cropped image width = ', cw)

				##############################################################################
				##
				##			JMB - Compute error using the Mean Squared Error - MSE Method
				##
				##############################################################################
				err = np.sum((crop_img.astype("float") - component_image.astype("float")) ** 2)
				err /= float(crop_img.shape[0] * crop_img.shape[1])


				print('err = ', err)

				err2 = mae(component_image,crop_img)

				#print('er2 = ', err2)
				######################################################################################
				##
				##			Call FindComponnet and draw a box on the image where we expect it to be
				##			We can uise either a saved_image or the ive image
				##
				#################################################################################
				if err < 8000:
					FindComponent(saved_image,componentfile,GREEN)
					#cv2.waitKey(0)
					#windowname = 'Find Component' + componentfile
					#time.sleep(1)
					#cv2.destroyWindow(windowname)
				else:
					###################################################################################
					#
					#			JMbn 2/23/23 If we fail, Draw a RED box around expected location
					#			and open a new window to show the image we expected to find
					#			Right now we will pause and wait for a key so we can see what happened
					#
					##################################################################################
					FindComponent(saved_image, componentfile, RED)
					component_image = cv2.resize(component_image, (0,0),fx=4,fy=4)
					cv2.imshow("Missing Component", component_image)
					cv2.setWindowProperty('Missing Component', cv2.WND_PROP_TOPMOST, 1)
					cv2.waitKey(0)
					cv2.destroyWindow("Missing Component")

				#time.sleep(1)

		time.sleep(2)				#JMB Debug - delay 2 seconds and repeat so we can test over and over again for ropbustness
		cv2.destroyAllWindows()
	cv2.waitKey(0)
	cv2.destroyAllWindows()




def mae(data, ref):
    mae = 0
    c = 0
    for i in data:
      mae += abs(i-ref)
      c += 1
    return mae / c
#######################################################################################
#
#				Look for the component in the passed component_file and draw a rectangle
#				around the expected position
#
#######################################################################################
def FindComponent(original_image, component_file,color):
	##############################################################################
	#
	#			JMB - 2/21/2023 THISWORKS!
	#
	#############################################################################
	xpos = 0			#position array index
	ypos = 1			#position array index
	height = 0			#dimension array index
	width = 1			#dimension array index

	#for i in onlyfiles:
	#ComponentFile = mypath + '\\304-166.jpg'
	readfile = cv2.imread(component_file)  # read a component file

	height,width = readfile.shape[0:2]
	print('Find Component component height = ',height)
	print('Find Component component width = ',width)


	########################################################################
	#
	#				Draw a RED Rectangle around the image
	#
	#######################################################################
	# Draw the rectangle:
	# Extract the coordinates of the component
	# This is embedded in the saved file name in this format
	# ComponentXLocation-ComponentYLocation

	#############################################################################
	#
	#			Call GetComponentXYFromFile(componentfile) to get the component X,Y
	#			from the filename
	#
	############################################################################
	componentposition =GetComponentXYFromFile(component_file)

	ComponentXLocation = componentposition[xpos]
	ComponentYLocation = componentposition[ypos]

	##################################################################################
	#
	#				Get the component Dimensions(Height, Width) from the file
	#
	###############################################################################
	componentdimenions = GetComponentDimensionsFromFile(component_file)
	component_height, component_width = componentdimenions[0:2]
	print('component_height = ', component_height)
	print('component_width = ', component_width)

	#ComponentRows = 163
	#ComponentCols = 117

	##################################################################################
	#
	#				Build the rectangle
	#				xStart = xposition
	#				xEnd = xStart + component width
	#				yStart = yposition
	#				yEnd = yStart + component height
	#
	###############################################################################
	# Step 3: Draw the rectangle on large_image
	xStart = ComponentXLocation
	xEnd = xStart + component_width
	yStart = ComponentYLocation
	yEnd = yStart + component_height

	###################################################################################
	#
	#		Draw the rectangle around the expected location on the image and show it
	#
	#############################################################################
	#windowname = 'Find Component' + component_file
	windowname = 'Find Component'

	##########################################################################################
	##
	##					JMB	- Set the Window name based on if we are using the webcam(Live Mode)
	##					or reading the master image from a file(Si,uate Mode)
	##
	##
	####################################################################################
	if (use_camera):
		windowname += ' - Live Mode'
	else:
		windowname += '  - Simulate Mode'

	cv2.rectangle(original_image, (xStart, yStart), (xEnd, yEnd), color, 2)

	#cv2.imshow('Find Component', original_image)
	cv2.imshow(windowname, original_image)


	#############################################################################
	#
	#			Display as topmost window for 100ms
	#
	#########################################################################ggg

	cv2.setWindowProperty(windowname, cv2.WND_PROP_TOPMOST, 1)
	cv2.waitKey(100)


#########################################################################
#
#		Get the component X,Y Location and send back the array
#
#######################################################################
def GetComponentXYFromFile(componentfile):
	positionarray = [0,0]
	xpos = 0
	ypos = 1

	pre = (componentfile.split('.', 1))[0]
	loc = pre.replace(mypath, '')
	loc = loc.replace('\\', '')
	loc = loc.replace('/', '')

	print('loc= ',loc)

	positionarray[xpos] = int((loc.split('-', -1))[xpos])
	positionarray[ypos] = int((loc.split('-', -1))[ypos])
	return positionarray

def GetComponentDimensionsFromImage(component_image):
	dimensionarray = [0, 0]
	height = 0  # array index
	width = 1  # array index
	dimensionarray[height],dimensionarray[width] = component_image.shape[0:2]
	return dimensionarray
	#component_height, component_width = component_image.shape[0:2]


def GetComponentDimensionsFromFile(componentfile):
	#componentfile = mypath + '\\304-166.jpg'
	height = 0			#array index
	width = 1			#array index
	dimensionarray = [0, 0]
	component_image = cv2.imread(componentfile)
	dimensionarray[height],dimensionarray[width] = component_image.shape[0:2]
	return dimensionarray

######################################################################################
#
#			Debug Code
#
######################################################################################
def DebugStuff():
	# load the original input image and display it to our screen
	maskfile = "c:\\Aoi\\Files\\Mask1.jpg"
	original_image = cv2.imread(maskfile)
	cv2.imshow("Original", original_image)

	# height, width = np.array(image).shape

	# a mask is the same size as our image, but has only two pixel
	# values, 0 and 255 -- pixels with a value of 0 (background) are
	# ignored in the original image while mask pixels with a value of
	# 255 (foreground) are allowed to be kept

	mask = np.zeros(original_image.shape[:2], dtype="uint8")
	# cv2.rectangle(mask, (0, 90), (290, 450), 255, -1)

	# cv2.rectangle(mask, (304, 166), (290,450), 255, -1)

	width = 420
	height = 325
	xpos = 304
	ypos = 166
	cv2.rectangle(mask, (304, 166), (width, height), 255, -1)
	# cv2.rectangle(mask, (304, 166), (163, 117), 255, -1)
	# cv2.rectangle(mask, (304, 166), (117, 163), 255, -1)

	# cv2.rectangle(mask, (117, 163), (304, 166),  255, -1)

	cv2.imshow("Rectangular Mask", mask)

	# apply our mask -- notice how only the person in the image is
	# cropped out
	masked = cv2.bitwise_and(original_image, original_image, mask=mask)
	cv2.imshow("Mask Applied to Image", masked)

	###############################################################
	#
	#				Resize
	#
	################################################################

	# resized_frame = imutils.resize(original_image, width=320)
	# resized_image = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2RGBA)

	# cv2.imshow('resize', resized_image)

	##############################################################################
	#
	#			JMB - 2/21/2023 THIS WORKS!
	#
	#############################################################################
	component_file = mypath + '//304-166.jpg'

	FindComponent(original_image, component_file,BLUE)
	cv2.waitKey(0)

	# Draw the rectangle:
	# Extract the coordinates of the component
	# This is embedded in the saved file name in this format
	# ComponentXLocation-ComponentYLocation

	ComponentXLocation = 304
	ComponentYLocation = 166

	# Step 2: Get the size of the template. This is the same size as the match.
	# trows, tcols = small_image.shape[:2]
	ComponentRows = 163
	ComponentCols = 117

	# Step 3: Draw the rectangle on large_image
	cv2.rectangle(original_image, (ComponentXLocation, ComponentYLocation),
				  (ComponentXLocation + ComponentCols, ComponentYLocation + ComponentRows), (0, 0, 255), 2)

	# Display the original image with the rectangle around the match.
	cv2.imshow('new output', original_image)

	# The image is only displayed if we call this
	cv2.waitKey(0)



#############################################################################################
#
#			Match Pattern - OLD
#
##########################################################################################


def pattern_match_old(img):
	xpos = 0				#componentposition rray index
	ypos = 1
	height = 0
	width = 1
	#############################################################################
	#
	#			Loop through all the saved image files
	#
	##############################################################################
	for i in onlyfiles:
		pattern = cv2.imread(mypath+"/"+i,1)				#read a component file
		patterns.append(cv2.cvtColor(pattern,cv2.COLOR_RGB2RGBA))

		componentdimenions = GetComponentDimensionsFromImage(pattern)
		#component_height, component_width = componentdimenions[0:2]

		pre = (i.split('.',1))[0]
		rectparts = pre.split('-')
		rectparts.append(componentdimenions[width])
		rectparts.append(componentdimenions[height])

		regions.append(rectparts)
		###################################################################
		##
		##			This should extract the image height and width from the file
		##
		###################################################################
		print('File Name = ',mypath+"/"+i)
		componentfile = mypath + "/" + i
		print('Component File Name = ', componentfile)

		#print ('File Height = ',h)
		#print('File Width = ', w)

		print('Comp File Height = ', componentdimenions[height])
		print('Comp File Width = ', componentdimenions[width])

	#while True:
	for i in onlyfiles:
		#pattern = cv2.imread(mypath + "/" + i, 1)  # read a component file

		componentfile = mypath + "/" + i
		print('Name to Process = ', componentfile)

		####################################################################################
		#
		#			Grab Image from Camera
		#
		####################################################################################
		#ret_val, img = cam.read()


		################################################################################
		##
		##		Right now we will fix the name of the component file, but eventually
		#		we want this aut-generated
		##
		################################################################################
		#componentfile =  mypath + '\\304-166.jpg'

		#componentfile =  mypath + '\\304-166.jpg'
		component_image = cv2.imread(componentfile)

		#############################################################################
		#
		#			Call GetComponentXYFromFile(componentfile) to get the component X,Y
		#			from the filename
		#
		############################################################################
		componentposition =GetComponentXYFromFile(componentfile)
		print('From Function ComponentXLocation = ', componentposition[0])
		print('From Function ComponentYLocation = ', componentposition[1])

		#rectparts = pre.removeprefix(mypath + '\\')
		#rectparts2 = rectparts.split('-')

		#h, w = pattern.shape[0:2]
		#print('Component Location X = ', h)
		#print('Component Location Y = ', w)


		#print('RectParts2 = ',rectparts2)

		#original_image = cv2.imread(maskfile)
		#cv2.imshow("MaskOriginal", component_image)

		# height, width = np.array(image).shape

		# a mask is the same size as our image, but has only two pixel
		# values, 0 and 255 -- pixels with a value of 0 (background) are
		# ignored in the original image while mask pixels with a value of
		# 255 (foreground) are allowed to be kept

		#mask = np.zeros(mask_image.shape[:2], dtype="uint8")

		show_mask = True
		zoom = False
		show_regions = True
		if (show_mask):
			################################################################################
			#
			#			Read the original saved image file from when we taught the components
			#			Eventually we want to use the live image
			############################################################################
			savedfile = mypath + '\\original image\\saved_image.jpg'
			saved_image = cv2.imread(savedfile)

			######################################################################################
			##
			##			Call FindComponnet and draw a box on the image where we expect it to be
			##			For now we will use the saved_image, but we really want the live image
			##
			#################################################################################
			FindComponent(saved_image,componentfile)
			##################################################################################
			#
			#			Crop out everything except where we expect the currrent component
			#
			####################################################################################

			#ComponentXLocation = 304  # from file name
			#ComponentYLocation = 166  # from component file name


			#ComponentXLocation,ComponentYLocation = componentposition[0:2]

			x = componentposition[xpos]
			y = componentposition[ypos]

			height, width = saved_image.shape[0:2]
			print('Saved Circuit Height = ', height)
			print('Saved Circuit Width = ', width)


			###############################################################################
			##
			##			JMB - Extract the component we are comparing from the passed component image file
			##
			#############################################################################
			#component_height,component_width = component_image.shape[0:2]
			#print('component_height = ', component_height)
			#print('component_width = ', component_width)
			#h = 163			# extracted from file
			#w = 117			# extracted from file

			##################################################################################
			#
			#				Get the component X,Y Position from the file
			#
			###############################################################################
			componentposition = GetComponentXYFromFile(componentfile)

			##################################################################################
			#
			#				Get the component Dimensions(Height, Width) from the file
			#
			###############################################################################
			#componentdimenions = GetComponentDimensionsFromImage(component_image)
			componentdimenions = GetComponentDimensionsFromFile(componentfile)
			component_height, component_width = componentdimenions[0:2]
			print('component_height = ', component_height)
			print('component_width = ', component_width)

			#h = component_height
			#w = component_width


			##############################################################################
			##
			##		Create the cropped image from the saved image by taking all the pixels from the
			# 		starting y,x position and adding the component height and width
			###############################################################################
			crop_img = saved_image[componentposition[ypos]:componentposition[ypos] + component_height,
					   componentposition[xpos]:componentposition[xpos] + component_width]
			#crop_img = saved_image[y:y + h, x:x + w]


			#cv2.imshow("cropped", crop_img)
			#cv2.waitKey(0)
			#crop_img = cv2.cvtColor(crop_img, cv2.COLOR_RGB2RGBA)

			ch, cw = crop_img.shape[0:2]

			print('cropped image height = ', ch)
			print('cropped image width = ', cw)

			##############################################################################
			##
			##			JMB - Compute error using the Mean Squared Error - MSE Method
			##
			##############################################################################
			err = np.sum((crop_img.astype("float") - component_image.astype("float")) ** 2)
			err /= float(crop_img.shape[0] * crop_img.shape[1])
			print('err = ', err)

			#crop_img = img[y, x]

			#difference = cv2.subtract(crop_img, component_image)
			#dif = ImageChops.difference(crop_img, component_image)

			#dif = crop_img.im.chop_difference(component_image.im)
			#print('difference = ', dif)
			#diff_image = cv2.bitwise_and(crop_img, component_image, mask=None)

			#cv2.imshow("diff", diff_image)
			#cv2.waitKey(0)
			#print('Diff = ',diff)


			diff = cv2.bitwise_and(img, img, mask=None)

			#print('Diff = ',diff)

			#diff = cv2.bitwise_and(img,img,mask=mask_inv)
			for i in range(len(patterns)):
				sub = img[(int)(regions[i][1])-10:(int)(regions[i][1])+(int)(regions[i][3])+10,(int)(regions[i][0])-10:(int)(regions[i][0])+(int)(regions[i][2])+10]

				if (show_regions==True):
					cv2.rectangle(diff,((int)(regions[i][0])-10,(int)(regions[i][1])-10), ((int)(regions[i][2])+(int)(regions[i][0])+10,(int)(regions[i][3])+(int)(regions[i][1])+10), (0,255,0), 1)


				#res = cv2.matchTemplate(sub,patterns[i],cv2.TM_CCOEFF_NORMED)
				res=.79

				h,w = patterns[i].shape[0:2]
				threshold = 0.80
				loc = np.where (res >= threshold)
				for pt in zip(*loc[::-1]):
					cv2.rectangle(diff,(pt[0]+(int)(regions[i][0])-10,pt[1]+(int)(regions[i][1])-10), (pt[0] + (int)(regions[i][0])+w-10, pt[1]+(int)(regions[i][1])+h-10), (0,0,0), -1)
					cv2.rectangle(diff,drag_start, drag_end, (255,0,0), 1)
			if (zoom):
				sub = img[320:454,544:680]
				resized_image = cv2.resize(sub, (0,0),fx=4,fy=4)
				diff[119:655,340:884] = resized_image
			else:
				diff = img
				cv2.imshow('John B AOI diff', diff)
				cv2.waitKey(0)
	cv2.destroyAllWindows()



#############################################################################
#
#				JMb - End Debug Stuff
#
###########################################################################


def main():
	#while True:
	show_webcam()
	#time.sleep(3)

if __name__ == '__main__':
	main()