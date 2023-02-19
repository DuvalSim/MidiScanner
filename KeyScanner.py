import cv2

# Open the video file
cap = cv2.VideoCapture('./media/FFX.mp4')

# Check if the video file was successfully opened
if not cap.isOpened():
    print('Error opening video file')

# Loop through each frame in the video
while True:
    # Read the next frame from the video
    ret, frame = cap.read()

    # Check if the frame was successfully read
    if not ret:
        break

    # Process the frame here (e.g. display it)
    cv2.imshow('frame', frame)

    # Wait for a key press to exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
