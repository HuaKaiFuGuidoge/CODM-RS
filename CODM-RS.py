import cv2
import numpy as np
import tkinter as tk
import pyautogui
import os
import time
from threading import Thread
import pygame

class ScreenDetectorApp:
    def __init__(self, master):
        self.master = master
        master.title("屏幕检测")

        self.start_button = tk.Button(master, text="开始", command=self.toggle_detection)
        self.start_button.pack()

        self.detecting = False
        self.playing_media = False

        self.detect_thread = Thread(target=self.detect_screen)
        self.detect_thread.daemon = True

    def toggle_detection(self):
        if not self.detecting:
            self.start_detection()
        else:
            self.stop_detection()

    def start_detection(self):
        if not self.detecting:
            self.detecting = True
            self.start_button.config(text="停止")

            if not self.detect_thread.is_alive():
                self.detect_thread.start()

    def stop_detection(self):
        if self.detecting:
            self.detecting = False
            self.start_button.config(text="开始")

    def detect_screen(self):
        while True:
            if self.detecting and not self.playing_media:
                screenshot = pyautogui.screenshot()
                screen_array = np.array(screenshot)
                white_pixels = np.sum((screen_array[:, :, 0] > 200) &
                                      (screen_array[:, :, 1] > 200) &
                                      (screen_array[:, :, 2] > 200))

                total_pixels = screen_array.size / 3
                white_ratio = (white_pixels / total_pixels) * 100

                if white_ratio > 90:
                    self.play_media("rs.mp4", "rs.mp3")

            time.sleep(1)

    def play_media(self, video_path, audio_path):
        self.master.withdraw()

        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"无法打开视频文件: {video_path}")
            self.playing_media = False
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 30

        pygame.mixer.music.play()

        while cap.isOpened() and self.detecting:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.namedWindow('Video', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('Video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.setWindowProperty('Video', cv2.WND_PROP_TOPMOST, 1)

            cv2.imshow('Video', frame)

            if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        while pygame.mixer.music.get_busy() and self.detecting:
            continue

        pygame.mixer.quit()

        self.playing_media = False
        self.master.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenDetectorApp(root)
    root.mainloop()
