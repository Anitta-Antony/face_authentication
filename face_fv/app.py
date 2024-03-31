import os 
import datetime
import cv2
from flask import Flask,jsonify,request,render_template
import numpy as np
import face_recognition
from flask import redirect, url_for
app = Flask(__name__)

registered_data = {}


registration_status_file = "registration_status.txt"

# Function to read registration status from file
def read_registration_status():
    if os.path.exists(registration_status_file):
        with open(registration_status_file, "r") as file:
            return file.read().strip() == "done"
    return False

# Function to write registration status to file
def write_registration_status(status):
    with open(registration_status_file, "w") as file:
        file.write("done" if status else "not_done")

# Check if registration has been done
registration_done = read_registration_status()

@app.route("/") 
def index():
    if registration_done:
        return redirect(url_for('login'))
    else:
        return render_template("index.html")

@app.route("/register",methods=["POST"])
def register():
    name = request.form.get("name")
    photo = request.files['photo']

    uploads_folder = os.path.join(os.getcwd(),"static","uploads") 

    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)

    global registration_done
    if registration_done:
        return redirect(url_for('login'))

    photo.save(os.path.join(uploads_folder,f'{name}.jpg'))
    registered_data[name] = f"{name}.jpg"

    registration_done = True
    write_registration_status(True)

    response = {"success":True,'name':name}
    return jsonify(response)

@app.route("/login")

def login():

    video_capture = cv2.VideoCapture(0)
    known_face_encodings = []
    known_face_names = []

# Path to the folder containing the images of known faces
    uploads_folder = os.path.join(os.getcwd(),"static","uploads")

# Iterate over files in the uploads folder
    for filename in os.listdir(uploads_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # Load the image file
            image_path = os.path.join(uploads_folder, filename)
            image = face_recognition.load_image_file(image_path)

            # Find face encodings for all faces in the image
            face_encodings = face_recognition.face_encodings(image)

            # Add each face encoding and its corresponding filename to the lists
            for face_encoding in face_encodings:
                known_face_encodings.append(face_encoding)
                known_face_names.append(os.path.splitext(filename)[0])

    print("Known faces loaded successfully.")

    # Now you have the known_face_encodings and known_face_names lists populated with face encodings and their corresponding filenames.

    
    
    face_locations = []
    face_encodings = []
    face_names = []
    s=True
 
 
 
 
    import time  # Import the time module

# Initialize variables for face tracking
    current_user_name = filename
    basename = os.path.basename(current_user_name)
    current_user = os.path.splitext(basename)[0]
    print(current_user)
    user_present_start_time = None
    min_detection_time = 5  # Minimum time (in seconds) for face to be continuously detected

    while True:
        ret, frame = video_capture.read()  # Capture a frame and check if it's successful
        if not ret:
             print("Error: Failed to capture frame from webcam.")
             break
        _, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        if s:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = ""
                face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distance)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    
                if(face_distance[best_match_index]>0.50):
                    return "unsuccesfull"
                # If the detected face is the same as the current user
                if name == current_user:
                    print(current_user)
                    # If user_present_start_time is not set, set it
                    if user_present_start_time is None:
                        user_present_start_time = time.time()
                    # If the face has been continuously detected for more than min_detection_time seconds
                    elif time.time() - user_present_start_time >= min_detection_time:
                        
                        video_capture.release()
                        cv2.destroyAllWindows()
                        user_present_start_time = time.time()
                        print("login succesfully")
                        return redirect(url_for('success', user_name=current_user))
                        
                        # Update the user_present_start_time to track continuous detection
                        
                else:
                    # If a different face is detected, reset the current_user and user_present_start_time
                    return "unsuccesfull"
                   
               
                    
        cv2.imshow("authenticate", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return "Error: Login failed"

        
    

   
@app.route("/success")
def success():
    user_name = request.args.get('user_name')  # Fix: add quotes around 'user_name'
    return render_template("success.html", user_name=user_name)

if __name__ == "__main__":
    app.run(debug=True)