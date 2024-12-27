import sys
import cv2
import imutils
from yoloDet import YoloTRT
import serial
import struct
import time

s = serial.Serial("/dev/ttyUSB0", 9600)

model = YoloTRT(library="yolov5/build/libmyplugins.so", engine="yolov5/build/final_vr.engine", conf=0.45, yolo_ver="v5")

cnt = 0
tt_width = 8  # cmq
container_width = 15  # cm
obstacle_width = 15  # cm
crater_width = 20  # cm
KNOWN_DISTANCE = 72  # cm

def object_detector(image):
    data_list = []
    results = model.Inference(image)
    for detection in results:
        class_id = detection["class"]
        box = detection["box"]
        x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        width = abs(int(x2 - x1))
        if class_id in ["test_tube", "container", "obstacle", "crater"]:
            data_list.append([class_id, width, (center_x, center_y)])
    return data_list

def focal_length_finder(measured_distance, real_width, width_in_rf):
    return (width_in_rf * measured_distance) / real_width

def distance_finder(focal_length, real_object_width, width_in_frame):
    return (real_object_width * focal_length) / width_in_frame

def initialize_reference_images():
    ref_tt = cv2.imread(r'/home/rover/Documents/JetsonYolov5/test_tube.jpg')
    ref_container = cv2.imread(r'/home/rover/Documents/JetsonYolov5/container.jpg')
    ref_obs = cv2.imread(r'/home/rover/Documents/JetsonYolov5/obstacle.jpg')
    
    tt_data = object_detector(ref_tt)
    container_data = object_detector(ref_container)
    obstacle_data = object_detector(ref_obs)
    
    tt_width_ref = tt_data[0][1] if tt_data else 1
    container_width_ref = container_data[0][1] if container_data else 1
    obstacle_width_ref = obstacle_data[0][1] if obstacle_data else 1
    
    focal_tt = focal_length_finder(KNOWN_DISTANCE, tt_width, tt_width_ref)
    focal_container = focal_length_finder(KNOWN_DISTANCE, container_width, container_width_ref)
    focal_obstacle = focal_length_finder(KNOWN_DISTANCE, obstacle_width, obstacle_width_ref)
    
    return focal_tt, focal_container, focal_obstacle

focal_tt, focal_container, focal_obstacle = initialize_reference_images()

cap = cv2.VideoCapture(0)
manual_mode = True

while True:
    ret, frame = cap.read()
    if not ret:
        break

    data = object_detector(frame)
    x_tt, x_con, x_obs = -12, -12, -12
    y_var, tt_dis, distance_obs = 0, 0, 0

    for d in data:
        class_id, width, (x, y) = d
        if class_id == 'test_tube':
            tt_dis = distance_finder(focal_tt, tt_width, width)
            x_tt, y_var = x, y
            # size = px_cm_ratio * width
            cv2.circle(frame, (x, y), abs(width // 2), (255, 255, 255))
            cv2.putText(frame, f'Dis: {round(tt_dis, 2)} cm', (x + 5, y + 13), cv2.FONT_HERSHEY_COMPLEX, 0.48, (0, 255, 255), 2)
        
        elif class_id == 'container':
            con_dis = distance_finder(focal_container, container_width, width)
            con_dis1 = con_dis *254
            x_con, y_var = x, y
            # size = px_cm_ratio * width
            cv2.circle(frame, (x, y), abs(width // 2), (255, 255, 255))
            cv2.putText(frame, f'Dis: {round(con_dis1, 2)} cm', (x + 5, y + 13), cv2.FONT_HERSHEY_COMPLEX, 0.48, (0, 255, 255), 2)
        
        elif class_id == 'obstacle':
            distance_obs = distance_finder(focal_obstacle, obstacle_width, width) * 2
            x_obs = x
            cv2.circle(frame, (x, y), abs(width // 2), (255, 255, 255))
            # Handle obstacle logic based on distance and position

    print(f"*************************      {cnt}    ***********************************")
            
    if not manual_mode:


        if 1 < x_tt < 450 and cnt == 0:
            s.write(b'l')
        elif x_tt >= 900 and cnt == 0:
            s.write(b'r')
        elif 450 < x_tt < 900 and cnt == 0:
            if round(tt_dis) > 34:
                s.write(b'f')
            elif round(tt_dis) <= 34:
                s.write(b"m")
                if round(tt_dis) > 13:
                    s.write(b'f')
                elif round(tt_dis) <= 13 :
                    s.write(b"s")
                    cnt = cnt + 1
                    s.write(b"p")
                    s.write(b"n")
                    s.write(b'j')
                    
                else:
                    s.write(b'r')


        else:
        #         if 1 < x_obs < 900:
        #             s.write(b'r')
        #             time.sleep(1)
        #             s.write(b'f')
        #             time.sleep(2)
        #             s.write(b'l')
        #         elif 900 <= x_obs:
        #             s.write(b'l')
        #             time.sleep(1)
        #             s.write(b'f')
        #             time.sleep(2)
        #             s.write(b'r')
        #     elif round(tt_dis) <= 50:
        #         s.write(b's')
        #         s.write(b'p')
            if 1 < x_con < 450 and cnt == 1:
                s.write(b'l')
            elif x_con >= 900 and cnt == 1:
                s.write(b'r')
            elif 450 < x_con < 900 and cnt == 1:
                if round(con_dis1) > 23:
                    s.write(b'f')
                    # if 1 < x_obs < 900:
                    #     s.write(b'r')
                    #     time.sleep(1)
                    #     s.write(b'f')
                    #     time.sleep(2)
                    #     s.write(b'l')
                    # elif 900 <= x_obs:
                    #     s.write(b'l')
                    #     time.sleep(1)
                    #     s.write(b'f')
                    #     time.sleep(2)
                    #     s.write(b'r')
                elif round(con_dis1) <= 23 and cnt == 1:
                    s.write(b's')
                    s.write(b'z')
                    cnt = cnt + 1
                else:
                    s.write(b's')
            else:
                if cnt == 2:
                    s.write(b's')
                else:
                    s.write(b"r")

    cv2.imshow('frame', frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('m'):
        manual_mode = not manual_mode
        if manual_mode:
            print("/////////////////////////Switched to Manual Mode/////////////////////////////")
        else:
            print("//////////////////////////Switched to Autonomous Mode////////////////////////")
    elif manual_mode:
        if key == ord('w'):
            s.write(b'f')
            print("forward")
        elif key == ord('a'):
            s.write(b'l')
        elif key == ord('d'):
            s.write(b'r')         
        elif key == ord('s'):
            s.write(b'b')
        elif key == ord('t'):
            s.write(b's')
        elif key == ord('p'):
            s.write(b'p')
        elif key == ord('z'):
            s.write(b'z')
        elif key == ord('v'):
            s.write(b'v')

cap.release()
cv2.destroyAllWindows()
