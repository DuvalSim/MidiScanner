import cv2


def get_lower_image(base_img):
	im_height = base_img.shape[0]
	im_bottom = base_img[int(im_height - (im_height / 5)):im_height, :]
	im_top = base_img[int(im_height/5):int(im_height - (im_height / 4)), :]
	return im_bottom, im_top
