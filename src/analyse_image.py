import numpy as np
import argparse, cv2, sys, os

def resource_path(relative_path):
	"""
	Taken from https://stackoverflow.com/a/49802075
	Resolves an issue with .exe made using PyInstaller
	"""
	if hasattr(sys, '_MEIPASS'):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.abspath("."), relative_path)

def manipulate(lower, upper, image):
	"""
	Crops, and manipulates the color of the image to identify the hitmarker. The image
	is converted to grayscale at the end to make the comparison easier.

	:param lower: A list of ints which define the lower bound of the color (in BGR)
	:param upper: A list of ints which define the upper bound of the color (in BGR)
	:param image: The image to be processed (cv2 object)
	:returns output: The processed image (cv2 object)
	"""
	# create NumPy arrays from the boundaries
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")
	# find the colors within the specified boundaries and apply
	
	mask = cv2.inRange(image, lower, upper) # the mask
	output = cv2.bitwise_and(image, image, mask=mask)

	# Remove the content in the middle of the image, otherwise it will impact the
	# MSE score in an unwanted manner. Hitmarker may be there but the content in the 
	# middle of the image of the same colour could give an inaccurate score
	triangle = np.array([[50, 50 + 50], [50, 50 + 50], [50, 50 - 50], [50 + 50, 50]])
	color = [0, 0, 0]
	cv2.fillConvexPoly(output, triangle, color)
	triangle = np.array([[50, 50 + 50], [50, 50 + 50], [50, 50 - 50], [50 - 50, 50]])
	color = [0, 0, 0]
	cv2.fillConvexPoly(output, triangle, color)
	
	output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

	return output

def compare(expected, img):
	"""
	Compares the expected hitmarker image with the passed image to check whether
	the hitmarker is in the passed image. 

	:param expected: A cv2 object of the image that has the expected hitmarker
	:param img: A cv2 object of the image we want to check for the hitmarker
	:returns Bool, mse_err: Returns whether img has the hitmarker or not, and the MSE score
	"""
	x = int((img.shape[1] - 100) / 2) 
	y = int((img.shape[0] - 100) / 2) 

	h = 100
	w = 100

	image = img[y:y + h, x:x + w] # Crop

	boundaries = [
		([15, 42, 191], [89, 109, 255]),
		([15, 42, 215], [89, 109, 255]),
		([56, 21, 209], [222, 209, 255])
	]

	mse_threshold = 220
	mse_err = 0
	for (lower, upper) in boundaries:
		output = manipulate(lower, upper, image)
		mse_err = mse(expected, output)
		if mse_err < mse_threshold:
			return True, mse_err
	return False, mse_err

def mse(image_a, image_b):
	"""
	Calculate the Mean Squared Error between the two images

	:param image_a: The first image
	:param image_b: The second image
	:returns err: A float
	"""
	err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
	err /= float(image_a.shape[0] * image_a.shape[1])
	return err

def get_expected_result():
	"""
	The expected image of the hitmarker needs to go through the same manipulation
	as the other images for an accurate comparison. I believe it has something to do
	with how the image is structured in the np.array after the manipulatio
	"""
	return manipulate([15, 42, 191], [89, 109, 255], cv2.imread(resource_path("expected.png")))

# if __name__ == "__main__":
# 	# For Debugging
# 	img1 = get_expected_result()
# 	result, score = compare(img1, cv2.imread("hitmarker5.png"))
# 	print(result, score)

