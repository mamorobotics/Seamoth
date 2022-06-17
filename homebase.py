import seamoth

def main():
    video = seamoth.Camera()
    ui = seamoth.UI(video.readCameraData())

    while True:
        ui.frame = video.readCameraData()


if __name__ == "__main__":
    main()
