import seamoth


def main():
    conn = seamoth.DataConnection(port=2000, server=True)
    controller = seamoth.Controller(0)

    ui = seamoth.UI()

    ui.connInfo = (conn.IP, 2000)
    ui.connectionStatus = "Waiting for Connection"

    def processFrame(message):
        if message[0] == 11:
            ui.setFrame(seamoth.Camera.resize(seamoth.Camera.decode(message[1]), 1280, 720))

    conn.onReceive(processFrame)

    while True:
        ui.connectionStatus = f"Connected with {conn.IP} on port {conn.PORT}"

        ui.controllerValues = controller.controllerValues
        conn.send(controller.controllerValues.toString().encode('utf-8'), 12)


if __name__ == "__main__":
    main()
