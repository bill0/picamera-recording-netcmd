#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time
import socket
import picamera
import picamera.array
import numpy as np
from PIL import Image


HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007 
flag_captrue = False


class Server_Thread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        address = (HOST, PORT)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(address)
    def run(self):
        print "Starting " + self.name

        while True:
            data, addr = self.s.recvfrom(2048)
            if not data:
                print "client has exist"
                break
            print "received:", data, "from", addr
            if data == 'c':
                threadLock.acquire()
                global flag_captrue
                flag_captrue = True
                threadLock.release()
            
class Camera_Thread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print "Starting " + self.name

        while True:
            with picamera.PiCamera() as camera:
                camera.resolution = (640, 480)
                camera.framerate = 30
                filename = 'video/' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.h264' 
                camera.start_recording(
                    filename, format='h264'
#                    motion_output=MyMotionDetector(camera)
                    )
                
                hour = 1
                min = hour * 60
                second = min * 60
                camera.wait_recording(second)
                camera.stop_recording()
                
                print "stop_recording"
            print "stop_recording2"        
frame = 0


class MyMotionDetector(object):
    def __init__(self, camera):
        self.camera = camera

    def write(self, s):
        global flag_captrue
        if flag_captrue == True:
            global frame
            frame += 1
            filename = 'photo/' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.jpg' 
            print('Writing %s' % filename)
            self.camera.capture(filename, use_video_port=True)
            threadLock.acquire()
            flag_captrue = False
            threadLock.release()
            print('Motion detected!')


threadLock = threading.Lock()
threads = []

# thread1 = Server_Thread(1, "Server_Thread", 1)
thread2 = Camera_Thread(2, "Camera_Thread", 2)

# thread1.start()
thread2.start()

# threads.append(thread1)
threads.append(thread2)

for t in threads:
    t.join()
print "Exiting Main Thread"
