import cv2

def draw_faces(image_path, faces):
    image = cv2.imread(image_path)
    for face in faces:
        x, y, w, h = (face.left(), face.top(), face.width(), face.height())
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return image
