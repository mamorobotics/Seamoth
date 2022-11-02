from turtle import left
import cv2, socket, json, numpy
from inputs import get_gamepad, devices
from threading import Thread
from tkinter import *
from PIL import Image, ImageTk

try:
    import RPi.GPIO
except ModuleNotFoundError:
    print("RPi.GIO module not found, motor control disabled")

motorThreads = []

class Controller():
    #dont touch these values, no idea why these work
    MAX_TRIG_VAL = float(256)
    MAX_JOY_VAL = float(32768)

    controllerValues = {'LeftJoystickY' : 0,'LeftJoystickX' : 0,'RightJoystickY' : 0,'RightJoystickX' : 0,'LeftTrigger' : 0,'RightTrigger' : 0,'LeftBumper' : 0,'RightBumper' : 0,'A' : 0,'X' : 0,'Y' : 0,'B' : 0,'LeftThumb' : 0,'RightThumb' : 0,'Menu' : 0,'Start' : 0,'DpadY' : 0,'DpadX' : 0}

    def __init__(self):
        #checking to make sure that controllers exist befor initiated
        if(len(devices.gamepads) < 1):
            raise RuntimeError("No Gamepad connection found")

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
    def __init__(self):
        pass

    def getHardwareMap(path):
        return open(path, "r").read()
    
    def getHardwareMapObject(hardwareMap):
        return json.loads(hardwareMap)

#uses open cv, this entire class is really easy to use and read
class Camera:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)

    def readCameraData(self):
        ret, frame = self.capture.read()
        while not ret:
            ret, frame = self.capture.read()
        return frame
    
    def close(self):
        self.capture.release()

    def encode(image, quality):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
        return cv2.imencode('.jpg', image, encode_param)[1].tobytes()

    def decode(image):
        nparr = numpy.frombuffer(image, numpy.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#all the GUI stuff
class UI:
    controllerValues = Controller.controllerValues
    menus = {}

    def _ui(self):
        win = Tk()
        win.title("Seamoth Homebase")
        win.config(bg="#323232") 

        #settings
        settings = Frame(win, bg="#323232")
        settings.grid(row=0, column=1, sticky=N)

        #conn details settings
        if self.menus.get("connDetails", True):
            connDetailsFrame = Frame(settings, bg="#323232")
            connDetailsFrame.grid(row=0, column=0, sticky=W, ipadx=10, pady=5, padx=5)
            Label(connDetailsFrame, text="CONNECTION DETAILS:", bg="#323232", foreground="#ffffff").pack(side=TOP, anchor=W)

            connDetailsIP = Label(connDetailsFrame, text="1.1.1.1", bg="#323232", foreground="#ffffff")
            connDetailsIP.pack(side=TOP, anchor=W)
            connDetailsPORT = Label(connDetailsFrame, text="1111", bg="#323232", foreground="#ffffff")
            connDetailsPORT.pack(side=TOP, anchor=W)

        #conn status settings
        if self.menus.get("connStatus", True):
            connStatusFrame = Frame(settings, bg="#323232")
            connStatusFrame.grid(row=1, column=0, sticky=W, ipadx=10, pady=5, padx=5)
            Label(connStatusFrame, text="CONNECTION STATUS:", bg="#323232", foreground="#ffffff").pack(side=TOP, anchor=W)

            connStatus = Label(connStatusFrame, text=self.connectionStatus, bg="#323232", foreground="#ffffff")
            connStatus.pack(side=TOP, anchor=W)

        #input settings
        if self.menus.get("input", True):
            inputDetailsFrame = Frame(settings, bg="#323232")
            inputDetailsFrame.grid(row=2, column=0, sticky=W, ipadx=10, pady=5, padx=5)
            Label(inputDetailsFrame, text="INPUT DETAILS:", bg="#323232", foreground="#ffffff").grid(row=0, column=0, sticky=W)

            inputDetailsJoyFrame = Frame(inputDetailsFrame, bg="#323232")
            inputDetailsJoyFrame.grid(row=1, column=0, sticky=W, ipadx=10, pady=5, padx=5)
            inputJoyLeftX = Scale(inputDetailsJoyFrame, from_=-1, to=1, resolution=0.01, orient=HORIZONTAL, label="Left Joy X", showvalue=0, bg="#323232", foreground="#ffffff", highlightthickness=0)
            inputJoyLeftX.pack(side=TOP, anchor=W)
            inputJoyLeftY = Scale(inputDetailsJoyFrame, from_=-1, to=1, resolution=0.01, orient=HORIZONTAL, label="Left Joy Y", showvalue=0, bg="#323232", foreground="#ffffff", highlightthickness=0)
            inputJoyLeftY.pack(side=TOP, anchor=W)
            inputJoyRightX = Scale(inputDetailsJoyFrame, from_=-1, to=1, resolution=0.01, orient=HORIZONTAL, label="Right Joy X", showvalue=0, bg="#323232", foreground="#ffffff", highlightthickness=0)
            inputJoyRightX.pack(side=TOP, anchor=W)
            inputJoyRightY = Scale(inputDetailsJoyFrame, from_=-1, to=1, resolution=0.01, orient=HORIZONTAL, label="Right Joy Y", showvalue=0, bg="#323232", foreground="#ffffff", highlightthickness=0)
            inputJoyRightY.pack(side=TOP, anchor=W)

            inputDetailsTrigFrame = Frame(inputDetailsFrame, bg="#323232")
            inputDetailsTrigFrame.grid(row=1, column=1, sticky=NW, ipadx=10, pady=5, padx=5)
            inputTrigRight = Scale(inputDetailsTrigFrame, from_=0, to=1, resolution=0.01, orient=HORIZONTAL, label="Right Trig X", showvalue=0, bg="#323232", foreground="#ffffff", highlightthickness=0)
            inputTrigRight.pack(side=TOP, anchor=W)
            inputTrigLeft = Scale(inputDetailsTrigFrame, from_=0, to=1, resolution=0.01, orient=HORIZONTAL, label="Right Trig Y", showvalue=0, bg="#323232", foreground="#ffffff", highlightthickness=0)
            inputTrigLeft.pack(side=TOP, anchor=W)
        
        #video
        video = Label(win)
        video.grid(row=0, column=0)
        
        def updateFrame():
            if self.menus.get("connDetails", True):
                connDetailsIP.configure(text=f"IP: {self.connInfo[0]}")
                connDetailsPORT.configure(text=f"PORT: {self.connInfo[1]}")

            if self.menus.get("connStatus", True):
                connStatus.configure(text=self.connectionStatus)

            if self.menus.get("input", True):
                inputJoyLeftX.set(float(self.controllerValues.get("LeftJoystickX")))
                inputJoyLeftY.set(float(self.controllerValues.get("LeftJoystickY")))
                inputJoyRightX.set(float(self.controllerValues.get("RightJoystickX")))
                inputJoyRightY.set(float(self.controllerValues.get("RightJoystickY")))
                inputTrigLeft.set(float(self.controllerValues.get("LeftTrigger")))
                inputTrigRight.set(float(self.controllerValues.get("RightTrigger")))

            cv2image = cv2.cvtColor(self.frame,cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image = img)
            video.imgtk = imgtk
            video.configure(image=imgtk)
            video.after(20, updateFrame)

        updateFrame()
        win.mainloop()

    def __init__(self, path, menus={}):
        self.menus = menus
        self.frame = cv2.imread(path)
        self.connectionStatus = "Starting"
        self.connInfo = ("1.1.1.1", "1111")
        self.uiThread = Thread(target=self._ui, args=())
        self.uiThread.start()

#black magic voodo, dont really feel like commenting all of it
class DataConnection:
    output = ''
    connected = False

    def __init__(self):
        self.IP = socket.gethostbyname(socket.gethostname())

    def _listen(self):
        while True:
            msg_len = None
            while not msg_len:
                try:
                    msg_len = self.connection.recv(64).decode('utf-8')
                except:
                    pass

            self.output = self.connection.recv(int(msg_len))

    def clientStart(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

        thread = Thread(target=self._listen, args=())
        thread.start()


    def serverStart(self, port):
        self.PORT = int(port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.IP, self.PORT))

        self.server.listen()
        self.connection, self.connectionAddress = self.server.accept()

        self.connected = True

        thread = Thread(target=self._listen, args=())
        thread.start()

        return self.IP

    def send(self, msg):
        send_length = str(len(msg)).encode('utf-8')
        send_length += b' ' * (64 - len(send_length))
        self.connection.send(send_length)
        self.connection.send(msg)
