import json
import seamoth


def main():
    conn = seamoth.DataConnection()
    controller = seamoth.Controller(0)

    ui = seamoth.UI(videoSize=(1248, 702), accentColor="#cf4100", backgroundColor="#000000")

    ui.connInfo = (conn.IP, 1951)
    ui.connectionStatus = "Waiting for Connection"
    conn.serverStart(1951)

    while True:
        if conn.output[0] > 0:
            ui.connectionStatus = f"Connected with {conn.connectionAddress[0]} on port {conn.PORT}"
            ui.frame = seamoth.Camera.decode(conn.output[1])
            ui.controllerValues = controller.controllerValues
            conn.send(json.dumps(controller.controllerValues).encode('utf-8'))


if __name__ == "__main__":
    main()
