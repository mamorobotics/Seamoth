Examples
=================

Home Base
-----------------

The following is an example of the code that could be used on the home base:
::
    import seamoth
    

    def main():
        conn = seamoth.DataConnection()
        controller = seamoth.Controller(0)

        ui = seamoth.UI()

        ui.connInfo = (conn.IP, 2000)
        ui.connectionStatus = "Waiting for Connection"
        conn.serverStart(2000)

        while True:
            ui.connectionStatus = f"Connected with {conn.connectionAddress[0]} on port {conn.PORT}"

            if conn.output[0] > 0:
                if conn.output[0] == 11:
                    ui.setFrame(seamoth.Camera.decode(conn.output[1]))

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
        camera = seamoth.Camera()
        conn = seamoth.DataConnection()

        testMotor = seamoth.Motor()
        testServo = seamoth.Servo()

        controllerValues = seamoth.ControllerValues()

        testMotor.setMotor("testMotor")
        testServo.setServo("testServo")

        conn.clientStart("0.0.0.0", 2000)

        while True:
            conn.send(seamoth.Camera.encode(seamoth.Camera.resize(camera.readCameraData(), 1248, 702), 90))

            if conn.output[0] == 12:
                controllerValues = seamoth.ControllerValues.fromString(conn.output[1].decode('utf-8'))

            testServo.setPosition(controllerValues.RightTrigger)

            testMotor.setSpeed(controllerValues.LeftJoystickY)

    if __name__ == "__main__":
        main()

