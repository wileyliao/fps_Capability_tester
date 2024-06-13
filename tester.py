import cv2
import threading
import time
from queue import Queue

# 初始化視頻流
cap = cv2.VideoCapture(0)

# 設置參數
fps = 30
frame_queue = Queue(maxsize=100)
result_queue = Queue(maxsize=100)
stop_event = threading.Event()


def capture_frames(fps, stop_event):
    frame_interval = 1 / fps
    while not stop_event.is_set():
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break
        frame_queue.put(frame)
        if frame_queue.full():
            frame_queue.get()

        elapsed_time = time.time() - start_time
        sleep_time = frame_interval - elapsed_time
        if sleep_time > 0:
            time.sleep(sleep_time)
        print(f"Captured frame at {fps} FPS, queue size: {frame_queue.qsize()}")


def process_frames(process_time_per_frame, stop_event):
    while not stop_event.is_set():
        if frame_queue.empty():
            continue
        frame = frame_queue.get()

        # 模擬處理每幀
        start_time = time.time()
        time.sleep(process_time_per_frame)
        result_queue.put("processed")
        if result_queue.full():
            result_queue.get()
        elapsed_time = time.time() - start_time
        print(f"Processed 1 frame in {elapsed_time:.2f} seconds, result queue size: {result_queue.qsize()}")


def test_max_processing_time(fps, max_process_time):
    global frame_queue, result_queue
    frame_queue = Queue(maxsize=100)
    result_queue = Queue(maxsize=100)
    stop_event.clear()

    capture_thread = threading.Thread(target=capture_frames, args=(fps, stop_event))
    capture_thread.start()

    max_time_found = 0
    process_time = 0.05  # 初始處理時間和增量設置為0.05秒

    while process_time <= max_process_time:
        process_thread = threading.Thread(target=process_frames, args=(process_time, stop_event))
        process_thread.start()

        start_time = time.time()
        processed_frames = 0

        while time.time() - start_time < 5:
            if not result_queue.empty():
                result_queue.get()
                processed_frames += 1

        process_thread.join()

        avg_processed_fps = processed_frames / 5
        print(f"Test process time per frame: {process_time}, Processed FPS: {avg_processed_fps}")

        if avg_processed_fps < fps:
            print(f"At {process_time} seconds per frame, the system cannot keep up with the processing.")
            break
        else:
            max_time_found = process_time
            process_time += 0.05  # 增加處理時間

    stop_event.set()
    capture_thread.join()
    return max_time_found


# 測試每秒捕獲30幀時的最大處理時間
max_process_time = test_max_processing_time(30, 1)  # 最高測試處理時間設置為1秒
print(f"The maximum acceptable processing time per frame at 30 FPS is: {max_process_time} seconds")
cap.release()
