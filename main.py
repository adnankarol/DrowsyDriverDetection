__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

# Import Dependencies
import json
import cv2
from scipy.spatial import distance
import dlib
from imutils import face_utils
import imutils
import time
import shutil

from graphical_analysis import plot_ear_graph
from graphical_analysis import plot_mar_graph

# Define the Path to the Config File
PATH_TO_CONFIG_FILE = "config.json"

def load_config():
    """
    Load configuration parameters from the JSON config file.

    Returns:
        tuple: A tuple containing EAR threshold, MAR threshold, number of frames for EAR detection,
               number of yawns to trigger an alert, number of frames to track yawns, and graph plotting parameter.
    """
    with open(PATH_TO_CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    return (
        config["EAR_threshold"],
        config["MAR_threshold"],
        config["number_of_frames"],
        config["number_of_yawns"],
        config["number_of_frames_yawns"],
        config["plot_graph_parameter"]
    )

def calculate_eye_aspect_ratio(eye):
    """
    Calculate the Eye Aspect Ratio (EAR) for a given eye.

    Args:
        eye (array-like): Coordinates of the eye landmarks.

    Returns:
        float: The calculated EAR value.
    """
    EAR1 = distance.euclidean(eye[1], eye[5])
    EAR2 = distance.euclidean(eye[2], eye[4])
    EAR3 = distance.euclidean(eye[0], eye[3])
    return (EAR1 + EAR2) / (2.0 * EAR3)

def calculate_mouth_aspect_ratio(mouth):
    """
    Calculate the Mouth Aspect Ratio (MAR) for a given mouth.

    Args:
        mouth (array-like): Coordinates of the mouth landmarks.

    Returns:
        float: The calculated MAR value.
    """
    MAR1 = distance.euclidean(mouth[13], mouth[19])
    MAR2 = distance.euclidean(mouth[14], mouth[18])
    MAR3 = distance.euclidean(mouth[15], mouth[17])
    MAR4 = distance.euclidean(mouth[12], mouth[16])
    return (MAR1 + MAR2 + MAR3) / (3.0 * MAR4)

def driver_sleep_detector():
    """
    Main function to detect driver drowsiness based on eye and mouth aspect ratios.
    Captures video from the camera and provides alerts based on detected drowsiness.
    """
    EAR_threshold, MAR_threshold, number_of_frames, number_of_yawns, number_of_frames_yawns, plot_graph_parameter = load_config()

    # Initialize dlib face detector and shape predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("dlib_models/shape_predictor_68_face_landmarks.dat")
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
    (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["mouth"]

    # Initialize video capture
    cap = cv2.VideoCapture(1)  # Use 0 for primary camera, 1 for secondary
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    blink_counter = 0
    yawns_counter = 0
    yawns_frame_counter = 0
    single_yawn_event = 0
    EAR_list = []
    MAR_list = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Closing the System...")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 0)

        for face in faces:
            shape = predictor(gray, face)
            shape = face_utils.shape_to_np(shape)

            left_eye = shape[lStart:lEnd]
            right_eye = shape[rStart:rEnd]
            mouth = shape[mStart:mEnd]

            left_EAR = calculate_eye_aspect_ratio(left_eye)
            right_EAR = calculate_eye_aspect_ratio(right_eye)
            EAR = (left_EAR + right_EAR) / 2.0
            MAR = calculate_mouth_aspect_ratio(mouth)

            EAR_list.append(EAR)
            MAR_list.append(MAR)

            # Draw eye and mouth contours on the frame
            left_eye_hull = cv2.convexHull(left_eye)
            right_eye_hull = cv2.convexHull(right_eye)
            cv2.drawContours(frame, [left_eye_hull], -1, (255, 0, 0), 1)
            cv2.drawContours(frame, [right_eye_hull], -1, (255, 0, 0), 1)
            mouth_hull = cv2.convexHull(mouth)
            cv2.drawContours(frame, [mouth_hull], -1, (255, 0, 0), 1)

            # Alert for closed eyes
            if EAR < EAR_threshold:
                blink_counter += 1
                if blink_counter >= number_of_frames:
                    cv2.putText(frame, "ALERT: Eyes Closed!", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    print("ALERT: Eyes Closed!")
            else:
                blink_counter = 0

            # Warning for yawning
            if MAR > MAR_threshold:
                single_yawn_event = 1
            elif MAR < MAR_threshold and single_yawn_event == 1:
                yawns_counter += 1
                if yawns_counter >= number_of_yawns and yawns_frame_counter <= number_of_frames_yawns:
                    cv2.putText(frame, "WARNING: Feeling Sleepy!", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    print("WARNING: Feeling Sleepy!")
                single_yawn_event = 0

            if yawns_counter >= number_of_yawns or yawns_frame_counter >= number_of_frames_yawns:
                yawns_counter = 0
                yawns_frame_counter = 0
            elif yawns_counter != 0:
                yawns_frame_counter += 1

        cv2.imshow('Driver Sleep Detection', frame)
        if cv2.waitKey(1) == ord('q'):
            if plot_graph_parameter:
                plot_ear_graph(EAR_list)
                plot_mar_graph(MAR_list)
            break

    cap.release()
    cv2.destroyAllWindows()

    try:
        print("Cleaning Root Directory")
        shutil.rmtree("__pycache__")
    except FileNotFoundError:
        pass

if __name__ == '__main__':
    driver_sleep_detector()
