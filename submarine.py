import Seamoth

def main():
    camera = Seamoth.Camera()
    conn = Seamoth.DataConnection()

    conn.clientStart("192.168.86.42", 1951)

    while True:
        conn.send(Seamoth.Camera.encode(camera.readCameraData()))

if __name__ == "__main__":
    main()