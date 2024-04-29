from typing import Dict, Iterable, List, Set, Tuple
import cv2
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO

import supervision as sv
from arguments import source_video_path, source_weights_path, target_video_path, confidence_threshold, iou_threshold

COLORS = sv.ColorPalette.from_hex(["#E6194B", "#3CB44B", "#FFE119", "#3C76D1"])

ZONE_IN_POLYGONS = [
    np.array([[592, 282], [900, 282], [900, 82], [592, 82]]),
    np.array([[950, 860], [1250, 860], [1250, 1060], [950, 1060]]),
    np.array([[592, 582], [592, 860], [392, 860], [392, 582]]),
    np.array([[1250, 282], [1250, 530], [1450, 530], [1450, 282]]),
]

ZONE_OUT_POLYGONS = [
    np.array([[950, 282], [1250, 282], [1250, 82], [950, 82]]),
    np.array([[592, 860], [900, 860], [900, 1060], [592, 1060]]),
    np.array([[592, 282], [592, 550], [392, 550], [392, 282]]),
    np.array([[1250, 860], [1250, 560], [1450, 560], [1450, 860]]),
]



def initiate_polygon_zones(
    polygons: List[np.ndarray],
    frame_resolution_wh: Tuple[int, int],
    triggering_anchors: Iterable[sv.Position] = [sv.Position.CENTER],
) -> List[sv.PolygonZone]:
    return [
        sv.PolygonZone(
            polygon=polygon,
            frame_resolution_wh=frame_resolution_wh,
            triggering_anchors=triggering_anchors,
        )
        for polygon in polygons
    ]


class VideoProcessor:
    def __init__(
        self,
        source_weights_path: str,
        source_video_path: str,
        target_video_path: str = None,
        confidence_threshold: float = 0.3,
        iou_threshold: float = 0.7,
    ) -> None:
        self.conf_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.source_video_path = source_video_path
        self.target_video_path = target_video_path

        self.model = YOLO(source_weights_path)
        self.tracker = sv.ByteTrack()

        self.video_info = sv.VideoInfo.from_video_path(source_video_path)
        self.zones_in = initiate_polygon_zones(
            ZONE_IN_POLYGONS, self.video_info.resolution_wh, [sv.Position.CENTER]
        )
        self.zones_out = initiate_polygon_zones(
            ZONE_OUT_POLYGONS, self.video_info.resolution_wh, [sv.Position.CENTER]
        )

        self.bounding_box_annotator = sv.BoundingBoxAnnotator(color=COLORS)
        self.label_annotator = sv.LabelAnnotator(
            color=COLORS, text_color=sv.Color.BLACK
        )
      

    def process_video(self, no_of_vehicles_per_lane, green_lane):
        frame_generator = sv.get_video_frames_generator(
            source_path=self.source_video_path
        )

        if self.target_video_path:
            with sv.VideoSink(self.target_video_path, self.video_info) as sink:
                for frame in tqdm(frame_generator, total=self.video_info.total_frames):
                    annotated_frame, vehicle_per_zone = self.process_frame(frame)
                    no_of_vehicles_per_lane.update(vehicle_per_zone)
                    cv2.imshow("Processed Video", annotated_frame)
                    if cv2.waitKey(1) == 27:
                        green_lane.value = "Error"
                        break
                    sink.write_frame(annotated_frame)
        else:
            for frame in tqdm(frame_generator, total=self.video_info.total_frames):
                annotated_frame, vehicle_per_zone = self.process_frame(frame)
                no_of_vehicles_per_lane.update(vehicle_per_zone)
                cv2.imshow("Processed Video", annotated_frame)
                if cv2.waitKey(1) == 27:
                    green_lane.value = "Error"
                    break
            cv2.destroyAllWindows()

    def annotate_frame(
        self, frame: np.ndarray, detections: sv.Detections, vehicles_per_zone: Dict[str, int]
    ) ->Tuple[np.ndarray, Dict[str, int]]:
        annotated_frame = frame.copy()
        for i, (zone_in, zone_out) in enumerate(zip(self.zones_in, self.zones_out)):
            annotated_frame = sv.draw_polygon(
                annotated_frame, zone_in.polygon, COLORS.colors[i]
            )
            annotated_frame = sv.draw_polygon(
                annotated_frame, zone_out.polygon, COLORS.colors[i]
            )
            cv2.putText(annotated_frame,
                        f"lane{i} vehicles: {vehicles_per_zone[f'lane{i}']}",
                        (10, 30 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
                        2)
        labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]
        annotated_frame = self.bounding_box_annotator.annotate(
            annotated_frame, detections
        )
        annotated_frame = self.label_annotator.annotate(
            annotated_frame, detections, labels
        )
        return annotated_frame, vehicles_per_zone

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        results = self.model(
            frame, verbose=False, conf=self.conf_threshold, iou=self.iou_threshold
        )[0]
        detections = sv.Detections.from_ultralytics(results)
        detections.class_id = np.zeros(len(detections))
        detections = self.tracker.update_with_detections(detections)

        detections_in_zones = []
        detections_out_zones = []
        y = 0
        vehicles_per_zone = {}

        for zone_in in self.zones_in:
            detections_in_zone = detections[zone_in.trigger(detections=detections)]
            detections_in_zones.append(detections_in_zone)
            print(f"Zone {y} in: {len(detections_in_zone)}")
            vehicles_per_zone[f"lane{y}"] = len(detections_in_zone)
            y += 1

        detections = sv.Detections.merge(detections_in_zones)

        return self.annotate_frame(frame, detections, vehicles_per_zone)





# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Traffic Flow Analysis with YOLO and ByteTrack"
#     )


#     parser.add_argument(
#         "--confidence_threshold",
#         default=0.3,
#         help="Confidence threshold for the model",
#         type=float,
#     )
  

#     args = parser.parse_args()
#     processor = VideoProcessor(
#         source_weights_path=source_weights_path,
#         source_video_path=source_video_path,
#         target_video_path=target_video_path,
#         confidence_threshold=confidence_threshold,
#         iou_threshold=iou_threshold,
#     )
#     processor.process_video()


