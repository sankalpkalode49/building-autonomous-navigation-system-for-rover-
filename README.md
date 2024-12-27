THIS REPOSITORY CONTRAINES THE CODE WHICH I USED FOR DEVELOPMENT OF THE AUTONOMOUS NAVIGATION ALOGIRTHM FOR A ROVER 

OBJECTIVE OF THE ROVER:
	1) Detect the testube
    2) Navigate towards it and pick it
	3)Look for the contaier and navigate towords it and place the testube init 
 	4) Avoid obatacls and crater while naivgating 

HARDWARE SELECTION:
	For hardware to perform realtime objection detect we had to select a powerfull single bord computer so we select Jetson Nano 4GB version.

MODEL SELECTION FOR OBJECT DETECTION:
	We used YOLOv5s for this as it gaive balanced performance and moving to any higher model increase the inferance time on the jetson nano

Training Process:
we had to create our own dataset for this as task was very specific and we couldn't find any dateset.We used RoboFlow(https://roboflow.com/) for making and labeling our dataset.
for traing we used the official github repository for the train (https://github.com/ultralytics/yolov5)

after the training was done we converted the .pt model to tensorrt .trt as the .pt model we alot to handle for our jetson nano so we converted it to .trt format and it also helped us to optimize the model.


