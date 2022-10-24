import Seamoth

def main():
    camera = Seamoth.Camera()
    conn = Seamoth.DataConnection()

    conn.clientStart("10.11.104.129", 1951)

    while True:
        conn.send(Seamoth.Camera.encode(camera.readCameraData(), 90))

if __name__ == "__main__":
    main()