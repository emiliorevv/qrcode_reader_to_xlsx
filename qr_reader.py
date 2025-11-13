# qr_reader.py
import cv2

qr_detector = cv2.QRCodeDetector()

def read_qr_from_frame(frame):
    data, points, _ = qr_detector.detectAndDecode(frame)
    if data:
        return [data]
    return []
