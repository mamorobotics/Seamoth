import seamoth,os

gamepad = seamoth.Controller()

while True:
    os.system('cls')
    print(gamepad.controllerValues)