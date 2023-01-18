import seamoth

def main():
    conn = Seamoth.DataConnection()
    
    controller1 = Seamoth.Controller(0)

    ui = Seamoth.UI(videoSize=(640, 480))

    ui.connInfo = (conn.IP, 1951)
    ui.connectionStatus = "Waiting for Connection"
    conn.serverStart(1951)

    while True:
        if conn.connected and len(conn.output) > 3:
            ui.connectionStatus = f"Connected with {conn.connectionAddress[0]} on port {conn.PORT}"
            ui.frame = Seamoth.Camera.decode(conn.output)
            ui.connectionStatus = "Connected to Sub"
            ui.controllerValues = controller1.controllerValues

if __name__ == "__main__":
    main()