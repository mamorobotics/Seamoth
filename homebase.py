import Seamoth

def main():
    conn = Seamoth.DataConnection()
    ui = Seamoth.UI("G:\Seamoth\staticImage.png")

    ui.connectionStatus = "Waiting for Connection"
    conn.serverStart(1951)
    
    while True:
        if conn.connected and len(conn.output) > 3:
            ui.connectionStatus = f"Connected with {conn.connectionAddress[0]} on port {conn.PORT}"
            ui.frame = Seamoth.Camera.decode(conn.output)
            ui.connectionStatus = "Connected to Sub"
        

if __name__ == "__main__":
    main()