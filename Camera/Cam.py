import cv2
import os
from datetime import datetime

class CameraApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # Open the default camera
        self.is_recording = False
        self.recorded_frames = []

    def capture_picture(self):
        ret, frame = self.cap.read()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"picture_{timestamp}.png"
            cv2.imwrite(filename, frame)
            print(f"Picture captured: {filename}")

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.recorded_frames = []
            print("Recording started. Press 'q' to stop.")
        else:
            self.is_recording = False
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"video_{timestamp}.avi"
            out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*"XVID"), 20.0, (640, 480))
            for frame in self.recorded_frames:
                out.write(frame)
            out.release()
            print(f"Video saved: {filename}")

    def run(self):
        while True:
            ret, frame = self.cap.read() 
            cv2.imshow('Camera App', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                self.capture_picture()
            elif key == ord('r'):
                self.toggle_recording()

            if self.is_recording:
                self.recorded_frames.append(frame)

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = CameraApp()
    app.run()
