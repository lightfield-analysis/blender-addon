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



class VIEW3D_OT_lightfield_setup(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Light Field Renderer"

    def draw(self, context):
        LF = bpy.context.scene.LF
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Camera parameters:")
        col.prop(LF, "focal_length")
        col.prop(LF, "x_res")
        col.prop(LF, "y_res")
        col.prop(LF, "sensor_size")
        col.prop(LF, "fstop")

        col = layout.column(align=True)
        col.label(text="Light field parameters:")
        col.prop(LF, "num_cams_x")
        col.prop(LF, "num_cams_y")
        col.prop(LF, "baseline_mm")
        col.prop(LF, "focus_dist")

        col = layout.column(align=True)
        col.operator("scene.create_lightfield", "Add Camera Grid", icon="HAND")
        col.operator("scene.delete_lightfield", "Delete Camera Grid", icon="HAND")

        col = layout.column(align=True)
        col.label(text="Disparity Preview:")
        col.prop(LF, "frustum_min_disp")
        col.prop(LF, "frustum_max_disp")

        if LF.frustum_is_hidden():
            col.operator("scene.show_frustum", "Show Frustum", icon="HAND")
        else:
            col.operator("scene.hide_frustum", "Hide Frustum", icon="HAND")

        col = layout.column(align=True)
        col.label(text="Rendering:")
        col.prop(LF, "tgt_dir")
        col.prop(LF, "depth_map_scale")
        col.prop(LF, "save_depth_for_all_views")
        col.prop(LF, "save_object_id_maps_for_all_views")
        col.operator("scene.render_lightfield", "Render Light Field", icon="HAND")

        col = layout.column(align=True)
        col.label("Meta information:")
        col.prop(LF, "scene")
        col.prop(LF, "category")
        col.prop(LF, "date")
        col.prop(LF, "version")
        col.prop(LF, "authors")
        col.prop(LF, "contact")

        col = layout.column(align=True)
        col.label(text="Save/load light field settings:")
        col.prop(LF, "path_config_file")
        col.operator("scene.load_lightfield", "Load config file", icon="SCENE_DATA")
        col.operator("scene.save_lightfield", "Save config file", icon="SCENE_DATA")
