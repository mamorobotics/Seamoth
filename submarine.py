import seamoth


def main():
    camera = seamoth.Camera()
    conn = seamoth.DataConnection()

    testMotor = seamoth.Motor()
    testServo = seamoth.Servo()

    controllerValues = seamoth.ControllerValues()

    testMotor.setMotor("testMotor")
    testServo.setServo("testServo")

    conn.clientStart("10.11.105.44", 2000)

    while True:
        conn.send(seamoth.Camera.encode(camera.readCameraData(), 90))

        if conn.output[0] == 12:
            controllerValues = seamoth.ControllerValues.fromString(conn.output[1].decode('utf-8'))

        testServo.setPosition(controllerValues.RightTrigger)

        testMotor.setSpeed(controllerValues.LeftJoystickY)


if __name__ == "__main__":
    main()
