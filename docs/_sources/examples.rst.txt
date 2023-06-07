Examples
=================

Home Base
-----------------

The following is an example of the code that could be used on the home base:
::
    import seamoth

    def main():
        conn = seamoth.DataConnection(port=2000, server=True)
        controller = seamoth.Controller(0)

        ui = seamoth.UI()

        ui.connInfo = (conn.IP, 2000)
        ui.connectionStatus = "Waiting for Connection"

        def processFrame(message):
            if message[0] == 11:
                ui.setFrame(seamoth.Camera.resize(seamoth.Camera.decode(message[1]), 1280, 720))

        conn.onReceive(processFrame)

        while True:
            ui.connectionStatus = f"Connected with {conn.IP} on port {conn.PORT}"

            ui.controllerValues = controller.controllerValues
            conn.send(controller.controllerValues.toString().encode('utf-8'), 12)

    if __name__ == "__main__":
        main()

Submarine
-----------------

The following is an example of the code that could be used on the submarine:
::
    import seamoth

    def main():
        camera = seamoth.Cv2Camera(size=(960, 540))
        conn = seamoth.DataConnection("10.11.104.90", 2000, server=False)
        controllerValues = seamoth.ControllerValues()

        testMotor = seamoth.Motor()
        testServo = seamoth.Servo()

        testMotor.setMotor("testMotor")
        testServo.setServo("testServo")

        def processController(message):
            if message[0] == 12:
                controllerValues = seamoth.ControllerValues.fromString(message[1].decode('utf-8'))

        conn.onReceive(processController)

        while True:
            conn.send(seamoth.Camera.encode(camera.readCameraData(), 60), 11)

            testServo.setPosition(controllerValues.RightTrigger)
            testMotor.setSpeed(controllerValues.LeftJoystickY)

    if __name__ == "__main__":
        main()
