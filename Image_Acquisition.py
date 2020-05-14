import os
from os.path import isfile, join
import datetime
import psycopg2
import psycopg2.extensions
import clr
import numpy as np
from typing import Any
import shutil
from subprocess import Popen
import logging
from logging.handlers import RotatingFileHandler
import log
import time
import gclib

day = str(datetime.date.today())
Path = r"C:\Users\rmabrouk\Documents\data"
Output = day+"_Trigger_Log"
ContNum = [167]
try:
    os.mkdir(os.path.join(Path, Output))
except:
    pass
Acquisition = day+"_Acquisition"

try:
    os.mkdir(os.path.join(Path,  Acquisition))
except:
    pass
path_aq = os.path.join(Path, Acquisition)
LOGGER_SP1 = log.ColoredLogger("Log_SP_Cam1",  os.path.join(Path, Output, "Log_SP_Cam1.txt"))
LOGGER_SP2 = log.ColoredLogger("Log_SP_Cam2",  os.path.join(Path, Output, "Log_SP_Cam2.txt"))
LOGGER_LP1 = log.ColoredLogger("Log_LP_Cam1",  os.path.join(Path, Output, "Log_LP_Cam1.txt"))
LOGGER_LP2 = log.ColoredLogger("Log_LP_Cam2",  os.path.join(Path, Output, "Log_LP_Cam2.txt"))



# In PgAdmin RUN:
#      NOTIFY OPR_GET_NEXT_OERATION,'FOO';
IMG_COUNT1 = 1
IMG_COUNT2 = 1
IMG_COUNT3 = 1
IMG_COUNT4 = 1
notify = [1, 1]


def image_available_Cam_A(icImagingControl, evtargs):
    global IMG_COUNT1
    global path_aq
    global notify
    currentbuffer = icImagingControl.ImageBuffers[evtargs.bufferIndex]
    path = path_aq+"\SP_Cam2_{}_{}_{}.bmp".format(notify[0], IMG_COUNT1, notify[1])
    currentbuffer.SaveAsBitmap(path)
    print("Saving: ", path)
    LOGGER_SP1.debug("Trigger OK, saving image: "+path)
    IMG_COUNT1 += 1


def image_available_Cam_B(icImagingControl, evtargs):
    global IMG_COUNT2
    global notify
    global path_aq
    currentbuffer = icImagingControl.ImageBuffers[evtargs.bufferIndex]
    path = path_aq+"\SP_Cam1_{}_{}_{}.bmp".format(notify[0], IMG_COUNT2,  notify[1])
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
    path = path_aq+"\LP_Cam1_{}_{}_{}.bmp".format(notify[0],  IMG_COUNT3, notify[1])
    currentbuffer.SaveAsBitmap(path)
    currentbuffer.Unlock()
    print("Saving: ", path)
    LOGGER_LP1.debug("Trigger OK, saving image: "+path)
    IMG_COUNT3 += 1


def image_available_Cam_D(icImagingControl, evtargs):
    global IMG_COUNT4
    global notify
    currentbuffer = icImagingControl.ImageBuffers[evtargs.bufferIndex]
    path = path_aq+"\LP_Cam2_{}_{}_{}.bmp".format(notify[0],  IMG_COUNT4, notify[1])
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
    #Popen(['Python', 'Training_file_version0.py'])
    global notify
    global path1
    ic = ICImagingControl()

    all_cameras = [MyCamera(ICImagingControl(), i) for i in range(len(ic.Devices))]
    my_dict = {camera.sn: camera for camera in all_cameras}
    # 33
   # Cam_dict = {'A': my_dict["46810489"], 'B': my_dict["20910362"], 'C': my_dict["19910455"], 'D': my_dict["19910458"]}

    # 272
    Cam_dict = {'A': my_dict["35910211"], 'B': my_dict["35910209"], 'C': my_dict["19910458"], 'D': my_dict["35910218"]}

    print(Cam_dict["A"].ic.DeviceValid, Cam_dict["A"].ic.Device, Cam_dict["A"].sn)
    print(Cam_dict["B"].ic.DeviceValid, Cam_dict["B"].ic.Device, Cam_dict["B"].sn)
    print(Cam_dict["C"].ic.DeviceValid, Cam_dict["C"].ic.Device, Cam_dict["C"].sn)
    print(Cam_dict["D"].ic.DeviceValid, Cam_dict["D"].ic.Device, Cam_dict["D"].sn)
    Cam_dict["A"].ic.LoadDeviceStateFromFile(".\Parameters\Camera_A.dat", 0)
    Cam_dict["B"].ic.LoadDeviceStateFromFile(".\Parameters\Camera_B.dat", 0)
    Cam_dict["C"].ic.LoadDeviceStateFromFile(".\Parameters\Camera_C.dat", 0)
    Cam_dict["D"].ic.LoadDeviceStateFromFile(".\Parameters\Camera_D.dat", 0)

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
    galil = gclib.py()
    #controller_ip = '192.168.75.14'
    controller_ip = 'COM3'
    timeout_ms = 5000
    galil.GOpen('{} --direct --timeout {}'.format(controller_ip, timeout_ms))
    format = 37
    tg = 1
    tgl = 0
    mass = 0
    frg = 0
    v1 = 1
    v2 = 1
    v3 = 1
    v4 = 1
    v5 = 1
    v6 = 1
    v7 = 1
    v8 = 0

    for itr_number in range(10000):
        for counter in ContNum:
            ran = int((counter - 1) / 25) + 1
            col = (counter - int((counter - 1) / 25) * 25)
            for ctr in range(7, 8):
                for per_num in range(1, 2):
                    galil.GCommand('com= 1; ran={}; col={};format={}; tg={}; tgl={}; mass={}; frg={}; v1={}; v2={};  \
                               v3={};v4={}; v5={}; v6={}; v7={}; v8={}; carte={}; per={};\
                               chk=com+ran+col+v1+v2+v3+v4+v5+v6+v7+v8+format+carte+per+tg+tgl+frg+mass;ala=0; exe=1'.format(
                        ran,
                        col,
                        format,
                        tg, tgl,
                        mass, frg,
                        v1, v2,
                        v3, v4,
                        v5, v6,
                        v7, v8,
                        ctr,
                        per_num))
                    fin = False
                    while not fin:
                        resultat = galil.GCommand('exe=?;ala=?')
                        split_result = [float(r) for r in resultat.split(':')]
                        if split_result[0] == 0 or split_result[1] == 1:
                            fin = True

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