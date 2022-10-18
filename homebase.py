import seamoth
import cv2

def main():
    conn = seamoth.DataConnection()
    ui = seamoth.UI("staticImage.png")

    conn.serverStart(1951)
    print(conn.IP)

    while True:
        ui.frame = conn.output

if __name__ == "__main__":
    main()