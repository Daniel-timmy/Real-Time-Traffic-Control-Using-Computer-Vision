source_weights_path="data/traffic_analysis.pt" # do not touch
source_video_path="data/traffic_analysis.mov" # replace this with the path for the drone footage
target_video_path="data/traffic_analysis_result1.mov" # make this into this target_video_path="" if you don't want to save the resulting video

confidence_threshold=0.5 # do not touch
iou_threshold=0.7 # do not touch
weights_path="dnn_model/yolov4.weights" # do not touch
cfg_path="dnn_model/yolov4.cfg" # do not touch

camera0="los_angeles.mp4" # this represent the paths to the cameras you want to use, for the code that uses 4 camera or 
# or you can provide a video path to test it just as i have done.
camera1="traffic_stop.mp4"
camera2="traffic_stop.mp4"
camera3="traffic_stop.mp4"
