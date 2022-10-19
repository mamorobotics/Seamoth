from http import client
import seamoth

def main():
    camera = seamoth.Camera()
    conn = seamoth.DataConnection()

    conn.clientStart("10.11.104.216", 1951)

    while True:
        conn.send(seamoth.Camera.encode(camera.readCameraData()))

if __name__ == "__main__":
    main()