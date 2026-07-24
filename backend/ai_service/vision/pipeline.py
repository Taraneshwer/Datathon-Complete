import logging

logger = logging.getLogger(__name__)

def run_image_pipeline(file_path: str) -> tuple[list[str], int]:
    """OpenCV face detection + YOLO object detection."""
    try:
        import cv2
        img = cv2.imread(file_path)
        if img is None:
            return [], 0

        # Face detection using Haar cascade
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        face_count = len(faces)

        # YOLO object detection (stub — returns simulated labels in dev)
        detected_objects = run_yolo_detection(file_path)

        return detected_objects, face_count
    except Exception as exc:
        logger.warning("Image pipeline error: %s", exc)
        return [], 0


def run_yolo_detection(file_path: str) -> list[str]:
    """
    YOLOv11 object detection.
    In production: load the YOLO model once at startup and run inference.
    Stub returns empty list (no model file in dev).
    """
    logger.debug("YOLO detection stub — load model for production use.")
    return []


def run_video_pipeline(file_path: str) -> tuple[list[str], int]:
    """Sample every 30th frame and run image analysis."""
    try:
        import cv2
        cap = cv2.VideoCapture(file_path)
        all_objects: set[str] = set()
        total_faces = 0
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % 30 == 0:
                tmp = f"/tmp/frame_{frame_idx}.jpg"
                cv2.imwrite(tmp, frame)
                objs, faces = run_image_pipeline(tmp)
                all_objects.update(objs)
                total_faces = max(total_faces, faces)
            frame_idx += 1

        cap.release()
        return list(all_objects), total_faces
    except Exception as exc:
        logger.warning("Video pipeline failed: %s", exc)
        return [], 0
