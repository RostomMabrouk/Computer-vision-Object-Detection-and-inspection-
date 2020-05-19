from datetime import date
import shutil
from os.path import isfile, join
from termcolor import colored
from opticam.logwriter import ColoredLogger
import cv2
from pynput import keyboard
from opticam.entrygate import op_main
import os
import json

def on_release(key):
    if key == keyboard.Key.enter:
        return False
    else:
        print('Please press Enter to continue')

def main():

    while True:
        allfiles1 = [f for f in os.listdir(path_data) if (isfile(join(path_data, f)))]
        for f in allfiles1:
            base = os.path.basename(f)
            file = os.path.splitext(base)[0]
            indices = file.split('_')
            side = indices[0]
            camera = indices[1]
            label = indices[2]
            tray = indices[3]
            Card = indices[4]
            file_index = indices[5]
            print("processing: ", os.path.join(path_data, base))
            pill_anal = op_main(base, path_data, path_text, path_model, commonfolder, output, SP_CLBT_C1, SP_CLBB_C1,
                                SP_CLBT_C2,
                                SP_CLBB_C2, LP_CLBT_C1, LP_CLBB_C1, LP_CLBT_C2, LP_CLBB_C2, SP_binmask1,
                                SP_binmask2, LP_binmask1, LP_binmask2, LOGGER, base, side, camera, label, tray,
                                Card, file_index, mode="test", print_out=False)
            pill_anal.processing()
            shutil.move(join(path_data, base), join(path_data, processed, base))

            if diagnosis:
                text = colored('Please press Enter to continue', 'red', attrs=['reverse', 'blink'])
                print(text)
                with keyboard.Listener(on_release=on_release) as listener:
                    listener.join()
                    pass
            else:
                pass



if __name__ == '__main__':
    Configuration_PATH = '.\Parameters\config.json'
    with open(Configuration_PATH, 'r') as f:
        data = f.read()
    obj = json.loads(data)
    path_data = obj["path_data"]
    path_text = obj["path_text"]
    path_model = obj["path_model"]
    day = str(date.today())
    commonfolder = "CommonFolder"
    output = day + "_output"
    processed = "processed"
    try:
        os.mkdir(join(path_data, commonfolder))
    except:
        pass
    f = open(join(path_data, commonfolder, "DinList1.json"), "a+")
    f.close()
    f = open(join(path_data, commonfolder, "DinList2.json"), "a+")
    f.close()
    try:
        os.mkdir(join(path_data, commonfolder, output))
    except:
        pass

    f = open(join(path_data, commonfolder, output, "outputs.txt"), "a+")
    f.close()

    try:
        os.mkdir(join(path_data, processed))
    except:
        pass
    SP_CLBT_C1 = int(obj["SP_CLBT_C1"])
    SP_CLBB_C1 = int(obj["SP_CLBB_C1"])
    SP_CLBT_C2 = int(obj["SP_CLBT_C2"])
    SP_CLBB_C2 = int(obj["SP_CLBB_C2"])
    LP_CLBT_C1 = int(obj["LP_CLBT_C1"])
    LP_CLBB_C1 = int(obj["LP_CLBB_C1"])
    LP_CLBT_C2 = int(obj["LP_CLBT_C2"])
    LP_CLBB_C2 = int(obj["LP_CLBB_C2"])
    SP_binmask1 = cv2.imread(obj["SP_binmask1"])
    SP_binmask2 = cv2.imread(obj["SP_binmask2"])
    LP_binmask1 = cv2.imread(obj["LP_binmask1"])
    LP_binmask2 = cv2.imread(obj["LP_binmask2"])
    LOGGER = ColoredLogger("Analysis", os.path.join(path_data, commonfolder, output, "outputs.txt"))
    diagnosis = False

    main()
