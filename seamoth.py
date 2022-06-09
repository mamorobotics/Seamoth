from http import server
from inputs import get_gamepad, devices
from threading import Thread
from cv2 import VideoCapture, imshow, destroyAllWindows
import socket

motorThreads = []

class Controller():
    #dont touch these values, no idea why these work
    MAX_TRIG_VAL = float(256)
    MAX_JOY_VAL = float(32768)

    def __init__(self):
        #checking to make sure that controllers exist befor initiated
        if(len(devices.gamepads) < 1):
            raise RuntimeError("No Gamepad connection found")
        
        #controller values
        self.controllerValues = {
            'LeftJoystickY' : 0,
            'LeftJoystickX' : 0,
            'RightJoystickY' : 0,
            'RightJoystickX' : 0,
            'LeftTrigger' : 0,
            'RightTrigger' : 0,
            'LeftBumper' : 0,
            'RightBumper' : 0,
            'A' : 0,
            'X' : 0,
            'Y' : 0,
            'B' : 0,
            'LeftThumb' : 0,
            'RightThumb' : 0,
            'Menu' : 0,
            'Start' : 0,
            'DpadY' : 0,
            'DpadX' : 0
        }

        #controller value monitor thread start
        self._monitor_thread = Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    #Following code is a modified version the tensorkart projects inplementation of controllor input detection by kevinhughes27 on github
    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.controllerValues['LeftJoystickY'] = event.state / Controller.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.controllerValues['LeftJoystickX'] = event.state / Controller.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.controllerValues['RightJoystickY'] = event.state / Controller.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.controllerValues['RightJoystickX'] = event.state / Controller.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.controllerValues['LeftTrigger'] = event.state / Controller.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.controllerValues['RightTrigger'] = event.state / Controller.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.controllerValues['LeftBumper'] = event.state
                elif event.code == 'BTN_TR':
                    self.controllerValues['RightBumper'] = event.state
                elif event.code == 'BTN_SOUTH':
                    self.controllerValues['A'] = event.state
                elif event.code == 'BTN_NORTH':
                    self.controllerValues['X'] = event.state
                elif event.code == 'BTN_WEST':
                    self.controllerValues['Y'] = event.state
                elif event.code == 'BTN_EAST':
                    self.controllerValues['B'] = event.state
                elif event.code == 'BTN_THUMBL':
                    self.controllerValues['LeftThumb'] = event.state
                elif event.code == 'BTN_THUMBR':
                    self.controllerValues['RightThumb'] = event.state
                elif event.code == 'BTN_SELECT':
                    self.controllerValues['Back'] = event.state
                elif event.code == 'BTN_START':
                    self.controllerValues['Start'] = event.state
                elif event.code == 'ABS_HAT0Y':
                    self.controllerValues['DpadY'] = -event.state
                elif event.code == 'ABS_HAT0X':
                    self.controllerValues['DpadX'] = event.state

class Motor:
    speed = 0
    connectionId = 0

    def __init__(self, connectionId):
        self.connectionId = connectionId

        #main motor function thread start
        motorThread = Thread(target=self._motorThread, args=())
        motorThread.start()

    #main motor function thread
    def _motorThread(self):
        print(f"Motor Connected on Port: {self.connectionId}")

#uses open cv, this entire class is really easy to use and read
class Camera:
    frame = ''
    
    def __init__(self):
        self.capture = VideoCapture(0)

    def readCameraData(self):
        ret, frame = self.capture.read()
        return frame
    
    def close(self):
        self.capture.release()
        destroyAllWindows()

#black magic voodo, dont really feel like commenting all of it
class DataConnection:
    output = ''

    def __init__(self):
        self.IP = socket.gethostbyname(socket.gethostname())

    def _listen(self):
        while True:
            msg_len = self.connection.recv(64).decode('utf-8')
            if msg_len:
                self.output = self.connection.recv(int(msg_len)).decode('utf-8')

    def clientStart(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))


    def serverStart(self, port):
        print(self.IP)
        self.PORT = int(port)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.IP, self.PORT))

        server.listen()
        self.connection, self.connectionAddress = server.accept()

        thread = Thread(target=self._listen, args=())
        thread.start()

    def send(self, msg):
        msg = msg.encode('utf-8')
        send_length = str(len(msg)).encode('utf-8')
        send_length += b' ' * (64 - len(send_length))
        self.connection.send(send_length)
        self.connection.send(msg)
