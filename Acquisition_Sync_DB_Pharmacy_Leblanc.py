import os
from os.path import isfile, join
import datetime
import psycopg2
import psycopg2.extensions
import clr
import numpy as np
from typing import Any
import shutil
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import log

day = str(datetime.date.today())
Path = r"C:\Users\RMabrouk\PycharmProjects\Test_for_pharmacy"
Output = day+"_Trigger_Log"

try:
    os.mkdir(os.path.join(Path, Output))
except:
    pass
Aquisition = day+"_Aquisition"

try:
    os.mkdir(os.path.join(Path,  Aquisition))
except:
    pass
path_aq = os.path.join(Path, Aquisition)
LOGGER_SP1 = log.ColoredLogger("Log_SP_Cam1",  os.path.join(Path, Output, "Log_SP_Cam1.txt"))
LOGGER_SP2 = log.ColoredLogger("Log_SP_Cam2",  os.path.join(Path, Output, "Log_SP_Cam2.txt"))
LOGGER_LP1 = log.ColoredLogger("Log_LP_Cam1",  os.path.join(Path, Output, "Log_LP_Cam1.txt"))
LOGGER_LP2 = log.ColoredLogger("Log_LP_Cam2",  os.path.join(Path, Output, "Log_LP_Cam2.txt"))



conn = psycopg2.connect(database="xxxxxxxxxx", user="xxxxxxxxxx", password="xxxxxxxxxxx")
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

curs = conn.cursor()
curs.execute("LISTEN OPR_GET_NEXT_OERATION;")
#curs.execute("LISTEN OPR_SET_OERATION_DONE;")

# In PgAdmin RUN:
#      NOTIFY OPR_GET_NEXT_OERATION,'FOO'; 
IMG_COUNT1 = 1
IMG_COUNT2 = 1
IMG_COUNT3 = 1
IMG_COUNT4 = 1
notify = None




# --------------------------------
# Decision functions:
# --------------------------------

# This function detect double pllis or semi-pill accoding to two criteria 1) solidity of the object calculated as the
# convex defect over the perimeter. 2) exceed the threshold of the max object size or less than the threshold of min
# object size.
#src = "C:\Synsoft\Fichier_Recu\Prescription_20190618_124745.txt"
#dst = "C:\Synsoft\Fichier_Entrant"
#shutil.copy2(src, dst)

def image_available_Cam_A(icImagingControl, evtargs):
    global IMG_COUNT1
    global notify
    global path_aq
    currentbuffer = icImagingControl.ImageBuffers[evtargs.bufferIndex]
    path = path_aq+"\SP_Cam1_{}.bmp".format(IMG_COUNT1)
    currentbuffer.SaveAsBitmap(path)
    #print("Saving: ", path)
    LOGGER_SP1.debug("Trigger OK, saving image: "+path)
    IMG_COUNT1 += 1


def image_available_Cam_B(icImagingControl, evtargs):
    global IMG_COUNT2
    global notify
    global path_aq
    currentbuffer = icImagingControl.ImageBuffers[evtargs.bufferIndex]
    path = path_aq+"\SP_Cam2_{}.bmp".format(IMG_COUNT2)
    currentbuffer.SaveAsBitmap(path)
    print("Saving: ", path)
    LOGGER_SP2.debug("Trigger OK, saving image: "+path)
    IMG_COUNT2 += 1


def image_available_Cam_C(icImagingControl, evtargs):
    global IMG_COUNT3
    global notify
    global path_aq
    currentbuffer = icImagingControl.ImageBuffers[evtargs.bufferIndex]
    currentbuffer.Lock() 
    path = path_aq+"\LP_Cam1_{}.bmp".format(IMG_COUNT3)
    currentbuffer.SaveAsBitmap(path)
    currentbuffer.Unlock()
    print("Saving: ", path)
    LOGGER_LP1.debug("Trigger OK, saving image: "+path)
    IMG_COUNT3 += 1


def image_available_Cam_D(icImagingControl, evtargs):
    global IMG_COUNT4
    global notify
    currentbuffer = icImagingControl.ImageBuffers[evtargs.bufferIndex]
    path = path_aq+"\LP_Cam2_{}.bmp".format(IMG_COUNT4)
    currentbuffer.SaveAsBitmap(path)
    print("Saving: ", path)
    LOGGER_LP2.debug("Trigger OK, saving image: "+path)
    IMG_COUNT4 += 1


class MyCamera(object):
    def __init__(self, ic, index):
        self.index = index
        self.ic = ic
        self.name = self.ic.Devices[index].Name
        self.ic.Device = self.name
        _, self.sn = self.ic.Devices[index].GetSerialNumber("")


def main():
    global notify
    global path1
    subprocess.Popen(["python", "main_opticam.py", path1])
    ic = ICImagingControl()

    all_cameras = [MyCamera(ICImagingControl(), i) for i in range(len(ic.Devices))]
    my_dict = {camera.sn: camera for camera in all_cameras}

    Cam_dict = {'A': my_dict["20910362"], 'B': my_dict["46810489"], 'C': my_dict["19910455"], 'D': my_dict["19910458"]}

    print(Cam_dict["A"].ic.DeviceValid, Cam_dict["A"].ic.Device, Cam_dict["A"].sn)
    print(Cam_dict["B"].ic.DeviceValid, Cam_dict["B"].ic.Device, Cam_dict["B"].sn)
    print(Cam_dict["C"].ic.DeviceValid, Cam_dict["C"].ic.Device, Cam_dict["C"].sn)
    print(Cam_dict["D"].ic.DeviceValid, Cam_dict["D"].ic.Device, Cam_dict["D"].sn)
    Cam_dict["A"].ic.LoadDeviceStateFromFile("tis_usb.dat", 0)
    Cam_dict["B"].ic.LoadDeviceStateFromFile("tis_usb2.dat", 0)
    Cam_dict["C"].ic.LoadDeviceStateFromFile("tis_usb.dat", 0)
    Cam_dict["D"].ic.LoadDeviceStateFromFile("tis_usb2.dat", 0)

    Cam_dict["A"].ic.LiveDisplay = False
    Cam_dict["B"].ic.LiveDisplay = False
    Cam_dict["C"].ic.LiveDisplay = False
    Cam_dict["D"].ic.LiveDisplay = False

    Cam_dict["A"].ic.LiveDisplayDefault = False
    Cam_dict["B"].ic.LiveDisplayDefault = False
    Cam_dict["C"].ic.LiveDisplayDefault = False
    Cam_dict["D"].ic.LiveDisplayDefault = False

    Cam_dict["A"].ic.LiveCaptureContinuous = True
    Cam_dict["B"].ic.LiveCaptureContinuous = True
    Cam_dict["C"].ic.LiveCaptureContinuous = True
    Cam_dict["D"].ic.LiveCaptureContinuous = True

    # ImageAvailable callback
    Cam_dict["A"].ic.LiveStart()
    Cam_dict["B"].ic.LiveStart()
    Cam_dict["C"].ic.LiveStart()
    Cam_dict["D"].ic.LiveStart()

    Cam_dict["A"].ic.ImageAvailable += image_available_Cam_A
    Cam_dict["B"].ic.ImageAvailable += image_available_Cam_B
    Cam_dict["C"].ic.ImageAvailable += image_available_Cam_C
    Cam_dict["D"].ic.ImageAvailable += image_available_Cam_D
    print("Waiting for notifications on channel......")
    while True:
        conn.poll()
        if conn.notifies:
            raw = conn.notifies.pop(0)
            notify = raw.payload.split(';')
            #print("Got NOTIFY:", notify[-1])
            #print("tiges = ", notify[29])

    Cam_dict["A"].ic.LiveStop()
    Cam_dict["B"].ic.LiveStop()
    Cam_dict["C"].ic.LiveStop()
    Cam_dict["D"].ic.LiveStop()



if __name__ == '__main__':
    netdll_path = r"C:\Program Files\Common Files\IC Imaging Control 3.4\bin\v4.0.30319\x64\TIS.Imaging.ICImagingControl34.dll"
    print(netdll_path)
    clr.AddReference(netdll_path)
    from TIS.Imaging import ICImagingControl, VCDGUIDs, VCDIDs, ImageBuffer
    from TIS.Imaging.VCDHelpers import VCDSimpleModule
    main()
