import seamoth


def main():
    conn = seamoth.DataConnection()

    ui = seamoth.UI(videoSize=(640, 480))

    ui.connInfo = (conn.IP, 1951)
    ui.connectionStatus = "Waiting for Connection"
    conn.serverStart(1951)

    while True:
        if conn.connected and len(conn.output[1]) > 3:
            ui.connectionStatus = f"Connected with {conn.connectionAddress[0]} on port {conn.PORT}"
            ui.frame = seamoth.Camera.decode(conn.output[1])


if __name__ == "__main__":
    main()
