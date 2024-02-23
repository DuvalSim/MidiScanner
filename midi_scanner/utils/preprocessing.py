import cv2

TOP_START_RATIO = 5
TOP_END_RATIO = 2.5

def crop_image(image, top_left_point, bottom_right_point):

	# print("Cropped image:")
	# print("y:", top_left_point[1], bottom_right_point[1])
	# print("x", top_left_point[0], bottom_right_point[0])
	cropped_image = image[top_left_point[1]:bottom_right_point[1], top_left_point[0]:bottom_right_point[0]].copy()
	return cropped_image

def get_lower_image(base_img):
	im_height = base_img.shape[0]
	im_bottom = base_img[int(im_height - (im_height / 3)):im_height, :]
	im_top = base_img[int(im_height/TOP_START_RATIO):int(im_height - (im_height / TOP_END_RATIO)), :]
	return im_bottom, im_top


 