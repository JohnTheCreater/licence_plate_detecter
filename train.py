from ultralytics import YOLO
import os
import cv2
from sort.sort import *
from util import get_bus,read_number_plate,write_csv
import  requests
import json
print(os.getcwd())



results={}
cam=cv2.VideoCapture('/home/john/road_track/VID_20240314_143858.mp4')
bus_tracker=Sort()
number_plate_model=YOLO('/home/john/road_track/new model/last.pt')
bus_model=YOLO('yolov8x.pt')
max_score=0.0
max_score_number_plate=''
frame_count=-1
_=True
while _:
    _,img=cam.read()
    
    if img is None:
        print('error: img not detected')
        break
         
    bus_results=bus_model.predict(img)
    result=bus_results[0]
    detection_=[]
    if _ :
        frame_count+=1
        print(frame_count)
        results[frame_count]= {}
        for box in result.boxes:
            if box.cls[0].item() == 5:
                x1, y1, x2, y2 = box.xyxy[0]
                detection_.append([x1, y1, x2, y2 ])
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) 
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                object_name = result.names[box.cls[0].item()]
                (text_width, text_height) = cv2.getTextSize(object_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                # cropped_frame=img[y1:y2,x1:x2]
                # cv2.imwrite(f'/home/john/road_track/images/frame{frame_count}.jpg',cropped_frame)
                
                cv2.rectangle(img, (x1, y1 - text_height - 5), (x1 + text_width, y1), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, object_name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                

                print(result.names[box.cls[0].item()])
        print('bus detected')
        track_ids=bus_tracker.update(np.asarray(detection_))
        
        results_number_plate=number_plate_model(img)
        result_number_plate=results_number_plate[0]
        for number_plate in result_number_plate.boxes.data.tolist():
                    
                            x1, y1, x2, y2,score,class_id = number_plate
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            bus_x1,bus_y1,bus_x2,bus_y2,bus_id=get_bus(number_plate,track_ids)
                            if bus_id!=-1: 
                                number_plate_crop_img=img[y1:y2,x1:x2]
                                number_plate_crop_img_gray=cv2.cvtColor(number_plate_crop_img,cv2.COLOR_BGR2GRAY)
                                _,number_plate_crop_img_thresh=cv2.threshold(number_plate_crop_img_gray,64,255,cv2.THRESH_BINARY_INV)
                                number_plate_text,number_plate_text_score=read_number_plate(number_plate_crop_img_thresh)
                                
                                if number_plate_text is not None:
                                    results[frame_count][bus_id]={'bus':{'bbox':[bus_x1,bus_y1,bus_x2,bus_y2]},
                                                                'number plate':{'bbox':[x1, y1, x2, y2],
                                                                'text':number_plate_text,
                                                                'bbox_score':score,
                                                                'number_plate_score':number_plate_text_score}}

                            
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  
                                object_name = result_number_plate.names[class_id]

                                (text_width, text_height) = cv2.getTextSize(number_plate_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                                # cropped_frame=img[y1:y2,x1:x2]
                                # cv2.imwrite(f'/home/john/road_track/images/frame{frame_count}.jpg',cropped_frame)
                                # frame_count+=1
                                cv2.rectangle(img, (x1, y1 - text_height - 5), (x1 + text_width, y1),  (0, 165, 255), cv2.FILLED)
                                cv2.putText(img, number_plate_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                                if number_plate_text_score is not None and float(number_plate_text_score) > max_score:
                                    max_score=float(number_plate_text_score)
                                    max_score_number_plate=number_plate_text
                                    

        print(max_score)
        print("number plate detected ")
        # cv2.imshow('frame',img)
        # cv2.imwrite(f'frame{frame_count}.png',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
print(max_score)
print(max_score_number_plate)
write_csv(results,'test.csv')
print('csv created')
url='http://localhost:5000/makeAvail'
data={'licence_plate_number':max_score_number_plate}

response =requests.post(url,json=data,headers={'Content-Type':'application/json'})

print(response.status_code)
print(response.text)

cam.release()
cv2.destroyAllWindows()
