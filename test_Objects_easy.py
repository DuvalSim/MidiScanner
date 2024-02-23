import cv2
import os

from midi_scanner.utils.preprocessing import get_lower_image
from midi_scanner.utils.visualization import display_pressed_keys
import imutils as imutils
import numpy as np

from midi_scanner.Keyboard import Keyboard
from midi_scanner.NoteRecorder import NoteRecorder
from midi_scanner.NoteWriter import ScoreWriter

from midi_scanner.utils.ImageProcessor import ImageProcessor

import music21 as music

# def get_cropped_image(img):
#     return img[270: img.shape[0] - 3, :,:].copy()


image_processor = ImageProcessor(keyboard_region_y=(244,360), keyboard_region_x=(0,650))



images_dir = "media"
base_img_name = "FirstFrame.png"


# Open the video file
cap = cv2.VideoCapture('./media/Les Aristochats - Gammes et arpèges (piano facile).mp4')

# Check if the video file was successfully opened
if not cap.isOpened():
	print('Error opening video file')

totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
cap.set(cv2.CAP_PROP_POS_FRAMES,120)
ret, first_frame = cap.read()

first_frame = image_processor.get_keyboard_image(first_frame)

cv2.imshow("first frame", first_frame)

keyboard = Keyboard(first_frame, "C3", "c3")



fps = cap.get(cv2.CAP_PROP_FPS)

#cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * 73) + 15)
#ret, current_frame = cap.read()

#current_frame = get_cropped_image(current_frame)
#keyboard.get_pressed_notes(current_frame=current_frame)

#cv2.imshow("current frame", current_frame)

k = cv2.waitKey(0)
cv2.destroyAllWindows()
nb_frame = 1



# ret, current_frame = cap.read()

# current_frame = get_cropped_image(current_frame)
# keyboard.get_pressed_keys(current_frame=current_frame)

# cv2.imshow("current frame", current_frame)

note_recorder = NoteRecorder()

while True:
    # Read the next frame from the video
    ret, frame = cap.read()

    # Check if the frame was successfully read
    if not ret:
        break

    # Process the frame here (e.g. display it)
    cropped_frame = image_processor.get_keyboard_image(frame)
    bot, top = get_lower_image(cropped_frame)
    #cv2.imshow("bot", bot)
    #cv2.imshow("top", top) 

    pressed_keys = keyboard.get_pressed_keys(cropped_frame)
    
    #print(pressed_keys)
    display_pressed_keys(frame, pressed_keys)

    # if nb_frame%1000 == 0:
    #     cv2.waitKey(0)
    
    note_recorder.populate_next_frame(pressed_keys)

    #cv2.waitKey(0)
    #print(nb_frame)
    nb_frame += 1
    # print(nb_frame)
    # if nb_frame > 2300:
    #     k = cv2.waitKey(0)
    
    # Wait for a key press to exit
    if (k == ord('q')) or (nb_frame > 1340):
        cv2.destroyAllWindows()
        break


cap.release()

# Release the video capture object and close all windows

note_recorder.end_recording()

note_recorder.sort_played_notes()

note_recorder.get_starting_frame_histogram()
#note_recorder.round_frames()

# note_recorder.get_starting_frame_histogram()

note_nb_frames = [ played_note.nb_frame for played_note in  note_recorder.get_notes_recorded()]

RYTHM_LENGTH = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3 , 4]

notes_recorded = note_recorder.get_notes_recorded()


    

print(note_nb_frames)

print("wait")

cv2.waitKey(0)

from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import numpy as np
from kneed import KneeLocator

X = np.array(note_nb_frames).reshape(-1,1)

kmeans_kwargs = {
    #"init": "random",
    "n_init": 10,
    "max_iter": 300,
    "random_state": 42,
}

# A list holds the SSE values for each k
sse = []
for k in range(1, 9):
    kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
    kmeans.fit(X)
    sse.append(kmeans.inertia_)

kl = KneeLocator(
    range(1,9), sse, curve="convex", direction="decreasing"
)

plt.plot(range(1,9), sse)
plt.show()

print("Elbow found:",kl.elbow)

kmeans_best = KMeans(n_clusters=5, **kmeans_kwargs)


#kmeans_best = KMeans(n_clusters=4, **kmeans_kwargs)

clusters =kmeans_best.fit_predict(X)
print("clusters:", clusters)
print("centroids:", kmeans_best.cluster_centers_)

rythm_classes = [ round(cluster[0]) for cluster in kmeans_best.cluster_centers_]
print(rythm_classes)
print("FPS ",fps)

print("frames per minute", fps* 60.0)
fpm = fps* 60

print("proposed bpms:", [ fpm / float(rythm_frame) for rythm_frame in rythm_classes ])

bpm = 52

rythm_in_frames = fpm/bpm

base_class_idx = 1

class_factor = [rythm_class / rythm_in_frames for rythm_class in rythm_classes]

rythm_dict = {}
for class_idx, factor in enumerate(class_factor):
    rythm_dict[class_idx] = factor


played_rythms = [ rythm_dict[class_label] for class_label in clusters]
print("class_factor:", class_factor)
print("rythms:", played_rythms)
played_note_list = [ played_note.note for played_note in  note_recorder.get_notes_recorded()]


music.environment.set("lilypondPath", "C:\\Program Files (x86)\\lilypond\\bin\\lilypond.exe")

# music_notes = [
#     ("C4", 0.0, 4.1),  # Example note 1: C4 starting at 0.0 seconds, lasts 2.0 seconds
#     ("E4", 1, 3.02),  # Example note 2: E4 starting at 1.0 second, lasts 1.5 seconds (overlapping)
#     ("G4", 2.01, 2.2)   # Example note 3: G4 starting at 2.0 seconds, lasts 2.0 seconds

# ]

offset = notes_recorded[0].start_frame

# Create a Stream object
stream = music.stream.Stream()

stream.insert(0, music.tempo.MetronomeMark(number=bpm))

def get_closest(duration_raw):
    closest_distance = 10
    rythm_result = None
    for duration_rounded in RYTHM_LENGTH:
        if abs(duration_rounded - duration_raw) < closest_distance:
            rythm_result = duration_rounded
            closest_distance = abs(duration_rounded - duration_raw)
        
    return rythm_result

for note_recorded in notes_recorded:
     
    note = music.note.Note(note_recorded.note)
    
    # Set the duration of the note
    #duration = round(note_recorded.nb_frame / rythm_in_frames,2)
    
    duration = get_closest(note_recorded.nb_frame / rythm_in_frames)
    
    note.duration = music.duration.Duration(duration)

    print(note.duration)
    
    start = round((note_recorded.start_frame - offset) / rythm_in_frames,1)
    # Add the Note object to the Stream
    stream.insert(start, note)

# Show the Stream
fp = stream.write('midi', fp='./test.mid')

stream.show()
#(stream.show('midi')
#for note in notes_recorded:

# note_writer = ScoreWriter()
# note_writer.create_part(played_note_list=played_note_list , played_rythms_list= played_rythms