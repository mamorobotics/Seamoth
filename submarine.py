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
