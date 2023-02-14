import seamoth


def main():
    camera = seamoth.Camera()
    conn = seamoth.DataConnection()

    conn.clientStart("0.0.0.0", 2000)

    while True:
        conn.send(seamoth.Camera.encode(seamoth.Camera.resize(camera.readCameraData(), 1248, 702), 90))


if __name__ == "__main__":
    main()
