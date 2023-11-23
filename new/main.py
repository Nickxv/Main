import cv2
import time
import pygetwindow as gw
from PIL import Image, ImageTk
import tkinter as tk

class FPSCounter:
    def __init__(self, video_path, update_interval=1):
        self.video_path = video_path
        self.update_interval = update_interval
        self.root = tk.Tk()
        self.root.title("FPS Counter")

        # Label to display FPS
        self.fps_label = tk.Label(self.root, text="FPS: 0")
        self.fps_label.pack()

        # Get the video properties
        self.cap = cv2.VideoCapture(video_path)
        self.frame_width = int(self.cap.get(3))
        self.frame_height = int(self.cap.get(4))

        # Initialize variables
        self.frame_count = 0
        self.start_time = time.time()

        # Start the update loop
        self.update_fps()

    def update_fps(self):
        ret, frame = self.cap.read()

        if not ret:
            self.cap.release()
            self.root.destroy()
            return

        self.frame_count += 1

        # Check if update interval has passed
        if time.time() - self.start_time >= self.update_interval:
            # Calculate FPS
            fps = self.frame_count / (time.time() - self.start_time)

            # Update the label
            self.fps_label.config(text=f"FPS: {fps:.2f}")

            # Reset variables for the next interval
            self.frame_count = 0
            self.start_time = time.time()

        # Update the window periodically
        self.update_window(frame)

        # Schedule the next update
        self.root.after(1, self.update_fps)

    def update_window(self, frame):
        # Convert frame to PhotoImage
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=img)

        # Find the active window
        active_window = gw.getActiveWindow()

        # Create a Toplevel window to overlay on top of the active window
        overlay_window = tk.Toplevel(self.root)
        overlay_window.geometry(f"{self.frame_width}x{self.frame_height}+{active_window.left}+{active_window.top}")

        # Create a label in the overlay window to display the frame
        label = tk.Label(overlay_window, image=img)
        label.image = img
        label.pack()

if __name__ == "__main__":
    video_path = "path/to/your/video/file.mp4"
    fps_counter = FPSCounter(video_path)
    fps_counter.root.mainloop()
    