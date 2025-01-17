# import tensor
# import numpy as np
# from simple_facerec import SimpleFacerec

import cv2
import dlib
import face_recognition


def faceBox(faceNet,frame):
    frameHeight=frame.shape[0]
    frameWidth=frame.shape[1]
    # blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, size, mean, swapRB=True)
    blob=cv2.dnn.blobFromImage(frame,1.0,(227,227),[104,117,123],swapRB=True)
    faceNet.setInput(blob) 
    detection=faceNet.forward()
    bboxs=[]
    for i in range(detection.shape[2]):
        confidence=detection[0,0,i,2]
        if confidence>0.7:        
                x1=int(detection[0,0,i,3]*frameWidth)
                y1=int(detection[0,0,i,4]*frameHeight)
                x2=int(detection[0,0,i,5]*frameWidth)
                y2=int(detection[0,0,i,6]*frameHeight)       
                bboxs.append([x1,y1,x2,y2]) 
                cv2.rectangle(frame , (x1,y1) , (x2,y2) , (0,255,0) , 2)
    return frame, bboxs

faceProto = "models/opencv_face_detector.pbtxt"
faceModel = "models/opencv_face_detector_uint8.pb"

ageProto = "models/age_deploy.prototxt"
ageModel = "models/age_net.caffemodel"

genderProto = "models/gender_deploy.prototxt"
genderModel = "models/gender_net.caffemodel"


faceNet=cv2.dnn.readNet(faceModel, faceProto)
ageNet=cv2.dnn.readNet(ageModel, ageProto)
genderNet=cv2.dnn.readNet(genderModel, genderProto)

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
# ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
ageList = ['(0-5)', '(6-9)', '(10-14)', '(15-19)', '(20-24)', '(25-29)', '(30-34)', '(35-39)', '(40-44)', '(45-49)', '(50-54)', '(55-59)', '(60-67)', '(68-75+)']
# genderList = ['Male' , 'Female']
genderList = ['Female' , 'Male']

video=cv2.VideoCapture(0)

padding=20

while True:
    ret,frame=video.read()
    # detect=faceBox(faceNet,frame)
    frame,bboxs=faceBox(faceNet,frame)
    for bbox in bboxs:
        # face=frame[bbox[1]:bbox[3],bbox[0]:bbox[2]]
        face = frame[max(0,bbox[1]-padding):min(bbox[3]+padding,frame.shape[0]-1),max(0,bbox[0]-padding):min(bbox[2]+padding, frame.shape[1]-1)]
        blob=cv2.dnn.blobFromImage(face , 1.0 , (227,227) ,[104,117,123], swapRB=True)
        
        genderNet.setInput(blob)
        genderprediction=genderNet.forward()
        gender=genderList[genderprediction[0].argmax()]
        
        ageNet.setInput(blob)
        ageprediction=ageNet.forward()
        age=ageList[ageprediction[0].argmax()]
        
        label="{},{}".format(gender,age)
        cv2.rectangle(frame , (bbox[0] , bbox[1]-30) , (bbox[2] , bbox[1]) , (0,255,0) , -1)
        cv2.putText(frame , label , (bbox[0] , bbox[1]-10) , cv2.FONT_HERSHEY_SIMPLEX, 0.8 , (255,255,255) , 2 , cv2.LINE_AA)
        
    cv2.imshow("Age-Gender",frame)
    k=cv2.waitKey(1)
    if k==ord('q'):
        break
video.release()
cv2.destroyAllWindows()    