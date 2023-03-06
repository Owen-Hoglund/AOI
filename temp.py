# Debugging Code
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