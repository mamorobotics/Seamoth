import seamoth


def main():
    camera = seamoth.Cv2Camera(size=(960, 540))
    conn = seamoth.DataConnection("169.254.85.174", 1951, server=False)
    controllerValues = seamoth.ControllerValues()

    def processController(message):
        if message[0] == 12:
            controllerValues = seamoth.ControllerValues.fromString(message[1].decode('utf-8'))

    conn.onReceive(processController)

    while True:
        conn.send(seamoth.Camera.encode(camera.readCameraData(), 60), 11)

if __name__ == "__main__":
    main()
