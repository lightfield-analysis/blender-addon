############################################################################
#  This file is part of the 4D Light Field Benchmark.                      #
#                                                                          #
#  This work is licensed under the Creative Commons                        #
#  Attribution-NonCommercial-ShareAlike 4.0 International License.         #
#  To view a copy of this license,                                         #
#  visit http://creativecommons.org/licenses/by-nc-sa/4.0/.                #
#                                                                          #
#  Authors: Katrin Honauer & Ole Johannsen                                 #
#  Contact: contact@lightfield-analysis.net                                #
#  Website: www.lightfield-analysis.net                                    #
#                                                                          #
#  This add-on is based upon work of Maximilian Diebold                    #
#                                                                          #
#  The 4D Light Field Benchmark was jointly created by the University of   #
#  Konstanz and the HCI at Heidelberg University. If you use any part of   #
#  the benchmark, please cite our paper "A dataset and evaluation          #
#  methodology for depth estimation on 4D light fields". Thanks!           #
#                                                                          #
#  @inproceedings{honauer2016benchmark,                                    #
#    title={A dataset and evaluation methodology for depth estimation on   #
#           4D light fields},                                              #
#    author={Honauer, Katrin and Johannsen, Ole and Kondermann, Daniel     #
#            and Goldluecke, Bastian},                                     #
#    booktitle={Asian Conference on Computer Vision},                      #
#    year={2016},                                                          #
#    organization={Springer}                                               #
#    }                                                                     #
#                                                                          #
############################################################################


import bpy
from bpy.props import *

import os


def update_lightfield(self, context):
    """
    update function for light field
    """
    bpy.ops.scene.update_lightfield('EXEC_DEFAULT')


def update_baseline(self, context):
    """
    update function for baseline property
    """
    LF = bpy.context.scene.LF
    LF.baseline_x_m = LF.baseline_mm / 1000.0
    LF.baseline_y_m = LF.baseline_mm / 1000.0
    update_lightfield(self, context)


def update_number_of_cameras(self, context):
    """
    update function for number of cameras
    """
    # enforce odd number of cameras
    LF = bpy.context.scene.LF

    if LF.num_cams_x % 2 == 0:
        if LF.num_cams_x_hidden and LF.num_cams_x_hidden < LF.num_cams_x:
            LF.num_cams_x += 1
        else:
            LF.num_cams_x -= 1

    if LF.num_cams_y % 2 == 0:
        if LF.num_cams_y_hidden and LF.num_cams_y_hidden < LF.num_cams_y:
            LF.num_cams_y += 1
        else:
            LF.num_cams_y -= 1

    LF.num_cams_x_hidden = LF.num_cams_x
    LF.num_cams_y_hidden = LF.num_cams_y

    update_lightfield(self, context)


def update_target_directory(self, context):
    """
    update function for target directory
    """
    LF = bpy.context.scene.LF
    if not LF.is_valid_directory(LF.tgt_dir):
        LF.tgt_dir = get_default_target_directory()


def update_path_config_file(self, context):
    """
    update function for path to config file
    """
    LF = bpy.context.scene.LF
    try:
        path, file_name = os.path.split(LF.path_config_file)
        if not LF.is_valid_directory(path):
            LF.path_config_file = get_default_path_config_file()
    except:
        print("Could not split file path into directory and file name: '%s'" % LF.path_config_file)
        LF.path_config_file = get_default_path_config_file()


def get_default_target_directory():
    path = os.path.join(bpy.context.user_preferences.filepaths.temporary_directory, 'lightfield')
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_default_path_config_file():
    return os.path.join(get_default_target_directory(), 'parameters.cfg')
