from object_detection import ObjectDetection
import cvzone

class ObjectTracking:
    """
    This class is used to track objects in a frame using DeepSort
    """
    def __init__(self):
        self.previous_positions = {}

    def plot_box(self, frame, list):
        """
        This function is used to plot bounding boxes around detected objects in a frame
        
        Args:
            frame: The frame in which the objects are to be detected
            list: A list of objects to be detected in the frame
        Returns: A tuple containing the detections and the frame with bounding boxes around the detected objects"""
        od = ObjectDetection()
        detections = []
        (class_ids, scores, boxes) = od.detect(frame)  # Detect objects in the frame and consumes alot of time and cpu resources
        for box, class_id, score in zip(boxes, class_ids, scores):
            if class_id in [1,2,3,5]:
                (x, y, w, h) = box
                current_class = list[class_id]
                detections.append((([x, y, w, h]), score, current_class))
        return detections, frame
    
    def track_detect(self, detections, img, tracker):
        """
        This function is used to track detected objects in a frame
        Args:
            detections: The detected objects in the frame
            img: The frame in which the objects are to be tracked
            tracker: The tracker object used to track the objects"""
        tracks = tracker.update_tracks(detections, frame=img)
        direction_s = {}
        direction_n = {}

        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
        
            print(f"mean({track_id}): {getattr(track, 'mean')}. original_ltwh: {getattr(track, 'original_ltwh')}")
            ltrb = track.to_ltrb()
            north, south = self.get_direction(track=track)
            direction_s.update(south)
            direction_n.update(north)

            
            bbox = ltrb
            x1, y1, x2, y2 = bbox
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2-x1, y2-y1

            cvzone.putTextRect(img, f'ID: {track_id}', (x1, y1), scale=1, thickness=1, colorR=(0,0,255))
            cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=1, colorR=(255,0,255))
        return img, direction_s, direction_n
    
    def get_direction(self, track):
        """
        Determines the direction of a given track based on its current position and previous positions.

        Args:
            track: The track object containing information about the track.

        Returns:
            A tuple containing two dictionaries: `direction_north` and `direction_south`.
            `direction_north` contains the track IDs and their corresponding direction as "South" (entering the intersection).
            `direction_south` contains the track IDs and their corresponding direction as "North" (leaving the intersection).
        """
        direction_north = {}
        direction_south = {}
        current_position = track.mean[:]

        state = track.is_deleted()
        track_id = track.track_id

        if track_id in self.previous_positions:
            # Calculate the direction vector
            if state:
                del self.previous_positions[track_id]
            else:
                if current_position[1] < self.previous_positions[track_id][1] and current_position[5] > current_position[4]:
                    direction_north[track_id] = "North" # Leaving the intersection
                elif current_position[1] > self.previous_positions[track_id][1] and current_position[5] > current_position[4]:
                    direction_south[track_id] = "South" # Entering the intersection
                self.previous_positions[track_id] = current_position
        elif not state and track_id not in self.previous_positions:
            self.previous_positions[track_id] = current_position
        # use velocity and position to determine direction
            
        return direction_north, direction_south