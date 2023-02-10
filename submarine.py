import seamoth

def main():
    camera = seamoth.Camera()
    conn = seamoth.DataConnection()

    conn.clientStart("0.0.0.0", 2000)

    while True:
        conn.send(seamoth.Camera.encode(camera.readCameraData(), 90))

if __name__ == "__main__":
    main()