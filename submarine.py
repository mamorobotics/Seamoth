import seamoth

def main():
    camera = seamoth.Camera()
    conn = seamoth.DataConnection()

    conn.clientStart("10.0.0.144", 1951)

    while True:
        conn.send(seamoth.Camera.encode(camera.readCameraData(), 90))

if __name__ == "__main__":
    main()