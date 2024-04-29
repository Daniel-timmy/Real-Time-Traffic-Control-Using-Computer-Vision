import time
import cv2
from helper_func import ObjectTracking
from deep_sort_realtime.deepsort_tracker import DeepSort
from arguments import camera0, camera1, camera2, camera3

cap = cv2.VideoCapture(camera0)
cap1 = cv2.VideoCapture(camera1)
cap2 = cv2.VideoCapture(camera2)
cap3 = cv2.VideoCapture(camera3)


def frame_processing(no_of_vehicles_per_lane, green_lane):
    """
    This function processes the frames from the video feed
    It uses the ObjectTracking class to detect and track objects in the frames
    It also uses the DeepSort class to track the detected objects between frames and assign unique IDs to them
    The function also determines the number of vehicles in each lane and stores the information in a dictionary 'no_of_vehicles_per_lane'.
    Args:
        no_of_vehicles_per_lane: A shared dictionary containing the number of vehicles in each lane
        green_lane: A shared variable containing the lane that has the green light
    Returns:
        None
    """
    ob = ObjectTracking()

    objects = [
        "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck",
        "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
        "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
        "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
        "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
        "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
        "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
        "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa",
        "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse",
        "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
        "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
        "toothbrush"
    ]
    tracker = DeepSort()
    tracker1 = DeepSort()
    tracker2 = DeepSort()
    tracker3 = DeepSort()

    while True:
        # Each frame represent frames from each lane entering the intersection
        ret, frame0 = cap.read()  #lane0
        if not ret:
            green_lane.value = "Error"
            # if there are no more frames to read from the video, break out of the loop
            # but i will recommend the system should be able to switch to a conventional traffic light system
            # rather than breaking out of the loop and causing the system to stop working

            break

        ret1, frame1 = cap1.read()  #lane1
        if not ret1:
            green_lane.value = "Error"

            break

        ret2, frame2 = cap2.read()  #lane2
        if not ret2:
            green_lane.value = "Error"

            break

        ret3, frame3 = cap3.read()  #lane3
        if not ret3:
            green_lane.value = "Error"

            break

        frames = {"lane0": frame0, "lane1": frame1, "lane2": frame2, "lane3": frame3}
        trkr = {"lane0": tracker, "lane1": tracker1, "lane2": tracker2, "lane3": tracker3}

        for frame in frames.keys():
            print(f"{green_lane}")
            if frame == green_lane:
                print(f"Green light is on {frame}. Skipping this frame")
                continue
            detections, v_frame = ob.plot_box(frame=frames[frame], list=objects)
            detect_frame, vehicles_south, vehicles_north = ob.track_detect(detections=detections, img=v_frame,
                                                                           tracker=trkr[frame])
            no_of_vehicles_per_lane[frame] = len(vehicles_south)
            print(no_of_vehicles_per_lane)
            cv2.imshow("Frame", detect_frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    cap.release()
    cv2.destroyAllWindows()


def timing(no_of_vehicles_per_lane, green_lane):
    """
    This function controls the timing of the traffic light
    It checks the number of vehicles in each lane and determines the lane with the highest number of vehicles
    The lane with the highest number of vehicles is given the green light
    And the time the green light is on is determined by the number of vehicles in the lane
    Once a lane has been given the green light, it is added to the list of lanes
    that has been greenlighted until all lanes have been served. This ensures that no lane is left out
    in a cycle. The algorithm is designed to serve all lanes in a cycle before starting a new cycle. And it always 
    picks the lane with the highest number of vehicles to serve first.
    Args:
        no_of_vehicles_per_lane: A shared dictionary containing the number of vehicles in each lane
        green_lane: A shared variable containing the lane that has the green light
    Returns:
        None
    """
    lane_time = {}  # This dictionary store the lanes which have turned green and their corresponding time

    while True:
        if green_lane.value == "None":
            green_lane.value = "lane0"
            print(f"Green light is on {green_lane}")
            time.sleep(
                100)  # This is just a placeholder for the actual code that will be used to control the traffic light hardware
            continue
        elif green_lane.value == "Error":
            break

        if len(lane_time.keys()) >= 4:
            nvpl = no_of_vehicles_per_lane.copy()
            print(f"All lanes have been served {lane_time} {nvpl}")
            lane_time.clear()
            max_key = max(nvpl, key=nvpl.get)
            lane_time[max_key] = no_of_vehicles_per_lane[max_key] * 100
            green_lane.value = max_key
            print(f"Green light is on {green_lane}")
            time.sleep(lane_time[
                           max_key])  # This is just a placeholder for the actual code that will be used to control the traffic light hardware
        elif len(no_of_vehicles_per_lane.keys()) == 0:
            green_lane.value = "lane0"
            print(f"Green light is on {green_lane}")
            time.sleep(
                100)  # This is just a placeholder for the actual code that will be used to control the traffic light hardware
        else:
            lane_left = {}
            for lane in no_of_vehicles_per_lane.keys():
                if lane not in lane_time.keys():
                    lane_left[lane] = no_of_vehicles_per_lane[lane]
            if len(lane_left.keys()) == 0:
                continue
            max_key = max(lane_left, key=lane_left.get)
            green_lane.value = max_key
            if lane_left[max_key] == 0:
                lane_time[max_key] = no_of_vehicles_per_lane[max_key]
                print(f"Green light is on {green_lane}")
                time.sleep(
                    100)  # This is just a placeholder for the actual code that will be used to control the traffic light hardware
            else:
                lane_time[max_key] = no_of_vehicles_per_lane[max_key] * 100  #seconds
                print(f"Green light is on {green_lane}")
                time.sleep(lane_time[
                               max_key])  # This is just a placeholder for the place of the actual code that will be used to control the traffic light hardware

# if __name__ == '__main__':
#     """
#     This is the main function that starts the two processes that will run the frame_processing and timing functions
#     """
#     with Manager() as manager:
#         no_of_vehicles_per_lane = manager.dict()
#         green_lane = manager.Value(str, "None")

#         p1 = Process(target=frame_processing, args=(no_of_vehicles_per_lane, green_lane))
#         p2 = Process(target=timing, args=(no_of_vehicles_per_lane, green_lane))

#         p1.start()
#         p2.start()

#         p1.join()
#         p2.join()
