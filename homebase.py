import seamoth


def main():
    conn = seamoth.DataConnection()
    motor = seamoth.Motor()

    controller1 = seamoth.Controller(0)

    ui = seamoth.UI(videoSize=(640, 480))

    ui.connInfo = (conn.IP, 1951)
    ui.connectionStatus = "Waiting for Connection"
    conn.serverStart(1951)

    while True:
        if conn.connected and len(conn.output) > 3:
            ui.connectionStatus = f"Connected with {conn.connectionAddress[0]} on port {conn.PORT}"
            ui.frame = seamoth.Camera.decode(conn.output)
            ui.connectionStatus = "Connected to Sub"
            ui.controllerValues = controller1.controllerValues


if __name__ == "__main__":
    main()
