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
import random
import shutil

import numpy as np

from math import *
from mathutils import *

__bpydoc__ = """
Write me!
"""


class OBJECT_OT_show_frustum(bpy.types.Operator):
    """Create the frustum preview"""
    bl_idname = "scene.show_frustum"
    bl_label = """Create the frustum"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        frustum_name = bpy.context.scene.LF.get_frustum_name()
        try:
            bpy.data.objects[frustum_name].hide = False
        except KeyError:
            print("Could not find frustum '%s' to show." % frustum_name)
        return {'FINISHED'}


class OBJECT_OT_hide_frustum(bpy.types.Operator):
    """Hide the frustum preview"""
    bl_idname = "scene.hide_frustum"
    bl_label = """Hide the frustum"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        frustum_name = bpy.context.scene.LF.get_frustum_name()
        try:
            bpy.data.objects[frustum_name].hide = True
        except KeyError:
            print("Could not find frustum '%s' to hide. Try adding a camera grid first." % frustum_name)
        return {'FINISHED'}


class OBJECT_OT_update_lightfield(bpy.types.Operator):
    """Update the light field setup"""
    bl_idname = "scene.update_lightfield"
    bl_label = """Update the light field setup"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        LF = bpy.context.scene.LF

        try:
            # save current position and orientation of the camera grid
            lightfield = bpy.data.objects[LF.get_lightfield_name()]
            LF.center_cam_x, LF.center_cam_y, LF.center_cam_z = lightfield.location
            LF.center_cam_rot_x, LF.center_cam_rot_y, LF.center_cam_rot_z = lightfield.rotation_euler
        except KeyError:
            pass

        bpy.ops.scene.create_lightfield('EXEC_DEFAULT')
        return {'FINISHED'}


class OBJECT_OT_create_lightfield(bpy.types.Operator):
    """Create the light field setup"""
    bl_idname = "scene.create_lightfield"
    bl_label = """Create the light field setup"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.scene.delete_lightfield('EXEC_DEFAULT')

        # initialize lightfield elements
        self.set_render_properties()
        cameras = self.create_cameras()
        frustum = self.create_frustum()

        # create lightfield container
        LF = bpy.context.scene.LF
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0), rotation=(0, 0, 0))
        bpy.context.object.empty_draw_size = 0.4
        bpy.context.object.name = LF.get_lightfield_name()

        # add all cameras and frustum to container
        lightfield_objects = cameras + [frustum]
        for object in lightfield_objects:
            object.select = True

        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=False)
        bpy.context.object.location = [LF.center_cam_x, LF.center_cam_y, LF.center_cam_z]
        bpy.context.object.rotation_euler = [LF.center_cam_rot_x, LF.center_cam_rot_y, LF.center_cam_rot_z]

        LF.get_frustum().hide_select = True
        return {'FINISHED'}

    def create_cameras(self):
        LF = bpy.context.scene.LF
        pos_x = -LF.baseline_x_m * ((LF.num_cams_x - 1) / 2.0)
        pos_y = LF.baseline_y_m * ((LF.num_cams_y - 1) / 2.0)
        pos_z = 0
        cameras = []

        for i in range(0, LF.num_cams_y):
            for j in range(0, LF.num_cams_x):
                cameras.append(self.create_camera(LF.get_camera_name(i, j), pos_x, pos_y, pos_z, 0, 0))
                pos_x += LF.baseline_x_m
            pos_y -= LF.baseline_y_m
            pos_x = -LF.baseline_x_m * float(((LF.num_cams_x - 1) / 2.0))

        return cameras

    def create_camera(self, cam_name, x_pos, y_pos, z_pos, theta, phi, eta=0):
        LF = bpy.context.scene.LF
        bpy.ops.object.camera_add(location=(x_pos, y_pos, z_pos),
                                  rotation=(0,0,0))

        camera = bpy.context.active_object
        camera.name = cam_name
        camera.data.draw_size = 0.5
        camera.data.lens = LF.focal_length
        camera.data.sensor_width = LF.sensor_size
        camera.data.sensor_height = LF.sensor_size

        if LF.focus_dist == 0:
            factor = 0  # focused at infinity
            bpy.context.object.data.dof_distance = 10000  # not really infinity... but close enough.
        else:
            factor = LF.focal_length / LF.sensor_size / LF.focus_dist
            bpy.context.object.data.dof_distance = LF.focus_dist

        camera.data.shift_x = -x_pos * factor
        camera.data.shift_y = -y_pos * factor

        bpy.context.object.data.cycles.aperture_type = 'FSTOP'
        bpy.context.object.data.cycles.aperture_fstop = LF.fstop
        bpy.context.object.data.cycles.aperture_blades = LF.num_blades
        bpy.context.object.data.cycles.aperture_rotation = LF.rotation
        bpy.context.object.data.gpu_dof.fstop = LF.fstop

        return camera

    def get_frustum_coordinates(self):
        LF = bpy.context.scene.LF
        max_res = max(LF.x_res, LF.y_res)

        if LF.focus_dist == 0:
            factor = LF.baseline_x_m * LF.focal_length * max_res
            G_plus = factor / (LF.frustum_max_disp * LF.sensor_size)
            G_minus = 10000  # factor / (LF.frustum_min_disp * LF.sensor_size)
        else:
            factor = LF.baseline_x_m * LF.focal_length * LF.focus_dist * max_res
            G_plus = factor / (LF.baseline_x_m * LF.focal_length * max_res +
                               LF.frustum_max_disp * LF.focus_dist * LF.sensor_size)
            G_minus = factor / (LF.baseline_x_m * LF.focal_length * max_res +
                                LF.frustum_min_disp * LF.focus_dist * LF.sensor_size)
            if G_minus < 0:
                G_minus = 10000

        A = 2.0 * LF.focal_length / LF.sensor_size
        ARx = LF.x_res / max_res
        ARy = LF.y_res / max_res

        vertices = [(-ARx * G_minus / A, -ARy * G_minus / A, -G_minus),
                    ( ARx * G_minus / A, -ARy * G_minus / A, -G_minus),
                    ( ARx * G_minus / A, ARy * G_minus / A, -G_minus),
                    (-ARx * G_minus / A, ARy * G_minus / A, -G_minus),
                    (-ARx * G_plus / A, -ARy * G_plus / A, -G_plus),
                    ( ARx * G_plus / A, -ARy * G_plus / A, -G_plus),
                    ( ARx * G_plus / A, ARy * G_plus / A, -G_plus),
                    (-ARx * G_plus / A, ARy * G_plus / A, -G_plus)]

        edges = [(0, 4), (1, 5), (2, 6), (3, 7)]
        faces = [(0, 1, 2, 3), (4, 7, 6, 5)]
        return vertices, edges, faces

    def create_frustum(self):
        LF = bpy.context.scene.LF

        # draw frustum
        vertices, edges, faces = self.get_frustum_coordinates()
        mesh_data = bpy.data.meshes.new("FrustumMeshData")
        mesh_data.from_pydata(vertices, edges, faces)
        mesh_data.update()

        frustum = bpy.data.objects.new(LF.get_frustum_name(), mesh_data)
        frustum.hide_render = True
        frustum.show_transparent = True
        frustum.show_wire = True
        frustum.show_all_edges = True

        # add color
        face_material = bpy.data.materials.new("Cyan")
        face_material.diffuse_color = (0, 1, 1)
        face_material.alpha = 0.3

        frustum.data.materials.append(face_material)
        for face in frustum.data.polygons:
            face.material_index = 0

        # add frustum to scene
        scene = bpy.context.scene
        scene.objects.link(frustum)

        return frustum

    def set_render_properties(self):
        LF = bpy.context.scene.LF
        scene = bpy.data.scenes[bpy.context.scene.name]
        scene.render.resolution_x = LF.x_res
        scene.render.resolution_y = LF.y_res
        scene.render.resolution_percentage = 100


class OBJECT_OT_delete_lightfield(bpy.types.Operator):
    """Delete lightfield"""
    bl_idname = "scene.delete_lightfield"
    bl_label = """Delete the light field setup"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        LF = bpy.context.scene.LF

        try:
            lightfield = bpy.data.objects[LF.get_lightfield_name()]

            # save initially selected objects
            selected_objects = bpy.context.selected_objects

            # delesect everything
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            # delete frustum, cameras and container
            for camera in LF.get_lightfield_cameras():
                camera.select = True

            LF.get_frustum().hide = False
            LF.get_frustum().hide_select = False
            LF.get_frustum().select = True
            lightfield.select = True
            bpy.ops.object.delete()

            # restore initial state
            for object in selected_objects:
                object.select = True

        except KeyError:
            print ("No camera grid to delete with name: %s. Try adding a camera grid first." % LF.get_lightfield_name())

        return {'FINISHED'}


class OBJECT_OT_render_lightfield(bpy.types.Operator):
    """render light field"""
    bl_idname = "scene.render_lightfield"
    bl_label = """Render Light Field"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        LF = bpy.context.scene.LF

        # legacy mode
        if LF.sequence_start == LF.sequence_end:
            bpy.context.scene.frame_current = LF.sequence_start
            self.renderFrame()

        # sequence mode
        # when more then one frame should be rendered we render each frame to a different folder
        else:
            frame_list = range(LF.sequence_start, LF.sequence_end+1, LF.sequence_steps)
            for i in frame_list:
                bpy.context.scene.frame_current = i
                tgt_dir = os.path.join(bpy.path.abspath(LF.tgt_dir),"sequence","{:06d}".format(i))
                self.renderFrame(tgt_dir)


        return {'FINISHED'}

    def renderFrame(self, tgt_dir = None):
        """
        Renders the currently selected frame to tgt_dir folder
        """

        scene_key = bpy.context.scene.name
        LF = bpy.context.scene.LF

        tgt_root_dir = bpy.path.abspath(LF.tgt_dir)

        if tgt_dir == None:
            tgt_dir = tgt_root_dir


        bpy.context.scene.use_nodes = True
        bpy.data.scenes[scene_key].render.layers['RenderLayer'].use_pass_z = True

        # remove all nodes of previous file outputs
        try:
            for node in bpy.context.scene.node_tree.nodes:
                if node.name.startswith("LF"):
                    bpy.context.scene.node_tree.nodes.remove(node)
        except KeyError:
            pass

        lf_cameras = LF.get_lightfield_cameras()
        LF.cycles_seed = random.randint(0, 2147483646 - len(lf_cameras) - 1)

        # render input views with original resolution
        self.render_input_views(lf_cameras, scene_key, LF, tgt_dir)

        # store current render status
        current_render_engine = bpy.context.scene.render.engine
        current_antialiasing = bpy.context.scene.render.use_antialiasing

        # change settings for high resolution rendering
        bpy.data.scenes[bpy.context.scene.name].render.resolution_percentage = 100 * LF.depth_map_scale
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        bpy.context.scene.render.use_antialiasing = False

        # render high resolution object id maps
        if LF.save_object_id_maps_for_all_views:
            oid_cameras = lf_cameras
        else:
            oid_cameras = [LF.get_center_camera()]
        self.render_object_id_maps(oid_cameras, scene_key, LF, tgt_dir)

        # render high resolution depth maps
        if LF.save_depth_for_all_views:
            depth_cameras = lf_cameras
        else:
            depth_cameras = [LF.get_center_camera()]
        self.render_depth_and_disp_maps(depth_cameras, scene_key, LF, tgt_dir)

        # save parameters as config file in target directory of rendering
        tmp_config_path = LF.path_config_file
        LF.path_config_file = os.path.join(tgt_dir, 'parameters.cfg')
        bpy.ops.scene.save_lightfield('EXEC_DEFAULT')
        LF.path_config_file = tmp_config_path

        # reset status
        bpy.context.scene.render.engine = current_render_engine
        bpy.context.scene.render.use_antialiasing = current_antialiasing
        bpy.data.scenes[bpy.context.scene.name].render.resolution_percentage = 100
        bpy.data.scenes[scene_key].render.filepath = tgt_root_dir

        print('Done!')

    def render_input_views(self, cameras, scene_key, LF, tgt_dir):



        # create image output node
        image_out_node = bpy.data.scenes[scene_key].node_tree.nodes.new(type='CompositorNodeOutputFile')
        image_out_node.format.file_format = 'PNG'
        image_out_node.format.color_mode = 'RGB'
        image_out_node.format.color_depth = '8'
        image_out_node.name = 'LF_IMAGE_OUTPUT'

        # connect nodes
        right = bpy.data.scenes[scene_key].node_tree.nodes['Render Layers'].outputs['Image']
        left = image_out_node.inputs['Image']
        bpy.data.scenes[scene_key].node_tree.links.new(right, left)

        bpy.data.scenes[scene_key].render.filepath = os.path.join(bpy.path.abspath(LF.tgt_dir), "unused_blenderender_output")

        image_out_node.base_path = tgt_dir

        # render view per camera
        c_image = 'Image'
        for cam_idx, camera in enumerate(cameras):
            print("Rendering scene with camera: " + camera.name)
            image_filename = 'input_' + self.get_raw_camera_name(camera.name)
            image_out_node.file_slots[c_image].path = image_filename + '_frame###'
            c_image = image_filename + '_frame###'

            # set scene camera to current light field camera
            bpy.data.scenes[scene_key].camera = camera

            # change seed
            bpy.data.scenes[scene_key].cycles.seed = LF.cycles_seed + cam_idx
            print("Cycles seed for camera %d: %d" % (cam_idx, bpy.data.scenes[scene_key].cycles.seed))

            # render scene and adjust the file name
            bpy.ops.render.render(write_still=True)
            self.remove_blender_frame_from_file_name(image_filename, tgt_dir)

        # remove the image output node
        bpy.context.scene.node_tree.nodes.remove(image_out_node)

    def render_object_id_maps(self, cameras, scene_key, LF, tgt_dir):
        bpy.data.scenes[bpy.context.scene.name].render.layers["RenderLayer"].use_pass_object_index = True

        # prepare nodes for object id map
        oid_out_node = bpy.data.scenes[scene_key].node_tree.nodes.new(type='CompositorNodeOutputFile')
        oid_out_node.format.file_format = 'PNG'
        oid_out_node.format.color_depth = '16'
        oid_out_node.format.color_mode = 'BW'
        oid_out_node.name = 'LF_OID_OUTPUT'

        oid_math_node = bpy.data.scenes[scene_key].node_tree.nodes.new(type='CompositorNodeMath')
        oid_math_node.operation = 'DIVIDE'
        oid_math_node.inputs[1].default_value = 2 ** 16 - 1
        oid_math_node.name = 'LF_OID_MATH'

        right = bpy.data.scenes[scene_key].node_tree.nodes['Render Layers'].outputs['IndexOB']
        math_left = oid_math_node.inputs[0]
        math_right = oid_math_node.outputs[0]
        left = oid_out_node.inputs['Image']

        bpy.data.scenes[scene_key].node_tree.links.new(right, math_left)
        bpy.data.scenes[scene_key].node_tree.links.new(math_right, left)
        oid_out_node.base_path = tgt_dir
        out_oid = oid_out_node.file_slots['Image']

        # assign an object id to all scene objects
        idx = 1
        for obj in bpy.data.objects:
            if obj.type not in ['CAMERA', 'LAMP', 'EMPTY'] and not obj.name.startswith("LF"):
                obj.pass_index = idx
                idx += 1

        # save object id map for each camera
        for camera in cameras:
            print("Rendering object id map with camera: " + camera.name)
            oid_filename = 'objectids_highres_' + self.get_raw_camera_name(camera.name)
            out_oid.path = oid_filename + "_frame###"

            # set scene camera to current light field camera
            bpy.data.scenes[scene_key].camera = camera

            # render scene and adjust the file name
            bpy.ops.render.render(write_still=True)
            self.remove_blender_frame_from_file_name(oid_filename, tgt_dir)

        # handle additional "standard" center view object id map
        center_camera = LF.get_center_camera()
        src = os.path.join(tgt_dir, 'objectids_highres_%s.png' % self.get_raw_camera_name(center_camera.name))
        tgt = os.path.join(tgt_dir, 'objectids_highres.png')

        # remove file with final filename if it exists
        # (necessary for Windows systems where renaming is not an atomic operation)
        try:
            os.remove(tgt)
        except:
            pass

        if LF.save_object_id_maps_for_all_views:
            shutil.copy(src, tgt)
        else:
            os.rename(src, tgt)

        # remove the oid output node
        bpy.context.scene.node_tree.nodes.remove(oid_out_node)

    def render_depth_and_disp_maps(self, cameras, scene_key, LF, tgt_dir):
        max_res = max(LF.x_res, LF.y_res)
        factor = LF.baseline_x_m * LF.focal_length * LF.focus_dist * max_res

        # prepare depth output node
        right = bpy.data.scenes[scene_key].node_tree.nodes['Render Layers'].outputs['Z']
        depth_view_node = bpy.data.scenes[scene_key].node_tree.nodes.new('CompositorNodeViewer')
        depth_view_node.use_alpha = False
        left = depth_view_node.inputs[0]
        bpy.data.scenes[scene_key].node_tree.links.new(right, left)

        for camera in cameras:
            print("Rendering depth map with camera: " + camera.name)

            # set scene camera to current light field camera
            bpy.data.scenes[scene_key].camera = camera

            # render scene and extract depth map to numpy array
            bpy.ops.render.render(write_still=True)
            pixels = bpy.data.images['Viewer Node'].pixels  # size is width * height * 4 (rgba)
            depth = np.array(pixels)[::4]

            # reshape high resolution depth map
            depth = depth.reshape((int(LF.y_res * LF.depth_map_scale), int(LF.x_res * LF.depth_map_scale)))

            # create depth map with original (low) resolution
            depth_small = median_downsampling(depth, LF.depth_map_scale, LF.depth_map_scale)

            # check if high resolution depth map has depth artifacts on individual pixels
            min_depth = np.min(depth_small)
            max_depth = np.max(depth_small)
            m_out_of_range = (depth < 0.9*min_depth) + (depth > 1.1*max_depth)

            if np.sum(m_out_of_range) > 0:
                depth = self.fix_pixel_artefacts(depth, m_out_of_range)
                depth_small = median_downsampling(depth, LF.depth_map_scale, LF.depth_map_scale)

            # create disparity maps
            disp = (factor / depth - LF.baseline_x_m * LF.focal_length * max_res) / LF.focus_dist / LF.sensor_size
            disp_small = median_downsampling(disp, LF.depth_map_scale, LF.depth_map_scale)

            # set disparity range for config file
            LF.min_disp = np.floor(np.amin(disp_small) * 10) / 10 - 0.1
            LF.max_disp = np.ceil(np.amax(disp_small) * 10) / 10 + 0.1

            # save disparity files
            if camera.name == LF.get_center_camera().name:
                write_pfm(depth, os.path.join(tgt_dir, 'gt_depth_highres.pfm'))
                write_pfm(disp, os.path.join(tgt_dir, 'gt_disp_highres.pfm'))
                write_pfm(depth_small, os.path.join(tgt_dir, 'gt_depth_lowres.pfm'))
                write_pfm(disp_small, os.path.join(tgt_dir, 'gt_disp_lowres.pfm'))

            if LF.save_depth_for_all_views:
                camera_name = self.get_raw_camera_name(camera.name)
                write_pfm(depth, os.path.join(tgt_dir, 'gt_depth_highres_%s.pfm' % camera_name))
                write_pfm(disp, os.path.join(tgt_dir, 'gt_disp_highres_%s.pfm' % camera_name))
                write_pfm(depth_small, os.path.join(tgt_dir, 'gt_depth_lowres_%s.pfm' % camera_name))
                write_pfm(disp_small, os.path.join(tgt_dir, 'gt_disp_lowres_%s.pfm' % camera_name))

    def fix_pixel_artefacts(self, disp, m_out_of_range, half_window=1):
        print("Fixing %d out of range pixel(s), values: %s" % (np.sum(m_out_of_range), list(disp[m_out_of_range])))
        coords = np.where(m_out_of_range)
        h, w = np.shape(disp)

        for x, y in zip(coords[1], coords[0]):
            xmin = max(0, x - half_window)
            xmax = min(w - 1, x + half_window)
            ymin = max(0, y - half_window)
            ymax = min(h - 1, y + half_window)

            window_values = disp[ymin:ymax + 1, xmin:xmax + 1]
            valid_window_values = window_values[~m_out_of_range[ymin:ymax + 1, xmin:xmax + 1]]
            n_values = np.size(valid_window_values)

            if n_values == 0:
                print("Could not find any pixels for inpainting depth artifact at (%d, %d)." % (y, x))
                continue

            # compute median (without averaging for even n)
            median = np.sort(valid_window_values)[n_values / 2]
            disp[y, x] = median

        return disp

    @staticmethod
    def get_raw_camera_name(camera_name):
        prefix, camera = camera_name.split("_Cam")
        return "Cam" + camera

    @staticmethod
    def remove_blender_frame_from_file_name(image_filename, tgt_dir):
        blender_filename = os.path.join(tgt_dir, "%s_frame%03d.png" % (image_filename, bpy.context.scene.frame_current))

        # remove blender frame numbers from file name
        final_filename = os.path.join(tgt_dir, os.path.join(tgt_dir, "%s.png" % image_filename))

        # remove file with final filename if it exists
        # (necessary for Windows systems where renaming is not an atomic operation)
        try:
            os.remove(final_filename)
        except:
            pass
        os.rename(blender_filename, final_filename)


def write_pfm(data, fpath):
    with open(fpath, 'wb') as file:
        # header
        height, width = np.shape(data)
        file.write('Pf\n'.encode('utf-8'))
        file.write(('%d %d\n' % (width, height)).encode('utf-8'))
        file.write(('%d\n' % -1).encode('utf-8'))

        # data
        values = np.ndarray.flatten(np.asarray(data, dtype=np.float32))
        file.write(values)


def median_downsampling(img, tile_height, tile_width):
    h, w = np.shape(img)
    if w % tile_width or h % tile_height:
        raise Exception("Image dimensions must be multiple of tile dimensions.")

    n_tiles_horiz = w / tile_width
    n_tiles_vert = h / tile_height
    n_tiles = n_tiles_horiz * n_tiles_vert

    # split vertically into tiles with height=tile_height, width=img_width
    tiles_vert = np.asarray(np.split(img, int(n_tiles_vert), 0))  # n_tiles_vert x tile_height x w
    tiles_vert = tiles_vert.transpose([1, 0, 2]).reshape(int(tile_height), int(n_tiles_vert * w))

    # split horizontally into tiles with height=tile_height, width=tile_width
    tiles = np.asarray(np.split(tiles_vert, n_tiles, 1))
    tiles = tiles.reshape(int(n_tiles), int(tile_width * tile_height))  # n_tiles x px_per_tile

    # compute median per tile (without averaging for even N)
    tiles = np.sort(tiles, axis=1)[:, int(tile_width*tile_height/2)]
    small_img = tiles.reshape(int(n_tiles_vert), int(n_tiles_horiz))

    return small_img
