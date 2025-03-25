import datetime
import io
import dropbox
import threading
import webbrowser
import base64
import requests
import json
import os

import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

access_token = os.environ['DROPBOX_ACCESS_CODE']

def get_new_token():
    APP_KEY = os.environ['DROPBOX_APP_KEY']
    APP_SECRET = os.environ['DROPBOX_APP_SECRET']
    url = f'https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&' \
        f'response_type=code&token_access_type=offline'

    webbrowser.open(url)
    print("Please copy the access code generated and paste it here: ")
    ACCESS_CODE_GENERATED = input()
    try:
        BASIC_AUTH = base64.b64encode(f'{APP_KEY}:{APP_SECRET}'.encode())

        headers = {
            'Authorization': f"Basic {BASIC_AUTH}",
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = f'code={ACCESS_CODE_GENERATED}&grant_type=authorization_code'

        response = requests.post('https://api.dropboxapi.com/oauth2/token',
                                data=data,
                                auth=(APP_KEY, APP_SECRET))
        new_access_code = json.loads(response.text)['access_token']
        dotenv.set_key(dotenv_file, "DROPBOX_ACCESS_CODE", new_access_code)
        print("Access token saved: ", new_access_code)
        os.environ['DROPBOX_ACCESS_CODE'] = new_access_code
        global access_token
        access_token = new_access_code
        return new_access_code
    except:
        print("Error getting access token")

if not access_token:
    access_token = get_new_token()

# print(access_token)

class UploadData(threading.Thread):
    def __init__(self, txtpath, imgpath, name, txtdata, imgdata, typeofupload,ac):
        threading.Thread.__init__(self)
        self.txtpath = txtpath
        self.imgpath = imgpath
        self.name = name
        self.txtdata = txtdata
        self.imgdata = imgdata
        self.typeofupload = typeofupload
        self.ac = ac

    def append_to_file(self,dropbox_path, new_content,access_token):
        print(access_token)
        dbx = dropbox.Dropbox(access_token)
        try:
            # Download the current content of the file
            _, existing_content = dbx.files_download(dropbox_path)
            existing_content_str = existing_content.content.decode()

            # Append the new content
            updated_content = existing_content_str + "\n" + new_content

            # Upload the updated content back to Dropbox
            dbx.files_upload(updated_content.encode(), dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
            print("uploaded to dropbox")
        except dropbox.exceptions.HttpError as err:
            print(f"Error adding new content: {err}")
            access_token = get_new_token()
            self.ac = access_token
            UploadData.append_to_file(self,dropbox_path, new_content,access_token)


    def upload_image(self,dropbox_path, new_content,access_token):
        dbx = dropbox.Dropbox(access_token)
        try:
            updated_content = new_content

            # Upload the updated content back to Dropbox
            dbx.files_upload(updated_content, dropbox_path)
            print("uploaded image to dropbox")
        except dropbox.exceptions.HttpError as err:
            print(f"Error adding new content: {err}")
            access_token = get_new_token()
            self.ac = access_token
            UploadData.upload_image(self,dropbox_path, new_content,access_token)

    def run(self):
        if self.typeofupload == 'txt':
            UploadData.append_to_file(self,self.txtpath, self.txtdata,self.ac)
        elif self.typeofupload == 'img':
            UploadData.upload_image(self,self.imgpath, self.imgdata,self.ac)
        elif self.typeofupload == 'both':
            UploadData.append_to_file(self,self.txtpath, self.txtdata,self.ac)
            UploadData.upload_image(self,self.imgpath, self.imgdata,self.ac)

    





import requests

def send_notification( title, body):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {
        "Access-Token": os.environ['PUSHBULLET_ACCESS_TOKEN'],
        "Content-Type": "application/json"
    }
    data = {
        "type": "note",
        "title": title,
        "body": body
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print(response.status_code)
        print("Failed to send notification.")


import face_recognition

person1_image = face_recognition.load_image_file("myimage.jpeg")
person2_image = face_recognition.load_image_file("supriya.png")
# person3_image = face_recognition.load_image_file("myimage2.png")

person1_encoding = face_recognition.face_encodings(person1_image)[0]
person2_encoding = face_recognition.face_encodings(person2_image)[0]
# person3_encoding = face_recognition.face_encodings(person3_image)[0]

known_encodings = [person1_encoding, person2_encoding]
known_names = ["Himank", "Supriya"]

import cv2

video_capture = cv2.VideoCapture(0)
current_faces = dict()

while True:
    ret, frame = video_capture.read()

    face_locations = face_recognition.face_locations(frame)

    if len(face_locations) == 0:
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for name in list(current_faces.keys()):
        current_faces[name] -= 1
        if current_faces[name] == 0:
            del current_faces[name]
            body = name + " has left the room!"
            print(body)
            send_notification("Face Left", body)
            # append_to_file('/recognitions.txt', body+" "+str(datetime.datetime.now()))
            thread1 = UploadData('/recognitions.txt', '', 'txtupload', body+" "+str(datetime.datetime.now()), '', 'txt',access_token)
            thread1.start()

    if len(face_locations) > 0:
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            if True in matches:
                match_idx = matches.index(True)
                matched_name = known_names[match_idx]
                try:
                    current_faces[matched_name] += 1
                except KeyError:
                    current_faces[matched_name] = 20
                    body = matched_name + " has been recognized!"
                    print(body)
                    datetimenow = str(datetime.datetime.now())
                    timenow = str(datetime.datetime.now().time())
                    datetoday = str(datetime.date.today())
                    send_notification("Face Recognized", body)
                    # append_to_file('/recognitions.txt', body+" "+datetimenow)
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_data = io.BytesIO(buffer.tobytes())
                    frame_data.seek(0)
                    # upload_image('/images_data/'+matched_name+'/'+datetoday+'/'+timenow+'.jpg', frame_data.read())
                    thread1 = UploadData('/recognitions.txt', '/images_data/'+matched_name+'/'+datetoday+'/'+timenow+'.jpg', 'bothupload', body+" "+datetimenow, frame_data.read(), 'both',access_token)
                    thread1.start()

    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close all OpenCV windows
video_capture.release()
cv2.destroyAllWindows()

