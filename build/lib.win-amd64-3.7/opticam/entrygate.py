import json
import os
from os.path import isfile, join

import cv2
import numpy as np
from analysis import features_vector
from decision import Decision
from segmentation import SynMedSeg
import cProfile

"""def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()
    return profiled_func
"""
from cProfile import Profile
import pstats


def profile(sort_args=['cumulative'], print_args=[10]):
    profiler = Profile()

    def decorator(fn):
        def inner(*args, **kwargs):
            result = None
            try:
                result = profiler.runcall(fn, *args, **kwargs)
            finally:
                stats = pstats.Stats(profiler)
                stats.strip_dirs().sort_stats(*sort_args).print_stats(*print_args)
            return result
        return inner
    return decorator
class op_main():
    def __init__(self, file_name, path_data, path_text, path_model, commonfolder, output, SP_CLBT_C1, SP_CLBB_C1, SP_CLBT_C2,
                 SP_CLBB_C2, LP_CLBT_C1, LP_CLBB_C1, LP_CLBT_C2, LP_CLBB_C2, SP_binmask1,
                 SP_binmask2, LP_binmask1, LP_binmask2, LOGGER, base, side, camera, label, tray, Card, file_index, mode,
                 print_out):
        self.file_name = file_name
        self.path_data = path_data
        self.path_text = path_text
        self.path_model = path_model
        self.commonfolder = commonfolder
        self.output = output
        self.SP_CLBT_C1 = SP_CLBT_C1
        self.SP_CLBB_C1 = SP_CLBB_C1
        self.SP_CLBT_C2 = SP_CLBT_C2
        self.SP_CLBB_C2 = SP_CLBB_C2
        self.LP_CLBT_C1 = LP_CLBT_C1
        self.LP_CLBB_C1 = LP_CLBB_C1
        self.LP_CLBT_C2 = LP_CLBT_C2
        self.LP_CLBB_C2 = LP_CLBB_C2
        self.SP_binmask1 = SP_binmask1
        self.SP_binmask2 = SP_binmask2
        self.LP_binmask1 = LP_binmask1
        self.LP_binmask2 = LP_binmask2
        self.LOGGER = LOGGER
        self.base = base
        self.side = side
        self.camera = camera
        self.label = label
        self.tray = tray
        self.Card = Card
        self.file_index = file_index
        self.LPLNoise = 18000
        self.LPSNoise = 4000
        self.SPLNoise = 5000
        self.SPSNoise = 800
        self.mode = mode
        self.training_set = "training_set"
        self.print_out = print_out
    #@profile(sort_args=['cumulative', 'name'], print_args=[.8, 'init'])
    def processing(self):
        file = join(self.path_data, self.file_name)
        if self.side == "LP" and self.camera == "Cam1":
            img = cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB)
            cam = 1
            if self.mode == "test":
                self.analysis(img, self.LP_binmask1, self.LP_CLBT_C1, self.LP_CLBB_C1, self.LPLNoise, self.LPSNoise,
                              cam)
            elif self.mode == "training":
                self.training(img, self.LP_binmask1, self.LP_CLBT_C1, self.LP_CLBB_C1, self.LPLNoise, self.LPSNoise,
                              cam)
        elif self.side == "LP" and self.camera == "Cam2":
            img = cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB)
            cam = 2
            if self.mode == "test":
                self.analysis(img, self.LP_binmask2, self.LP_CLBT_C2, self.LP_CLBB_C2, self.LPLNoise, self.LPSNoise,
                              cam)
            elif self.mode == "training":
                self.training(img, self.LP_binmask2, self.LP_CLBT_C2, self.LP_CLBB_C2, self.LPLNoise, self.LPSNoise,
                              cam)
        elif self.side == "SP" and self.camera == "Cam1":
            img = cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB)
            cam = 1
            if self.mode == "test":
                self.analysis(img, self.SP_binmask1, self.SP_CLBT_C1, self.SP_CLBB_C1, self.SPLNoise, self.SPSNoise,
                              cam)
            elif self.mode == "training":
                self.training(img, self.SP_binmask1, self.SP_CLBT_C1, self.SP_CLBB_C1, self.SPLNoise, self.SPSNoise,
                              cam)

        elif self.side == "SP" and self.camera == "Cam2":
            img = cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB)
            cam = 2
            if self.mode == "test":
                self.analysis(img, self.SP_binmask2, self.SP_CLBT_C2, self.SP_CLBB_C2, self.SPLNoise, self.SPSNoise,
                              cam)
            elif self.mode == "training":
                self.training(img, self.SP_binmask2, self.SP_CLBT_C2, self.SP_CLBB_C2, self.SPLNoise, self.SPSNoise,
                              cam)

    def analysis(self, img, binmask, CLBT, CLBB, L_exp_noise, S_exp_noise,  cam):
        maskfinal = np.zeros(img.shape, np.uint8)
        ClassExist = False
        my_dict = dict()
        img_seg = SynMedSeg(img, binmask, CLBT, CLBB, L_exp_noise, S_exp_noise, cam, self.side)
        regions = img_seg.labeledRegions()
        for props in regions:
            my_dict[props.label] = (props.bbox[1], props.bbox[0], props.bbox[3] - props.bbox[1],
                                    props.bbox[2] - props.bbox[0])
        for key, values in my_dict.items():
            mask = np.zeros(img.shape[:2], np.uint8)
            if cam == 1:
                pipes_num = 4
            else:
                pipes_num = 6
            if key < pipes_num:
                mask, pipe_number = img_seg.segmentation(values, mask, pad=100)

                if cam == 2:
                    pipe_number += 3
                mask[mask != 0] = 1
                maskfinal += np.stack((mask,) * 3, axis=-1)
                pill = features_vector(img, mask, (pipe_number - 1), cam, self.side)
                if self.print_out:
                    print(pill.get_features())
                if len(pill.get_features()) != 0:
                    model_file = join(self.path_model, "Classification_model_Cam" + str(cam) + "_" +
                                      self.label.lstrip("0") + ".sav")
                    if isfile(model_file):
                        ClassExist = True
                        self.save_data_test(str(pipe_number), pill.get_features(), cam, ClassExist)
                        sys_dec = Decision(self.path_data, self.path_text, self.path_model, mask, self.label, self.side, cam,
                                           pill.get_features(), self.print_out)
                        sys_dec.duplicate()
                        sys_dec.classification()
                        if sys_dec.dup:
                            self.LOGGER.debug(
                                join(self.path_data, self.file_name) + " :Pipe number " + str(pipe_number) + ": " + "Event_DC")
                            cv2.rectangle(maskfinal, (values[0], values[1]), (values[0] +
                                                                              values[2], values[1] + values[3]),
                                          (255, 0, 0), 8)
                        elif sys_dec.size_max_T:
                            self.LOGGER.debug(
                                join(self.path_data, self.file_name) + " :Pipe number " + str(pipe_number) + ": " + "Event_x")
                            cv2.rectangle(maskfinal, (values[0], values[1]), (values[0] +
                                                                              values[2], values[1] + values[3]),
                                          (255, 0, 0), 8)
                        elif sys_dec.size_min_T:
                            self.LOGGER.debug(
                                join(self.path_data, self.file_name) + " :Pipe number " + str(pipe_number) + ": " + "Event_n")
                            cv2.rectangle(maskfinal, (values[0], values[1]), (values[0] +
                                                                              values[2], values[1] + values[3]),
                                          (255, 0, 0), 8)
                        elif not sys_dec.dec_return:
                            self.LOGGER.debug(
                                join(self.path_data, self.file_name) + " :Pipe number " + str(pipe_number) + ": " + "Event_P")
                            cv2.rectangle(maskfinal, (values[0], values[1]), (values[0] + values[2],
                                                                              values[1] + values[3]), (255, 0, 0), 8)
                        else:
                            self.LOGGER.debug(
                                join(self.path_data, self.file_name) + " :Pipe number " + str(pipe_number) + ": " + "True")
                    else:
                        self.save_data_test(str(pipe_number), pill.get_features(), cam, ClassExist)
                        path = join(self.path_data, self.commonfolder, "DinList"+str(cam)+".json")
                        with(open(path, "r")) as a_file:
                            json_object = json.load(a_file)
                        if self.label in json_object:
                            cpt = int(json_object[self.label])
                            cpt += 1
                            json_object[self.label] = str(cpt)
                        else:
                            json_object[self.label] = "1"
                        with open(path, "w") as f:
                            json.dump(json_object, f, indent=4)
                else:
                    pass
        imgr = img * maskfinal
        self.save_image_test(imgr, ClassExist)
    def training(self, img, binmask, CLBT, CLBB, L_exp_noise, S_exp_noise,  cam):
        maskfinal = np.zeros(img.shape, np.uint8)
        my_dict = dict()
        img_seg = SynMedSeg(img, binmask, CLBT, CLBB, L_exp_noise, S_exp_noise, cam, self.side)
        regions = img_seg.labeledRegions()
        for props in regions:
            my_dict[props.label] = (props.bbox[1], props.bbox[0], props.bbox[3] - props.bbox[1],
                                    props.bbox[2] - props.bbox[0])
        for key, values in my_dict.items():
            mask = np.zeros(img.shape[:2], np.uint8)
            if cam == 1:
                pipes_num = 4
            else:
                pipes_num = 6
            if key < pipes_num:
                mask, pipe_number = img_seg.segmentation(values, mask, pad=100)

                if cam == 2:
                    pipe_number += 3
                mask[mask != 0] = 1
                maskfinal += np.stack((mask,) * 3, axis=-1)
                pill = features_vector(img, mask, (pipe_number - 1), cam, self.side)
                if self.print_out:
                    print(pill.get_features())
                if len(pill.get_features()) != 0:
                    self.save_data_training(str(pipe_number), pill.get_features(), cam)
        imgr = img * maskfinal
        self.save_image_training(imgr)


    def save_data_test(self, pipe_number,  features, cam, ClassExist):
        if ClassExist:
            try:
                os.mkdir(join(self.path_data, self.commonfolder, self.output, "features"))
            except:
                pass
            feature_path = join(self.path_data, self.commonfolder, self.output, "features", self.label+"Cam" +
                                str(cam) + ".txt")
            fwrite = open(feature_path, "a+")
            fwrite.write(self.label + "," + self.tray + "," + self.Card + "," + self.file_index + "," + pipe_number + ";")
            fwrite.write(str(features) + "\n")
            fwrite.close()
        else:
            try:
                os.mkdir(join(self.path_data, self.commonfolder))
            except:
                pass
            feature_path = join(self.path_data, self.commonfolder, "Cam" + str(cam) + "_not_ready.txt")
            fwrite = open(feature_path, "a+")
            fwrite.write(self.label+","+self.tray+","+self.Card+","+self.file_index+","+pipe_number+";")
            fwrite.write(str(features)+"\n")
            fwrite.close()

    def save_image_test(self, imgr, ClassExist):
        if ClassExist:
            if imgr.sum() != 0:
                try:
                    os.mkdir(join(self.path_data, self.commonfolder, self.output, "Tray_"+str(self.tray)))
                except:
                    pass
                try:
                    os.mkdir(join(self.path_data, self.commonfolder, self.output, "Tray_"+str(self.tray), "Card_" + self.Card))
                except:
                    pass
            cv2.imwrite(os.path.join(self.path_data, self.commonfolder, self.output, "Tray_"+str(self.tray),
                                         "Card_"+self.Card, self.file_name[:-4] + '_Seg' + ".bmp"),
                            cv2.cvtColor(imgr, cv2.COLOR_RGB2BGR))
        else:
            if imgr.sum() != 0:
                try:
                    os.mkdir(join(self.path_data, self.commonfolder, self.label))
                except:
                    pass
                cv2.imwrite(os.path.join(self.path_data, self.commonfolder, self.label,
                                         self.file_name[:-4] + '_Seg' + ".bmp"),
                            cv2.cvtColor(imgr, cv2.COLOR_RGB2BGR))

    def save_data_training(self, pipe_number,  features, cam):
        try:
            os.mkdir(join(self.path_data, self.commonfolder, self.training_set))
        except:
            pass
        feature_path = join(self.path_data, self.commonfolder, self.training_set, "Cam" + str(cam) + ".txt")
        fwrite = open(feature_path, "a+")
        fwrite.write(self.label + "," + self.tray + "," + self.Card + "," + self.file_index + "," + pipe_number + ";")
        fwrite.write(str(features) + "\n")
        fwrite.close()

    def save_image_training(self, imgr):
        if imgr.sum() != 0:
            try:
                os.mkdir(join(self.path_data, self.commonfolder, self.training_set))
            except:
                pass
            try:
                os.mkdir(join(self.path_data, self.commonfolder, self.training_set, self.label))
            except:
                pass
            cv2.imwrite(os.path.join(self.path_data, self.commonfolder, self.training_set, self.label,
                    self.file_name[:-4] + '_Seg' + ".bmp"), cv2.cvtColor(imgr, cv2.COLOR_RGB2BGR))
