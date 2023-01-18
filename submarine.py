import seamoth

def main():
    camera = Seamoth.Camera()
    conn = Seamoth.DataConnection()

    conn.clientStart("192.168.86.31", 1951)

    while True:
        conn.send(Seamoth.Camera.encode(camera.readCameraData(), 90))

if __name__ == "__main__":
    main()