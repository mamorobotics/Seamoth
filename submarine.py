import seamoth, time, math


def main():
    def clamp(i, maxN, minN):
        return max(min(i, maxN), minN)

    width = 1280
    height = 720
    camera1 = seamoth.Cv2Camera(width, height)
    camera2 = seamoth.PiCamera(size=(width, height))
    conn = seamoth.DataConnection("192.168.1.1", 8080, server=False)
    controllerValues = seamoth.ControllerValues()
    camQual = 60;
    camNum = 1;
    
    camInc = 0
    clawInc = 0.6

    LeftJoystickY = 0
    LeftJoystickX = 0
    RightJoystickY = 0
    RightJoystickX = 0
    LeftTrigger = 0
    RightTrigger = 0
    LeftBumper = 0
    RightBumper = 0
    A = 0
    X = 0
    Y = 0
    B = 0
    DpadY = 0
    DpadX = 0
    
    clawClose = seamoth.Servo();
    clawClose.setServo("clawClose")
    clawRot = seamoth.Servo();
    clawRot.setServo("clawRot")

    clawClose.setPosition(1)
    clawRot.setPosition(clawInc)

    fowL = seamoth.Motor();
    fowL.setMotor("fowLMotor")
    upR = seamoth.Motor();
    upR.setMotor("upRMotor")
    upL = seamoth.Motor();
    upL.setMotor("upLMotor")
    fowR = seamoth.Motor();
    fowR.setMotor("fowRMotor")
    
    time.sleep(2)
    prjoyy = 0
    prjoyx = 0
    pljoyy = 0
    pljoyx = 0
    
    #conn.send(b'hello', 11)
    while True:
        header,message = conn.msg_buff
        print(header)
        for i in range(len(header)):
            if int(header[i]) == 5:
                controllerValueList = message[i].split("!")

                LeftJoystickX = float(controllerValueList[0])
                LeftJoystickY = float(controllerValueList[1])
                RightJoystickX = float(controllerValueList[2])
                RightJoystickY = float(controllerValueList[3])
                LeftTrigger = float(controllerValueList[4])
                RightTrigger = float(controllerValueList[5])
                LeftBumper = int(controllerValueList[10])
                RightBumper = int(controllerValueList[11])
                A = int(controllerValueList[6])
                X = int(controllerValueList[8])
                Y = int(controllerValueList[9])
                B = int(controllerValueList[7])
                up = int(controllerValueList[12])
                right = int(controllerValueList[15])
                down = int(controllerValueList[13])
                left = int(controllerValueList[14])
               
                inc = 0.05

                if up == 1:
                       camInc+= inc
                elif down == 1:
                       camInc-= inc
                elif right == 1:
                       clawInc += inc
                elif left == 1:
                       clawInc -= inc

                clawInc = clamp(clawInc, 1.0, 0.0)

                clawClose.setPosition(1-LeftTrigger)
                clawRot.setPosition(clawInc)
                

    #            fowL.setSpeed(A)
     #           fowR.setSpeed(-B

                upL.setSpeed(-RightJoystickY)
                upR.setSpeed(RightJoystickY)

                X = 0.2*LeftJoystickX + 0.8*pljoyx
                Y = 0.2*LeftJoystickY + 0.8*pljoyy

                if ((pljoyy > 0) == (LeftJoystickY > 0)) or ((pljoyx > 0) == (LeftJoystickX > 0)):
                    z = math.sqrt(X * X + Y * Y)
                    if z != 0:
                        angle = math.acos(math.fabs(X) / z) * 180 / math.pi
                        tcoeff = -1 + (angle / 90) * 2
                        turn = tcoeff * math.fabs(math.fabs(Y) - math.fabs(X))
                        mov = max(math.fabs(Y), math.fabs(X))
                        if (X >= 0 and Y >= 0) or (X < 0 and Y < 0):
                            rawLeft = mov
                            rawRight = turn
                        else:
                            rawRight = mov
                            rawLeft = turn
                        if Y < 0:
                            rawLeft = 0 - rawLeft
                            rawRight = 0 - rawRight
                        fowL.setSpeed(rawLeft)
                        fowR.setSpeed(rawRight)
                else:
                    fowL.setSpeed(0)
                    fowR.setSpeed(0)
            elif int(header[i]) == 6:
                camSettings = message[i].split("!")
                if camSettings[0] == 'qual':
                    camera2.camQual = int(camSettings[1])
                    seamoth.Camera.setCamQual(int(camSettings[1]))
                elif camSettings[0] == 'cam':
                    seamoth.Camera.setCamNum(int(camSettings[1]))
            prjoyy = RightJoystickY
            prjoyx = RightJoystickX
            pljoyy = LeftJoystickY
            pljoyx = LeftJoystickX
        conn.send(seamoth.Camera.readCameraData(camera1, camera2), 4)

if __name__ == "__main__":
    main()
