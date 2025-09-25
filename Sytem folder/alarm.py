import pygame
import time
import threading

class AlarmSystem:
    def __init__(self):
        pygame.mixer.init()
        self.alarm_sound = pygame.mixer.Sound('static/sounds/alarm.mp3')
        self.alarm_playing = False
        self.last_alarm_time = 0
        self.cooldown_period = 4  # 4 seconds cooldown
        self.stop_alarm_flag = False
        
    def trigger_alarm(self):
        current_time = time.time()
        
        # Check if cooldown period has passed
        if current_time - self.last_alarm_time < self.cooldown_period:
            return
        
        # Check if alarm is already playing
        if self.alarm_playing:
            return
            
        self.last_alarm_time = current_time
        self.alarm_playing = True
        self.stop_alarm_flag = False
        
        # Play alarm in a separate thread
        def play_alarm():
            self.alarm_sound.play()
            while pygame.mixer.get_busy() and not self.stop_alarm_flag:
                time.sleep(0.1)
            self.alarm_playing = False
        
        alarm_thread = threading.Thread(target=play_alarm)
        alarm_thread.start()
    
    def stop_alarm(self):
        self.stop_alarm_flag = True
        pygame.mixer.stop()
        self.alarm_playing = False