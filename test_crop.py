import cv2

def crop_image(image, top_left_point, bottom_right_point):

    print("Cropped image:")
    print("y:", top_left_point[1], bottom_right_point[1])
    print("x", top_left_point[0], bottom_right_point[0])
    cropped_image = image[top_left_point[1]:bottom_right_point[1], top_left_point[0]:bottom_right_point[0]]
    return cropped_image

def mouse_callback(event, x, y, flags, param):
    global drawing, top_left_pt, bottom_right_pt, img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        top_left_pt = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        bottom_right_pt = (x, y)
        img_copy = frame.copy()  # Reset img_copy to the original frame
        cv2.rectangle(img_copy, top_left_pt, bottom_right_pt, (0, 255, 0), 2)
        cv2.imshow("Select ROI", img_copy)

        test = crop_image(frame, top_left_pt, bottom_right_pt)
        cv2.imshow("Preview", test)
    
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        img_copy = frame.copy()  # Reset img_copy to the original frame
        cv2.rectangle(img_copy, top_left_pt, (x, y), (0, 255, 0), 2)
        cv2.imshow("Select ROI", img_copy)
        

if __name__ == "__main__":
    video_capture = cv2.VideoCapture('./media/Les Aristochats - Gammes et arpèges (piano facile).mp4')
    video_capture.set(cv2.CAP_PROP_POS_FRAMES,120)
    ret, frame = video_capture.read()
    img_copy = frame.copy()
    drawing = False
    top_left_pt, bottom_right_pt = (-1, -1), (-1, -1)

    cv2.namedWindow("Select ROI")
    cv2.setMouseCallback("Select ROI", mouse_callback)

    while True:
        cv2.imshow("Select ROI", img_copy)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            cropped_image = crop_image(frame, *top_left_pt, *bottom_right_pt)
            cv2.imshow("Cropped Image", cropped_image)
            break

        elif key == 27:
            break

    cv2.destroyAllWindows()
    video_capture.release()
