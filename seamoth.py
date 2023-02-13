import PIL
import cv2
import gpiozero
import json
import numpy
import socket
from PIL import ImageTk
from inputs import devices
from threading import Thread
from tkinter import *

PATH = "hardwareMap.txt"

global logs
logs = []

try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
except:
    logs.append("[ERROR] Unable to get windll.\n        Window sharpening will not be possible")


class Controller:
    """
    `Note: Some code in this class is a modified version of the tensorkart project's implementation of controller
    input detection by kevinhughes27 on GitHub`

    Controllers are currently tested to work with XInput designed controllers,
    however controls should be relatively normalized for other types of controllers.
    The class runs in a separate thread to read controller input and assigns read values to an internal
    buffer in the object. Reading the controllers in your main loop is as simple as referencing that buffer such as:

    ``values = controller.controllerValues``

    These values are returned as a dictionary with the following values:

    `LeftJoystickX, LeftJoystickY, LeftThumb, RightJoystickX, RightJoystickY, RightThumb, RightTrigger, RightBumper, LeftTrigger, LeftBumper, Menu, Start, DpadX, DpadY, A, X, Y, B`

    The controller class can later be referenced to access or set:

    * **Controller Values** : ``controller.controllerValues`` = most recent values of the controller

    :param controllerPort: controller identifier number
    """

    MAX_TRIG_VAL = float(256)
    MAX_JOY_VAL = float(32768)

    controllerValues = {'LeftJoystickY': 0, 'LeftJoystickX': 0, 'RightJoystickY': 0, 'RightJoystickX': 0,
                        'LeftTrigger': 0, 'RightTrigger': 0, 'LeftBumper': 0, 'RightBumper': 0, 'A': 0, 'X': 0, 'Y': 0,
                        'B': 0, 'LeftThumb': 0, 'RightThumb': 0, 'Menu': 0, 'Start': 0, 'DpadY': 0, 'DpadX': 0}

    def __init__(self, controllerPort: int):
        self.controllerPort = controllerPort

        # checking to make sure that controllers exist before initiated
        if len(devices.gamepads) < 1:
            logs.append("[ERROR] Cannot find a connected controller.\n")

        else:
            # controller value monitor thread start
            self.thread = Thread(target=self._monitor_controller, args=())
            self.thread.daemon = True
            self.thread.start()

    #
    def _monitor_controller(self):
        gamepad = devices.gamepads[self.controllerPort]

        while True:
            events = gamepad.read()
            for event in events:
                if event.code == 'ABS_Y':
                    self.controllerValues[
                        'LeftJoystickY'] = event.state / Controller.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.controllerValues[
                        'LeftJoystickX'] = event.state / Controller.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.controllerValues[
                        'RightJoystickY'] = event.state / Controller.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.controllerValues[
                        'RightJoystickX'] = event.state / Controller.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.controllerValues[
                        'LeftTrigger'] = event.state / Controller.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.controllerValues[
                        'RightTrigger'] = event.state / Controller.MAX_TRIG_VAL  # normalize between 0 and 1
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
    """
    The motor class represents a motor. It takes no inputs and has two functions, ``setMotor()`` and ``setSpeed()``.

    To set a motor you need to have a file within the project directory called hardwareMap.txt,
    which specifies the names and ports of all connected servos and motors. This file should follow the format of:

    ``{ "name": [port1, port2], "name": [port1, port2] }``
    """

    def __init__(self):
        self.motor = None
        self.hardwareMap = json.loads(open(PATH, "r").read())

    def setMotor(self, name: str):
        """
        Assigns the motor to ports specified in the hardware map

        :param name: the name of the motor in the hardware map
        """

        if name in self.hardwareMap:
            self.motor = gpiozero.Motor(self.hardwareMap[name][0], self.hardwareMap[name][1])
        else:
            logs.append("[ERROR] Cannot find motor \"" + name + "\" on hardware map.\n")

    def setSpeed(self, speed: float):
        """
        Sets the speed of the motor the function is called on.

        :param speed: speed of motor
        """

        if speed > 0:
            self.motor.forward(speed)
        if speed < 0:
            self.motor.backward(speed)
        if speed == 0:
            self.motor.stop()


class Servo:
    """
        The servo class represents a servo. It takes no inputs and has two functions,
        ``setMotor()`` and ``setPosition()``.

        To set a servo you need to have a file within the project directory called hardwareMap.txt, which specifies the
        names and ports of all connected servos and motors. This file should follow the format of:

        ``{ "name": port, "name": port }``
        """

    def __init__(self):
        self.servo = None
        self.hardwareMap = json.loads(open(PATH, "r").read())

    def setMotor(self, name: str):
        """
        Assigns the servo to port specified in the hardware map

        :param name: the name of the servo in the hardware map
        """

        if name in self.hardwareMap:
            self.servo = gpiozero.Servo(self.hardwareMap[name])
        else:
            logs.append("[ERROR] Cannot find servo \"" + name + "\" on hardware map.\n")

    def setSpeed(self, position: float):
        """
        Sets the position of the servo the function is called on.

        :param position: position of servo
        """

        self.servo.value = position


class Camera:
    """
    The controller class takes in no inputs, and instead reads from the first camera that it finds.
    The class stores the active camera connection and reads on a function call.
    Reading the camera data in your main loop is as simple as calling the read function such as:

    ``image = camera.readCameraData()``

    Which returns a Cv2 image array

    The class also includes two functions for encoding and decoding the above image for transmission,
    aptly named ``encode()`` and ``decode()``, and a function for resizing an image, named ``resize()``.
    """

    def __init__(self):
        self.capture = cv2.VideoCapture(0)

    def readCameraData(self):
        """
        Reads the current camera image

        :return: Cv2 image object
        """
        ret, frame = self.capture.read()
        while not ret:
            ret, frame = self.capture.read()
        return frame

    @staticmethod
    def encode(image, quality: int):
        """
        Encodes and compressed a Cv2 image to make it possible to send over the internet

        :param image: Cv2 image object
        :param quality: quality of Jpeg compression

        :return: Compressed byte array representation of input image
        """

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
        return cv2.imencode('.jpg', image, encode_param)[1].tobytes()

    @staticmethod
    def decode(image):
        """
        Decodes and decompresses an image encoded with *encode()*

        :param image: compressed byte array representation of image

        :return: Cv2 image object
        """

        npimg = numpy.frombuffer(image, numpy.uint8)
        return cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    @staticmethod
    def resize(image, x: int, y: int):
        """
        Resizes an image

        :param image: Cv2 image object
        :param x: image X
        :param y: image Y

        :return: resized Cv2 image object
        """
        return cv2.resize(image, (x, y), interpolation=cv2.INTER_AREA)


# all the GUI stuff
class UI:
    """
    The class is currently uses tkinter and is meant to be used as your viewport to the submarine.
    The class runs entirely in a separate thread and shows the video from an internal buffer.
    You can write to the ui by referencing the internal buffer such as such as:

    ``ui.frame = frame``

    Which is expected to be the frame data from the camera class.
    Camera and UI are separate to allow data connections through an
    internet connection or other similar connections without impeding functionality.

    You can specify which menus to be active or inactive with the menus input with the following possible menus:

    * connDetails
    * connStatus
    * input
    * output
    * custom

    The ui class can later be referenced to access or set:

    * **Video Frame** : ``ui.frame`` = most recent frame of video, the ui class reads this every 20ms
    * **Connection Status** : ``ui.connectionStatus`` = status where status is a string representing the current status
    * **Connection Info** : ``ui.connInfo`` = (ip, port) where the tuple of ip and port represents the ip and port you
    are listening from (these can be retrieved from the DataConnection class with conn.IP and conn.PORT respectively.)
    * **Input Data** : ``ui.controllerValues`` = controllerValues where controllerValues is the dictionary outputted
    by the Controller class

    :param videoSize: default video viewport size
    :param menus: dictionary of which menus to keep active. All are on by default.
    :param accentColor: accent color of the ui
    :param backgroundColor: background color of the ui
    """

    controllerValues = {'LeftJoystickY': 0, 'LeftJoystickX': 0, 'RightJoystickY': 0, 'RightJoystickX': 0,
                        'LeftTrigger': 0, 'RightTrigger': 0, 'LeftBumper': 0, 'RightBumper': 0, 'A': 0, 'X': 0, 'Y': 0,
                        'B': 0, 'LeftThumb': 0, 'RightThumb': 0, 'Menu': 0, 'Start': 0, 'DpadY': 0, 'DpadX': 0}

    menus = {}

    def _ui(self):
        win = Tk()
        win.title("Seamoth Homebase")
        win.config(bg=self.backgroundColor)

        if self.connInfo[1] == 1951:
            logs.append("Good luck MHS!")

        video = Label(win, background=self.accentColor)
        video.grid(row=0, column=0)

        # details
        details = Frame(win, bg=self.backgroundColor)
        details.grid(row=0, column=1, sticky=N)

        # conn details settings
        if self.menus.get("connDetails", True):
            connDetailsFrame = Frame(details, bg=self.backgroundColor)
            connDetailsFrame.grid(row=0, column=0, sticky=W, ipadx=10, pady=5, padx=5)
            Label(connDetailsFrame, text="CONNECTION DETAILS:", bg=self.backgroundColor, foreground="#ffffff").pack(side=TOP,
                                                                                                         anchor=W)

            connDetailsIP = Label(connDetailsFrame, text="1.1.1.1", bg=self.backgroundColor, foreground="#ffffff")
            connDetailsIP.pack(side=TOP, anchor=W)
            connDetailsPORT = Label(connDetailsFrame, text="1111", bg=self.backgroundColor, foreground="#ffffff")
            connDetailsPORT.pack(side=TOP, anchor=W)

        # conn status settings
        if self.menus.get("connStatus", True):
            connStatusFrame = Frame(details, bg=self.backgroundColor)
            connStatusFrame.grid(row=1, column=0, sticky=W, ipadx=10, pady=5, padx=5)
            Label(connStatusFrame, text="CONNECTION STATUS:", bg=self.backgroundColor, foreground="#ffffff").pack(side=TOP,
                                                                                                       anchor=W)

            connStatus = Label(connStatusFrame, text=self.connectionStatus, bg=self.backgroundColor, foreground="#ffffff")
            connStatus.pack(side=TOP, anchor=W)

        # input settings
        if self.menus.get("input", True):
            inputDetailsFrame = Frame(details, bg=self.backgroundColor)
            inputDetailsFrame.grid(row=2, column=0, sticky=W, ipadx=10, pady=5, padx=5)
            Label(inputDetailsFrame, text="INPUT DETAILS:", bg=self.backgroundColor, foreground="#ffffff").grid(row=0, column=0,
                                                                                                     sticky=W)

            inputDetailsJoyFrame = Frame(inputDetailsFrame, bg=self.backgroundColor)
            inputDetailsJoyFrame.grid(row=1, column=0, sticky=W, ipadx=10, pady=5, padx=5)
            inputJoyLeftX = Scale(inputDetailsJoyFrame, from_=-1, to=1, resolution=0.01, orient=HORIZONTAL,
                                  label="Left Joy X", showvalue=0, bg=self.backgroundColor, foreground="#ffffff",
                                  highlightthickness=0)
            inputJoyLeftX.pack(side=TOP, anchor=W)
            inputJoyLeftY = Scale(inputDetailsJoyFrame, from_=-1, to=1, resolution=0.01, orient=HORIZONTAL,
                                  label="Left Joy Y", showvalue=0, bg=self.backgroundColor, foreground="#ffffff",
                                  highlightthickness=0)
            inputJoyLeftY.pack(side=TOP, anchor=W)
            inputJoyRightX = Scale(inputDetailsJoyFrame, from_=-1, to=1, resolution=0.01, orient=HORIZONTAL,
                                   label="Right Joy X", showvalue=0, bg=self.backgroundColor, foreground="#ffffff",
                                   highlightthickness=0)
            inputJoyRightX.pack(side=TOP, anchor=W)
            inputJoyRightY = Scale(inputDetailsJoyFrame, from_=-1, to=1, resolution=0.01, orient=HORIZONTAL,
                                   label="Right Joy Y", showvalue=0, bg=self.backgroundColor, foreground="#ffffff",
                                   highlightthickness=0)
            inputJoyRightY.pack(side=TOP, anchor=W)

            inputDetailsTrigFrame = Frame(inputDetailsFrame, bg=self.backgroundColor)
            inputDetailsTrigFrame.grid(row=1, column=1, sticky=NW, ipadx=10, pady=5, padx=5)
            inputTrigRight = Scale(inputDetailsTrigFrame, from_=0, to=1, resolution=0.01, orient=HORIZONTAL,
                                   label="Left Trigger", showvalue=0, bg=self.backgroundColor, foreground="#ffffff",
                                   highlightthickness=0)
            inputTrigRight.pack(side=TOP, anchor=W)
            inputTrigLeft = Scale(inputDetailsTrigFrame, from_=0, to=1, resolution=0.01, orient=HORIZONTAL,
                                  label="Right Trigger", showvalue=0, bg=self.backgroundColor, foreground="#ffffff",
                                  highlightthickness=0)
            inputTrigLeft.pack(side=TOP, anchor=W)

        # errors
        if self.menus.get("output", True):
            logDetailsFrame = Frame(details, bg=self.backgroundColor, bd=1)
            logDetailsFrame.grid(row=3, column=0, sticky=W, pady=5, padx=5)

            Label(logDetailsFrame, text="OUTPUT:", bg=self.backgroundColor, foreground="#ffffff").grid(row=0, column=0, sticky=W)
            logBox = Text(logDetailsFrame, bg=self.backgroundColor, foreground=self.accentColor, height=15, width=60, relief=FLAT)
            logBox.grid(row=1, column=0, sticky=W)

        # settings
        settings = Frame(win, bg=self.backgroundColor)
        settings.grid(row=1, column=0, sticky=W)

        # custom values
        if self.menus.get("custom", True):
            customSettingsFrame = Frame(settings, bg=self.backgroundColor)
            customSettingsFrame.grid(row=0, column=0, sticky=W, pady=5, padx=5)

            Label(customSettingsFrame, text="CUSTOMIZABLE VALUES:", bg=self.backgroundColor, foreground="#ffffff").grid(row=0, column=0, sticky=W)

            customSettingsSlidersFrame = Frame(customSettingsFrame, bg=self.backgroundColor)
            customSettingsSlidersFrame.grid(row=1, column=0, sticky=W, pady=5, padx=5)

            customOne = Scale(customSettingsSlidersFrame, from_=0, to=100, resolution=1, orient=VERTICAL, label="1",
                              bg=self.backgroundColor, foreground="#ffffff", highlightthickness=0)
            customOne.pack(side=LEFT, anchor=W)
            customTwo = Scale(customSettingsSlidersFrame, from_=0, to=100, resolution=1, orient=VERTICAL, label="2",
                              bg=self.backgroundColor, foreground="#ffffff", highlightthickness=0)
            customTwo.pack(side=LEFT, anchor=W)
            customThree = Scale(customSettingsSlidersFrame, from_=0, to=100, resolution=1, orient=VERTICAL, label="3",
                                bg=self.backgroundColor, foreground="#ffffff", highlightthickness=0)
            customThree.pack(side=LEFT, anchor=W)
            customFour = Scale(customSettingsSlidersFrame, from_=0, to=100, resolution=1, orient=VERTICAL, label="4",
                               bg=self.backgroundColor, foreground="#ffffff", highlightthickness=0)
            customFour.pack(side=LEFT, anchor=W)
            customFive = Scale(customSettingsSlidersFrame, from_=0, to=100, resolution=1, orient=VERTICAL, label="5",
                               bg=self.backgroundColor, foreground="#ffffff", highlightthickness=0)
            customFive.pack(side=LEFT, anchor=W)

        # video settings
        if self.menus.get("video", True):
            videoSettingsFrame = Frame(settings, bg=self.backgroundColor)
            videoSettingsFrame.grid(row=0, column=1, sticky=N, pady=5, padx=5)

            Label(videoSettingsFrame, text="VIDEO SETTINGS:", bg=self.backgroundColor, foreground="#ffffff").grid(row=0, column=0, sticky=W)

            Button(videoSettingsFrame, text="fullscreen", bg=self.foregroundColor, foreground="#ffffff", command=self.toggleFullscreen).grid(row=1, column=0, sticky=W)

        # main loop
        def updateFrame():
            if self.fullscreen:
                cv2.imshow("hello", Camera.resize(self.frame, 1920, 1080))
            else:
                cv2.destroyAllWindows()

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

            if self.menus.get("output", True):
                logBox.delete("1.0", "end")
                for log in logs:
                    logBox.insert(INSERT, log)

            cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            img = PIL.Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            video.imgtk = imgtk
            video.configure(image=imgtk)
            if self.running:
                video.after(10, updateFrame)

        updateFrame()
        win.mainloop()

    def toggleFullscreen(self):
        self.fullscreen = not self.fullscreen

    def __init__(self, videoSize: tuple = (640, 480), menus: dict = {}, accentColor: str = "#ffffff", backgroundColor: str = "#3f3f3f", foregroundColor: str = "#585654"):
        self.running = True
        self.menus = menus
        self.frame = numpy.array(PIL.Image.new(mode="RGB", size=videoSize, color=(82, 82, 82)))
        self.connectionStatus = "Starting"
        self.connInfo = ("1.1.1.1", "1111")
        self.thread = Thread(target=self._ui, args=())
        self.thread.start()

        self.accentColor = accentColor
        self.backgroundColor = backgroundColor
        self.foregroundColor = foregroundColor
        self.fullscreen = False


# black magic voodoo, don't really feel like commenting all of it
class DataConnection:
    """
    The controller class is separated into two types, server and client, and is built on a UDP based architecture.
    All data received by the server is stored within its internal ``output`` buffer for asynchronous reading.
    This buffer stores the main message and the specified header as ``(header, message)``.

    You can send messages with the ``send()`` function.

    **header values 0-5 are reserved for system functions**
    """

    output = (0, b'')
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

            header = int(self.connection.recv(16).decode('utf-8'))
            message = self.connection.recv(int(msg_len), socket.MSG_WAITALL)
            if header == 1:
                logs.append("[ERROR]" + message.decode('utf-8'))
            if header == 2:
                logs.append("[WARNING]" + message.decode('utf-8'))
            if header == 3:
                logs.append("[TELEMETRY]" + message.decode('utf-8'))
            if header > 5:
                self.output = (header, message)

    def clientStart(self, ip: str, port: int):
        """
        Starts a client to connect to a server and will send received messages to the objects ``output`` buffer

        :param ip: ip of the server
        :param port: port of the server
        """

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

        self.thread = Thread(target=self._listen, args=())
        self.thread.start()

    def serverStart(self, port: int):
        """
        Starts a server and will send received messages to the objects ``output`` buffer

        :param port: port of the server
        """

        self.PORT = int(port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.IP, self.PORT))

        self.server.listen()
        self.connection, self.connectionAddress = self.server.accept()

        self.connected = True

        self.thread = Thread(target=self._listen, args=())
        self.thread.start()

        return self.IP

    def sendError(self, msg):
        """
        Sends an error message directly to the log

        :param msg: Error msg
        """
        self.send(msg, 1)

    def sendWarning(self, msg):
        """
        Sends a warning message data directly to the log

        :param msg: Warning msg
        """
        self.send(msg, 2)

    def sendTelemetry(self, msg):
        """
        Sends a telemetric message directly to the log

        :param msg: Telemetric msg
        """
        self.send(msg, 3)

    def send(self, msg: bytearray, header: int = 1):
        """
        Sends a message to all servers or clients connected to the program

        :param msg: message that you want to send in a byte form
        :param header: message header value **header values 0-5 are reserved for system functions**
        """

        send_length = str(len(msg)).encode('utf-8')
        send_length += b' ' * (64 - len(send_length))

        header = str(header).encode('utf-8')
        header += b' ' * (16 - len(header))

        self.connection.send(send_length)
        self.connection.send(header)
        self.connection.send(msg)
