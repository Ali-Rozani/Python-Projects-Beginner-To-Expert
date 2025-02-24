import os
import cv2
import face_recognition
from deepface import DeepFace

# Load known images and encode them
def load_known_faces(images_folder):
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(images_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(images_folder, filename)
            image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(image)[0]  # Encode the first face found
            known_face_encodings.append(face_encoding)
            known_face_names.append(os.path.splitext(filename)[0])  # Use the filename as the name
    return known_face_encodings, known_face_names

# Initialize the webcam
def start_webcam(known_face_encodings, known_face_names):
    video_capture = cv2.VideoCapture(0)  # 0 for default webcam

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Convert the frame from BGR (OpenCV) to RGB (face_recognition)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare the face with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            emotion = "Unknown"

            # If a match is found, use the name of the known face
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

                # Crop the face for emotion detection
                face_image = frame[top:bottom, left:right]
                try:
                    emotion_result = DeepFace.analyze(face_image, actions=['emotion'], enforce_detection=False)
                    emotion = emotion_result[0]['dominant_emotion']
                except Exception as e:
                    print(f"Error in emotion detection: {e}")

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Display the name and emotion
            label = f"{name} - {emotion}"
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Display the resulting frame
        cv2.imshow('Face Recognition', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    video_capture.release()
    cv2.destroyAllWindows()

# Main function
def main():
    images_folder = "Images"  # Folder containing known images
    known_face_encodings, known_face_names = load_known_faces(images_folder)
    start_webcam(known_face_encodings, known_face_names)

if __name__ == "__main__":
    main()
