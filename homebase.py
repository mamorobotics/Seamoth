import Seamoth

def main():
    conn = Seamoth.DataConnection()
    ui = Seamoth.UI("staticImage.png")

    ui.connectionStatus = "Searching for connection..."
    conn.serverStart(1951)

    while True:
        if conn.connected and len(conn.output) > 3:
            ui.connectionStatus = f"Connected with {conn.connectionAddress[0]} on port {conn.PORT}"
            ui.frame = Seamoth.Camera.decode(conn.output)
        

if __name__ == "__main__":
    main()