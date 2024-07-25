import cv2
import dlib

def recognize_faces(image_path):
    detector = dlib.get_frontal_face_detector()
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    return faces
