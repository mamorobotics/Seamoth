import seamoth, cv2

def main():
    connection = seamoth.DataConnection()
    connection.serverStart(25565)

    while True:
        print(connection.output)

if __name__ == "__main__":
    main()
