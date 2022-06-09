import seamoth, time

def main():
    connection = seamoth.DataConnection()
    connection.clientStart('192.168.56.1', 25565)

    time.sleep(2)

    connection.send('Hello')

if __name__ == "__main__":
    main()