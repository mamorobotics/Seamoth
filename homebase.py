import seamoth
import cv2

def main():
    conn = seamoth.DataConnection()
    ui = seamoth.UI("staticImage.png")

    conn.serverStart(1951)

    while True:
        if conn.connected and len(conn.output) > 3:
            ui.frame = seamoth.Camera.decode(conn.output)

if __name__ == "__main__":
    main()