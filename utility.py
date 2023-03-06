# Get component XY and return the array
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
