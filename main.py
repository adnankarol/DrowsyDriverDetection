"""
Created on Sat Nov 19 23:21:57 2022
@author = Karol
"""

# Import Dependencies

import json
import cv2
from scipy.spatial import distance
import dlib
from imutils import face_utils
import imutils

from graphical_analysis import plot_ear_graph

# Define the Path to the Config File
path_to_config_file = "config.json"

"""
Function to load config parameters
"""
def config_params():

    with open(path_to_config_file, 'r') as f:
        config = json.load(f)
    
    EAR_threshold = config["EAR_threshold"]
    number_of_frames = config["number_of_frames"]

    return EAR_threshold, number_of_frames


"""
Function to Calculate the EAR of an eye
"""
def eye_aspect_ratio(eye):

	# Euclidean distance between the two sets of vertical coordinates
	EAR1 = distance.euclidean(eye[1], eye[5])
	EAR2 = distance.euclidean(eye[2], eye[4])

	# Euclidean distance between the two sets of horizontal coordinates
	EAR3 = distance.euclidean(eye[0], eye[3])

	EAR = (EAR1 + EAR2) / (2.0 * EAR3)

	return EAR


"""
Function to Calculate the MAR of the mouth
"""
def eye_aspect_ratio(eye):

	# Euclidean distance between the two sets of vertical coordinates
	EAR1 = distance.euclidean(eye[1], eye[5])
	EAR2 = distance.euclidean(eye[2], eye[4])

	# Euclidean distance between the two sets of horizontal coordinates
	EAR3 = distance.euclidean(eye[0], eye[3])

	EAR = (EAR1 + EAR2) / (2.0 * EAR3)

	return EAR


"""
Driver Function
"""
def driver_sleep_detector():

    EAR_threshold, number_of_frames = config_params()

    # dlib based face detection
    detect = dlib.get_frontal_face_detector()
    predict = dlib.shape_predictor("dlib_models\shape_predictor_68_face_landmarks.dat")
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

    # Using my seconday camera, hence 1. If you want to use primary camera enter 0
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    counter = 0
    EAR_list = list()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame. Closing the System ...")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        persons = detect(gray, 0)
        for person in persons:
            shape = predict(gray, person)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            EAR = (leftEAR + rightEAR) / 2.0

            try:
                EAR_list.append(EAR)
            except:
                pass

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (255, 0, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (255, 0, 0), 1)

            if EAR < EAR_threshold:
                counter = counter + 1
                print(counter)
                if counter >= number_of_frames:
                    cv2.putText(frame, "****************ALERT!****************", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    print("ALERT !!!")
            else:
                counter = 0

        # Display the frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            # Before Shutting Off Save Plot of EAR for analyis: not needed for production code
            EAR_graph_status = plot_ear_graph(EAR_list)
            break

    # When everything done, close the video
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    driver_sleep_detector()