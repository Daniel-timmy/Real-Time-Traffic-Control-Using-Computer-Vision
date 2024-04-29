import argparse
from multiprocessing import Manager, Process
from arguments import source_video_path, source_weights_path, target_video_path, confidence_threshold, iou_threshold
from aerial import VideoProcessor
from four_c import frame_processing, timing


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Traffic Flow Analysis with YOLO and ByteTrack"
    )


    parser.add_argument(
        "--mode",
        default="aerial",
        help="Confidence threshold for the model",
        type=str,
    )
  

    args = parser.parse_args()
    
    if args.mode == "aerial":
        processor = VideoProcessor(
            source_weights_path=source_weights_path,
            source_video_path=source_video_path,
            target_video_path=target_video_path,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
        )
        with Manager() as manager:
            print("Using the drone version")
            no_of_vehicles_per_lane = manager.dict()
            green_lane = manager.Value(str, "None")

            p1 = Process(target=processor.process_video, args=(no_of_vehicles_per_lane, green_lane))
            p2 = Process(target=timing, args=(no_of_vehicles_per_lane, green_lane))

            p1.start()
            p2.start()

            p1.join()
            p2.join()
    
        
        processor.process_video()
    elif args.mode == "4C":
        with Manager() as manager:
            print("Using the 4 camera version")
            no_of_vehicles_per_lane = manager.dict()
            green_lane = manager.Value(str, "None")

            p1 = Process(target=frame_processing, args=(no_of_vehicles_per_lane, green_lane))
            p2 = Process(target=timing, args=(no_of_vehicles_per_lane, green_lane))

            p1.start()
            p2.start()

            p1.join()
            p2.join()
    