import json
import seamoth


def main():
    conn = seamoth.DataConnection()
    controller = seamoth.Controller(0)

    ui = seamoth.UI()

    ui.connInfo = (conn.IP, 2000)
    ui.connectionStatus = "Waiting for Connection"
    conn.serverStart(2000)

    while True:
        ui.connectionStatus = f"Connected with {conn.connectionAddress[0]} on port {conn.PORT}"

        if conn.output[0] > 0:
            if conn.output[0] == 11:
                ui.frame = seamoth.Camera.decode(conn.output[1])

            ui.controllerValues = controller.controllerValues
            conn.send(json.dumps(controller.controllerValues.getDict()).encode('utf-8'), 12)


if __name__ == "__main__":
    main()
