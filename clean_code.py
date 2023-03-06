from matplotlib import pyplot as plt
from os.path import isfile, join
from PIL import ImageChops
from utility import *
from os import listdir
import imutils as imutils
import numpy as np
import time
import cv2
import re

global mypath, onlyfiles, original_image # files
global drag, drag_start, drag_end, save_drag_end, save_drag_start # rectangle drawing
global RED, BLUE, GREEN # color components

# TODO component dimension extraction function -> all in one, no more indexing. 
# TODO Something weird going on with the paths, 
	# " c:\AOI\Files/407-86.jpg " 
	# Why different slashes? I will clean this up.
	# If we dont access the files directly through a directory library (we probably should)
	# We should at least make it consistent and language agnostic

#TODO I think if we are already storing the metadata for the components in the file name
#  we should consider packaging the dimensions also so that we dont have to open the file multiple times to get the dimensions
# Optionally, we could also change the getdimensions function to take a dense array, which is how cv2 reads its files already.
# that way we can opent the image once when we are about to use it and then get all the info we need immediately. Just a thought

# This sets the configurations of the changeable settings. 
# Need to collect these in one place to make it easier to 
# edit in the GUI
def set_configuration():
    user_config() # Variables we change (use_camera, teach_components, etc)
    file_config() # Source files #TODO file paths should come from a config or environment file
    color_config() # Color configuration, stuff that is unlikely to ever change
    drag_config() # Initialization for the rectangle drag components
    misc_config() # this initializes variables whose purpose I haven't figured out yet

# These are the things a user, or us for development, will set.
def user_config():
	global teach_components, use_camera, align_camera
	teach_components = False
	use_camera = False  
	align_camera = False #TODO implement camera alignment

# Sets the directory and the files within
def file_config():
    global mypath, onlyfiles, original_image
    mypath="c:\AOI\\Files"
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    original_image = r"C:\AOI\Files\original image\saved_image.jpg" 

# Sets RGB color values
def color_config():
	global RED, GREEN, BLUE
	RED=(0,0,255)
	BLUE=(255,0,0)
	GREEN=(0,255,0)

# Sets variables needed for rectangle drawing
def drag_config():
	global drag, drag_start, drag_end, save_drag_start, save_drag_end
	drag = False
	drag_start = (0,0)
	drag_end = (0,0)
	save_drag_start = (0,0)
	save_drag_end = (0,0)
def misc_config():
	global patterns, regions, show_regions, show_mask
	patterns = []
	regions = []
	show_regions = False
	show_mask = True


def show_webcam():
	global drag_start, drag_end, img, patterns, regions, show_regions, show_mask, save_drag_start, save_drag_end
	print('teach_components = ',teach_components)
	if teach_components == False:
		pattern_match_All()
	else:
		teach()

def example():
    x = 10
# Manually identify the components by dragging 
def teach():
	global drag_start, drag_end, img, patterns, regions, show_regions, show_mask, save_drag_start, save_drag_end

	# Fixed / Implemented so that I can teach it new images from the source file. Before it was just a black screen when teach was true
	if use_camera:
		cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # jmb 2/24/23 much much faster!
		cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
		cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
		ret_val, img = cam.read() #TODO error handling
	else:
		img = cv2.imread(original_image, 1)

	windowname = 'Teach Components'
	cv2.namedWindow(windowname)
	cv2.setMouseCallback(windowname, on_mouse, 0)


	while True:
		# Get image from camera
		if use_camera:
			ret_val, image = cam.read() #TODO error handling
		else:
			image = cv2.imread(original_image, 1)
		# Draw last rectangle
		cv2.rectangle(img=image, pt1=save_drag_start, pt2=save_drag_end, color=BLUE, thickness=2, lineType=8, shift=0)
		cv2.imshow(windowname, image)

		# call waitkey for image to display
		char = chr(cv2.waitKey(1) & 255)
		if cv2.waitKey(33) == ord('q'):
			break

	cv2.destroyAllWindows()


# track mouse buttons and positions for teach routine
def on_mouse(event, x, y, flags, params):
	global drag, drag_start, drag_end, patterns, img, regions, save_drag_start, save_drag_end
	if event == cv2.EVENT_LBUTTONDOWN:
		drag_start = (x, y)
		drag_end = (x, y)
		save_drag_start = (x,y)
		save_drag_end = (x,y)
		drag = True
	elif event == cv2.EVENT_LBUTTONUP:
		drag = False
		drag_end = (x, y)
		save_drag_end = (x, y)
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

			drag_start = (0,0)
			drag_end = (0,0)
	elif event == cv2.EVENT_MOUSEMOVE and drag==True:
		drag_end = (x,y)
		save_drag_end = (x,y)
		print('drag end = ',x,y)

# align routine
def align():
    global drag_start, drag_end, img, patterns, regions, show_regions, show_mask, draw, bSave, save_drag_start, save_drag_end
    
    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # jmb 2/24/23 much much faster!
    cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    ret_val, img = cam.read()

    windowname = 'Alignment'
    cv2.namedWindow(windowname)
    cv2.setMouseCallback(windowname, on_mouse, 0)



    while True:
        # Get image from camera
        ret_val, image = cam.read()

        # Draw last rectangle
        cv2.rectangle(img=image, pt1=save_drag_start, pt2=save_drag_end, color=BLUE, thickness=2, lineType=8, shift=0)
        cv2.imshow(windowname, image)

        # Must call waitkey for display
        char = chr(cv2.waitKey(1) & 255)
        if cv2.waitKey(33) == ord('q'):
            break

    cv2.destroyAllWindows()


# Finding alignment marks to get X-Y offset to accomodate for movement in the board 
def find_alignment_mark():
	xpos = 0				#componentposition array index
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


	cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)			#jmb 2/24/23 much much faster!
 
	cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
	while True:
        # Get live part image to use when looking for components
		ret_val, live_img = cam.read()

        # Loop through all the saved image files
		#while True:
		#for i in onlyfiles:
			#pattern = cv2.imread(mypath + "/" + i, 1)  # read a component file

		#componentfile = mypath + "/" + i

		#"c:\AOI\\Files
		componentfile = mypath + "\\1022-50-Align.jpg"
		print('Alignment File = ', componentfile)

		component_image = cv2.imread(componentfile)

		#cv2.imshow("Reference", component_image)
		#cv2.waitKey(0)
		#component_image = cv2.cvtColor(crop_img, cv2.COLOR_RGB2RGBA)
  
        # get the XY position from filename
		componentposition =GetComponentXYFromFile(componentfile)


		#print('From Function ComponentXLocation = ', componentposition[0])
		#print('From Function ComponentYLocation = ', componentposition[1])

		componentposition=[1022,50]

		print('From Function ComponentXLocation = ', componentposition[0])
		print('From Function ComponentYLocation = ', componentposition[1])

		#componentfile[xpos] = 1022
		#componentfile[ypos] = 50

		show_mask = True
		
		show_regions = True
		if (show_mask):
            # Read original saved image file from when we taught the components
            # TODO: use live image instead
			if (use_camera):
				saved_image = live_img
			else:
				savedfile = mypath + '\\original image\\saved_image.jpg'
				saved_image = cv2.imread(savedfile)
				cv2.waitKey(300)			#delay 300 msecs for viewing

			x = componentposition[xpos]
			y = componentposition[ypos]


			height, width = saved_image.shape[0:2]

			#componentposition = GetComponentXYFromFile(componentfile)
			#componentdimensions = GetComponentDimensionsFromImage(component_image)
   
			componentdimensions = GetComponentDimensionsFromFile(componentfile)
			component_height, component_width = componentdimensions[0:2]

			component_height = 24		#debug just set
			component_width = 25

			c_xpos = componentposition[xpos] + offsetx
			c_ypos = componentposition[ypos] + offsety

			print('c_xpos = ', c_xpos)

            # creates a cropped image from the saved image from the xy position and adding the height and width
            # TODO: Make this into a separate function
            
			#crop_img = saved_image[componentposition[ypos]:componentposition[ypos] + component_height,
					   #componentposition[xpos]:componentposition[xpos] + component_width]

			crop_img = saved_image[c_ypos:c_ypos + component_height,c_xpos:c_xpos + component_width]

			ch, cw = crop_img.shape[0:2]

            # Compute error using MSE
			err = np.sum((crop_img.astype("float") - component_image.astype("float")) ** 2)
			err /= float(crop_img.shape[0] * crop_img.shape[1])

			print('err = ', err)

			xStart = c_xpos
			xEnd = xStart + component_width
			yStart = c_ypos
			yEnd = yStart + component_height
   
   
			windowname = 'Find Component'
			if(use_camera):
				windowname+=' Live Mode'
			else:
				windowname += ' Simulate Mode'
    
    
            # Draw rectangle around the expected location on the image and show it
            # TODO: Lets see if we can get this into its own function.
            # TODO: if else instead of this 
			color = GREEN
			if err > 8000:
				color = RED
			cv2.rectangle(saved_image, (xStart, yStart), (xEnd, yEnd), color, 2)

			# cv2.imshow('Find Component', original_image)
			cv2.imshow(windowname, saved_image)

			# component_file

            # Display as topmost winow for 100ms
			cv2.setWindowProperty(windowname, cv2.WND_PROP_TOPMOST, 1)
			cv2.waitKey(100)

			print('offset x = ',offsetx)
			print('offset y = ', offsety)
			print('offset = ', offset)
			print('Direction = ', direction)

            # I don't know what this does, but it can probably be streamlined
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
cv2.waitKey(0)
cv2.destroyAllWindows()


# Find all components
def pattern_match_All():
	global original_image
    # component position array index
	xpos = 0
	ypos = 1
	height = 0
	width = 1

	cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)			#jmb 2/24/23 much much faster!
 
	cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
 
	while True:
        # get live part image to use when looking for components
		ret_val, live_img = cam.read()

        # Loop through all the saved image files
		for i in onlyfiles:
			componentfile = mypath + "/" + i
   
			print('Name to Process = ', componentfile)
			
			# Grabs the saved component image which we will check against the live feed / original image 
			component_image = cv2.imread(componentfile)

			# The image file saves its own location in its name
			componentposition =GetComponentXYFromFile(componentfile)

			show_mask = True
			
			show_regions = True
			if (show_mask):
				# Read the original saved image file from when we taught the components
				# TODO use live image instead
				if (use_camera):
					saved_image = live_img
				else:
					saved_image = cv2.imread(original_image)
					#delay 300 msecs for viewing
					cv2.waitKey(300)

				# these are the positions we pulled from the 
				x = componentposition[xpos]
				y = componentposition[ypos]


				height, width = saved_image.shape[0:2]


				componentposition = GetComponentXYFromFile(componentfile)
				#componentdimensions = GetComponentDimensionsFromImage(component_image)
				componentdimensions = GetComponentDimensionsFromFile(componentfile)
				component_height, component_width = componentdimensions[0:2]
				print('component_height = ', component_height)
				print('component_width = ', component_width)

				crop_img = saved_image[y:(y + component_height), x:(x + component_width)]

				#cv2.imshow("cropped", crop_img)
				#cv2.waitKey(0)
				#crop_img = cv2.cvtColor(crop_img, cv2.COLOR_RGB2RGBA)

				croppedheight, croppedwidth = crop_img.shape[0:2]

				print('cropped image height = ', croppedheight)
				print('cropped image width = ', croppedwidth)

                # Compute MSE error TODO functionize
				err = mean_squared_error(crop_img, component_image)
				# err2 = np.sum((crop_img.astype("float") - component_image.astype("float")) ** 2)
				# err2 /= float(crop_img.shape[0] * crop_img.shape[1])
				# print("error function working properly: {eq}".format(eq= err == err2))

				print('err = ', err)

				# Mean Absolute Error, not sure what this is doing here
				# err2 = mae(component_image,crop_img)

                # Call FindComponent and draw a box on the image where we expect it to be
                # We can use either a saved image or the live image
				if err < 8000:
					FindComponent(saved_image,componentfile,GREEN)
					#cv2.waitKey(0)
					#windowname = 'Find Component' + componentfile
					#time.sleep(1)
					#cv2.destroyWindow(windowname)
				else:

                    # On Failure draw a RED box around the expected location and open a new window to show the image we expect
                    # Then Pause and wait for a key press so we can see what happened
					FindComponent(saved_image, componentfile, RED)
					component_image = cv2.resize(component_image, (0,0),fx=4,fy=4)
					cv2.imshow("Missing Component", component_image)
					cv2.setWindowProperty('Missing Component', cv2.WND_PROP_TOPMOST, 1)
					cv2.waitKey(0)
					cv2.destroyWindow("Missing Component")
        #JMB Debug - delay 2 seconds and repeat so we can test over and over again for ropbustness
		time.sleep(2)				
		cv2.destroyAllWindows()
  # TODO fix indentation and make this code reachable
	cv2.waitKey(0)
	cv2.destroyAllWindows()



# I don't know what this code does, it doesn't seem to be called
def mae(data, ref):
    mae = 0
    c = 0
    for i in data:
      mae += abs(i-ref)
      c += 1
    return mae / c

# Look for the component in the passed component_file and draw a rectangle around the expected position
def FindComponent(original_image, component_file,color):

	xpos = 0			#position array index
	ypos = 1			#position array index
	height = 0			#dimension array index
	width = 1			#dimension array index

	readfile = cv2.imread(component_file)  # read a component file

	height,width = readfile.shape[0:2]
	print('Find Component component height = ',height)
	print('Find Component component width = ',width)

    # TODO rearrange if no effect
	# TODO Can load direct rather than save as a list and extract
	componentposition = GetComponentXYFromFile(component_file)

	ComponentXLocation = componentposition[xpos]
	ComponentYLocation = componentposition[ypos]
 
	componentdimensions = GetComponentDimensionsFromFile(component_file)
	component_height, component_width = componentdimensions[0:2]
	print('component_height = ', component_height)
	print('component_width = ', component_width)

    # TODO lets make a rectangle class / struct so we don't have to do this every time
	xStart = ComponentXLocation
	xEnd = xStart + component_width
	yStart = ComponentYLocation
	yEnd = yStart + component_height


	windowname = 'Find Component'

    # Set window name base on live mode vs main image mode
	if (use_camera):
		windowname += ' - Live Mode'
	else:
		windowname += '  - Simulate Mode'

	cv2.rectangle(original_image, (xStart, yStart), (xEnd, yEnd), color, 2)

	cv2.imshow(windowname, original_image)

    # Display as topmost window for 100 ms
	cv2.setWindowProperty(windowname, cv2.WND_PROP_TOPMOST, 1)
	cv2.waitKey(100)

# Get component XY and return the array
def GetComponentXYFromFile(componentfile):
	temp = re.findall(r'\d+', componentfile)
	return list(map(int, temp))

# TODO Check if this makes any difference between image/file, i suspect it doesn't. I think cv2 represents an image read from a camera the same as it does for file
def GetComponentDimensionsFromImage(component_image):
	dimensionarray = [0, 0]
	height = 0  # array index
	width = 1  # array index
	dimensionarray[height],dimensionarray[width] = component_image.shape[0:2]
	return dimensionarray


def GetComponentDimensionsFromFile(componentfile):
	height = 0			#array index
	width = 1			#array index
	dimensionarray = [0, 0]
	component_image = cv2.imread(componentfile)
	dimensionarray[height],dimensionarray[width] = component_image.shape[0:2]
	return dimensionarray

def mean_squared_error(crop_img, component_image):
	err = np.sum((crop_img.astype("float") - component_image.astype("float")) ** 2)
	err /= float(crop_img.shape[0] * crop_img.shape[1])
	return err


def main():
	set_configuration()
	show_webcam()

if __name__ == '__main__':
	main()
