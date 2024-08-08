import cv2
import face_recognition
import sqlite3
import numpy as np
import time
import os
from twilio.rest import Client
import threading

# Twilio configuration
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886'  # Ensure this is in WhatsApp format
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def load_known_faces():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT roll_number, image_path, whatsapp_number FROM students")
    known_faces = cursor.fetchall()
    conn.close()

    face_encodings = []
    face_data = {}

    for roll_number, image_path, whatsapp_number in known_faces:
        if os.path.exists(image_path):
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                face_encodings.append(encoding[0])
                face_data[tuple(encoding[0])] = whatsapp_number

    return face_encodings, face_data

def send_whatsapp_message(to, message):
    to_number = 'whatsapp:' + to
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=to_number
        )
    except Exception as e:
        print(f"Failed to send message: {e}")

def process_faces(frame, known_face_encodings, face_data, line_y, last_sent_time, message_interval, result):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings_in_frame = face_recognition.face_encodings(rgb_frame, face_locations)

    for (face_encoding, (top, right, bottom, left)) in zip(face_encodings_in_frame, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            matched_encoding = known_face_encodings[best_match_index]
            whatsapp_number = face_data[tuple(matched_encoding)]

            if bottom >= line_y:
                current_time = time.time()
                if whatsapp_number not in last_sent_time or (current_time - last_sent_time[whatsapp_number]) >= message_interval:
                    send_whatsapp_message(whatsapp_number, "Your ward has left the campus.")
                    last_sent_time[whatsapp_number] = current_time
                    result.append((left, top, right, bottom))

def main():
    known_face_encodings, face_data = load_known_faces()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    last_sent_time = {}
    message_interval = 1
    frame_count = 0
    result = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        height, width = frame.shape[:2]
        line_y = height - 100
        frame_count += 1

        if frame_count % 15 == 0:
            result.clear()
            process_thread = threading.Thread(target=process_faces, args=(frame, known_face_encodings, face_data, line_y, last_sent_time, message_interval, result))
            process_thread.start()

        for (left, top, right, bottom) in result:
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

        cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 0), 2)
        cv2.imshow('Video Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
