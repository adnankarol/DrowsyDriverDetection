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
import time
import os

from graphical_analysis import plot_ear_graph
from graphical_analysis import plot_mar_graph

# Define the Path to the Config File
path_to_config_file = "config.json"

"""
Function to load config parameters
"""
def config_params():

    with open(path_to_config_file, 'r') as f:
        config = json.load(f)
    
    EAR_threshold = config["EAR_threshold"]
    MAR_threshold = config["MAR_threshold"]
    number_of_frames = config["number_of_frames"]
    number_of_yawns = config["number_of_yawns"]
    number_of_frames_yawns = config["number_of_frames_yawns"]
    plot_graph_parameter = config["plot_graph_parameter"]

    return EAR_threshold, MAR_threshold, number_of_frames, number_of_yawns, number_of_frames_yawns, plot_graph_parameter


"""
Function to Calculate the EAR of an eye
"""
def eye_aspect_ratio(eye):

	# Euclidean distance between the two sets of vertical coordinates
	EAR1 = distance.euclidean(eye[1], eye[5])
	EAR2 = distance.euclidean(eye[2], eye[4])

	# Euclidean distance between the sets of horizontal coordinates
	EAR3 = distance.euclidean(eye[0], eye[3])

	EAR = (EAR1 + EAR2) / (2.0 * EAR3)

	return EAR


"""
Function to Calculate the MAR of the mouth
"""
def mouth_aspect_ratio(mouth):

    # Euclidean distance between the three sets of vertical coordinates
    MAR1 = distance.euclidean(mouth[13], mouth[19])
    MAR2 = distance.euclidean(mouth[14], mouth[18])
    MAR3 = distance.euclidean(mouth[15], mouth[17])

    # Euclidean distance between the sets of horizontal coordinates
    MAR4 = distance.euclidean(mouth[12], mouth[16])

    MAR = (MAR1 + MAR2 + MAR3) / (3.0 * MAR4)

    return MAR


"""
Driver Function
"""
def driver_sleep_detector():

    EAR_threshold, MAR_threshold, number_of_frames, number_of_yawns, number_of_frames_yawns, plot_graph_parameter = config_params()

    # dlib based face detection
    detect = dlib.get_frontal_face_detector()
    predict = dlib.shape_predictor("dlib_models\shape_predictor_68_face_landmarks.dat")
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
    (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["mouth"]

    # Using my seconday camera, hence 1. If you want to use primary camera enter 0
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    blink_counter = 0
    yawns_counter = 0
    yawns_frame_starter = 0
    yawns_frame_counter = 0
    EAR_list = list()
    MAR_list = list()

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
            mouth = shape[mStart:mEnd]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            # For EAR take Average of both eyes
            EAR = (leftEAR + rightEAR) / 2.0
            MAR = mouth_aspect_ratio(mouth)

            try:
                EAR_list.append(EAR)
            except:
                pass

            try:
                MAR_list.append(MAR)
            except:
                pass

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (255, 0, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (255, 0, 0), 1)

            mouth = cv2.convexHull(mouth)
            cv2.drawContours(frame, [mouth], -1, (255, 0, 0), 1)

            if EAR < EAR_threshold:
                blink_counter = blink_counter + 1
                if blink_counter >= number_of_frames:
                    cv2.putText(frame, "*************ALERT! You Eyes are Closed !!!*************", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    print("ALERT !!!")
            else:
                blink_counter = 0

            if MAR > MAR_threshold:
                yawns_counter = yawns_counter + 1
                yawns_frame_starter = yawns_frame_starter + 1
                # Since a yawn can last for about a certain amount of seconds
                time.sleep(2)
                if yawns_counter >= number_of_yawns and yawns_frame_counter <= number_of_frames_yawns :
                    cv2.putText(frame, "*************WARNING! You are feeling Sleepy !!!*************", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    print("WARNING !!!")
                    yawns_frame_starter = 0
                    yawns_frame_counter = 0
                    number_of_yawns = 0
            if yawns_frame_starter != 0:
                yawns_frame_counter = yawns_frame_counter + 1

        # Display the frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            # Before Shutting Off, Save Plot of EAR and MAR for analyis: not needed for production code (set plot_graph_parameter to 0)
            if plot_graph_parameter:
                EAR_graph_status = plot_ear_graph(EAR_list)
                MAR_graph_status = plot_mar_graph(MAR_list)
            break

    # When everything done, close the video
    cap.release()
    cv2.destroyAllWindows()

    # Clean the Root Folder
    try:
        print("Cleaning Root Directory")
        os.rmdir("__pycache__")
    except:
        pass



if __name__ == '__main__':
    driver_sleep_detector()