import time
import threading
import base64
import requests
import RPi.GPIO as GPIO
from aiy.board import Board
from aiy.voice.audio import AudioFormat, play_wav, record_file
from gtts import gTTS
import os
import subprocess


Lab = AudioFormat(sample_rate_hz=16000, num_channels=2, bytes_per_sample=2)

GPIO.setmode(GPIO.BCM)
SEQUENCE = [[1,0,0,0], [1,1,0,0], [0,1,0,0], [0,1,1,0],
            [0,0,1,0], [0,0,1,1], [1,0,0,1], [1,0,0,1]]
STEPPER_PINS = [17,18,27,22]
for pin in STEPPER_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

class TTSClient:
    def __init__(self):
        self.language = "zh-tw"

    def generate_audio(self, text: str, filename: str):
        if not os.path.exists(filename):
            tts = gTTS(text=text, lang=self.language)
            temp_file = "temp_" + filename
            tts.save(temp_file)
            subprocess.run(["ffmpeg", "-i", temp_file, "-ar", "16000", "-ac", "2", "-y", filename], check=True)
            os.remove(temp_file)

class MotorController:
    def __init__(self):
        self.sequence_index = 0
        self.wait_time = 5 / 1000
        self.direction = None
        self.running = False
        self.thread = None

    def rotate(self):
        while self.running and self.direction:
            direction_value = 1 if self.direction == "clockwise" else -1
            for pin in range(len(STEPPER_PINS)):
                GPIO.output(STEPPER_PINS[pin], SEQUENCE[self.sequence_index][pin])
            self.sequence_index = (self.sequence_index + direction_value) % len(SEQUENCE)
            time.sleep(self.wait_time)

    def set_direction(self, direction):
        if direction != self.direction:
            self.direction = direction
            if direction == "clockwise":
                print("正在順時針旋轉...")
                play_wav("clockwise.wav")
            elif direction == "counterclockwise":
                print("正在逆時針旋轉...")
                play_wav("counterclockwise.wav")
            elif direction is None:
                print("馬達已停止旋轉")
                play_wav("stop.wav")
            if not self.running and direction:
                self.running = True
                self.thread = threading.Thread(target=self.rotate)
                self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

def record_audio():
    with Board() as board:
        print("請按下按鈕開始錄音說 '順時針'、'逆時針' 或 '停止'")
        board.button.wait_for_press()
        done = threading.Event()
        board.button.when_released = done.set
        
        def wait():
            start = time.monotonic()
            while not done.is_set():
                duration = time.monotonic() - start
                print("錄音中: %.02f 秒 [按下按鈕停止錄音]" % duration)
                time.sleep(0.5)
            
        try:
            record_file(
                Lab, 
                filename="recording.wav", 
                wait=wait, 
                filetype="wav", 
                device="plughw:2,0"
            )
        except Exception as e:
            print(f"錄音失敗: {e}")
            return False
        return True

def recognize_speech(file_path="recording.wav"):
    try:
        with open(file_path, 'rb') as file:
            audio_data = base64.b64encode(file.read()).decode()
            response = requests.post('http://140.116.245.149:5002/proxy',
                                   data={'lang': 'STT for course', 'token': '2025@ME@asr', 'audio': audio_data})
            return response.json()['sentence'] if response.status_code == 200 else None
    except Exception as e:
        print(f"語音辨識失敗: {e}")
        return None

def main():
    tts = TTSClient()
    motor = MotorController()

    tts.generate_audio("正在順時針旋轉", "clockwise.wav")
    tts.generate_audio("正在逆時針旋轉", "counterclockwise.wav")
    tts.generate_audio("馬達已停止旋轉", "stop.wav")

    try:
        while True:
            if not record_audio():
                continue
            result = recognize_speech()
            if not result:
                print("辨識失敗，請重試")
                continue
            print(f"辨識結果: {result}")
            
            if "順時針" in result:
                motor.set_direction("clockwise")
            elif "逆時針" in result:
                motor.set_direction("counterclockwise")
            elif "停止" in result:
                motor.set_direction(None)
            else:
                print("無法識別指令，請說 '順時針'、'逆時針' 或 '停止'")

    except KeyboardInterrupt:
        print('關閉程式')
        motor.stop()
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()