import dlib

face_detector = dlib.get_frontal_face_detector()

def recognize_face(image_path):
    image = dlib.load_rgb_image(image_path)
    dets = face_detector(image, 1)
    return [{'left': d.left(), 'top': d.top(), 'right': d.right(), 'bottom': d.bottom()} for d in dets]
