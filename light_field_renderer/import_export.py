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


import configparser


class OBJECT_OT_save_lightfield(bpy.types.Operator):
    """Save config file with camera setup"""
    bl_idname = "scene.save_lightfield"
    bl_label = """Save light field parameters"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        LF = bpy.context.scene.LF
        parser = configparser.ConfigParser(delimiters="=")

        section = "intrinsics"
        parser.add_section(section)
        parser.set(section, 'focal_length_mm', str(LF.focal_length))
        parser.set(section, 'image_resolution_x_px', str(LF.x_res))
        parser.set(section, 'image_resolution_y_px', str(LF.y_res))
        parser.set(section, 'sensor_size_mm', str(LF.sensor_size))
        parser.set(section, 'fstop', str(LF.fstop))

        section = "extrinsics"
        parser.add_section(section)
        parser.set(section, 'num_cams_x', str(LF.num_cams_x))
        parser.set(section, 'num_cams_y', str(LF.num_cams_y))
        parser.set(section, 'baseline_mm', str(LF.baseline_mm))
        parser.set(section, 'focus_distance_m', str(LF.focus_dist))

        try:
            lightfield = bpy.data.objects[LF.get_lightfield_name()]
            LF.center_cam_x, LF.center_cam_y, LF.center_cam_z = lightfield.location
            LF.center_cam_rot_x, LF.center_cam_rot_y, LF.center_cam_rot_z = lightfield.rotation_euler

            parser.set(section, 'center_cam_x_m', str(LF.center_cam_x))
            parser.set(section, 'center_cam_y_m', str(LF.center_cam_y))
            parser.set(section, 'center_cam_z_m', str(LF.center_cam_z))
            parser.set(section, 'center_cam_rx_rad', str(LF.center_cam_rot_x))
            parser.set(section, 'center_cam_ry_rad', str(LF.center_cam_rot_y))
            parser.set(section, 'center_cam_rz_rad', str(LF.center_cam_rot_z))
        except:
            pass

        parser.set(section, 'offset', str(self.get_offset(LF)))

        section = "meta"
        parser.add_section(section)
        parser.set(section, 'scene', str(LF.scene))
        parser.set(section, 'category', str(LF.category))
        parser.set(section, 'date', str(LF.date))
        parser.set(section, 'version', str(LF.version))
        parser.set(section, 'authors', str(LF.authors))
        parser.set(section, 'contact', str(LF.contact))

        parser.set(section, 'cycles_seed', str(LF.cycles_seed))
        parser.set(section, 'disp_min', str(round(LF.min_disp, 1)))
        parser.set(section, 'disp_max', str(round(LF.max_disp, 1)))
        parser.set(section, 'frustum_disp_min', str(LF.frustum_min_disp))
        parser.set(section, 'frustum_disp_max', str(LF.frustum_max_disp))
        parser.set(section, 'depth_map_scale', str(LF.depth_map_scale))

        with open(bpy.path.abspath(LF.path_config_file), "w") as f:
            parser.write(f)

        return {'FINISHED'}

    def get_offset(self, LF):
        offset = LF.baseline_mm * LF.focal_length / LF.focus_dist / 1000. / LF.sensor_size * max(LF.x_res, LF.y_res)
        return offset


class OBJECT_OT_load_lightfield(bpy.types.Operator):
    """Load config file with camera setup"""
    bl_idname = "scene.load_lightfield"
    bl_label = """Load and initialize light field parameters"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        LF = bpy.context.scene.LF
        parser = configparser.ConfigParser(delimiters="=")
        parser.read(bpy.path.abspath(LF.path_config_file))

        section = "intrinsics"
        LF.focal_length = float(parser.get(section, 'focal_length_mm'))
        LF.x_res = int(parser.get(section, 'image_resolution_x_px'))
        LF.y_res = int(parser.get(section, 'image_resolution_y_px'))
        LF.sensor_size = float(parser.get(section, 'sensor_size_mm'))
        LF.fstop = float(parser.get(section, 'fstop'))

        section = "meta"
        LF.scene = parser.get(section, 'scene')
        LF.category = parser.get(section, 'category')
        LF.date = parser.get(section, 'date')
        LF.version = parser.get(section, 'version')
        LF.authors = parser.get(section, 'authors')
        LF.contact = parser.get(section, 'contact')
        LF.frustum_min_disp = float(parser.get(section, 'frustum_disp_min'))
        LF.frustum_max_disp = float(parser.get(section, 'frustum_disp_max'))
        LF.min_disp = float(parser.get(section, 'disp_min'))
        LF.max_disp = float(parser.get(section, 'disp_max'))
        LF.depth_map_scale = float(parser.get(section, 'depth_map_scale'))
        LF.cycles_seed = float(parser.get(section, 'cycles_seed'))

        section = "extrinsics"
        LF.num_cams_x = int(parser.get(section, 'num_cams_x'))
        LF.num_cams_y = int(parser.get(section, 'num_cams_y'))
        LF.baseline_mm = float(parser.get(section, 'baseline_mm'))
        LF.focus_dist = float(parser.get(section, 'focus_distance_m'))
        LF.center_cam_x = float(parser.get(section, 'center_cam_x_m'))
        LF.center_cam_y = float(parser.get(section, 'center_cam_y_m'))
        LF.center_cam_z = float(parser.get(section, 'center_cam_z_m'))
        LF.center_cam_rot_x = float(parser.get(section, 'center_cam_rx_rad'))
        LF.center_cam_rot_y = float(parser.get(section, 'center_cam_ry_rad'))
        LF.center_cam_rot_z = float(parser.get(section, 'center_cam_rz_rad'))

        bpy.ops.scene.create_lightfield('EXEC_DEFAULT')
        return {'FINISHED'}
