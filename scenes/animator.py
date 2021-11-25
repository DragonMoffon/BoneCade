import json
import math
from copy import deepcopy
from typing import List

import arcade

import animation
import global_access
from global_access import SCREEN_WIDTH, SCREEN_HEIGHT
import skeleton
import lin_al as la


class AnimatorWindow(arcade.Window):

    def __init__(self):
        super().__init__()
        self.reference_texture = arcade.load_texture("resources/sprite_textures/run_reference.png")
        self.reference_frame = 0
        self.reference_shift = 0

        self.current_skeleton: skeleton.Skeleton = skeleton.create_skeleton("resources/skeletons/robot.json", "robot")
        self.current_pose: skeleton.SkeletonPose = skeleton.get_pose("resources/poses/robot_poses.json", "t_pose", 2)
        self.saved_poses: List[skeleton.SkeletonPose] = []
        self.selected_joint = -1
        self.last_rendered_pose = []

        self.world_matrix = [
            la.Matrix33.all_matrix(la.Vec2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2), la.Vec2(64*3.33333), 0),
            la.Matrix33.inverse_all_matrix(la.Vec2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2), la.Vec2(64*3.333333), 0)
        ]

        self.file_location = "resources/poses/animations/robot_motion.json"
        clips = json.load(open(self.file_location))['clips']
        animation.generate_clips("resources/poses/animations/robot_motion.json", None)
        self.saved_clips = [clip['id'] for clip in clips]
        self.clip_looping = False
        self.clip_fps = 1 / 30

    def on_draw(self):
        arcade.start_render()

        arcade.draw_circle_filled(45, SCREEN_HEIGHT - 45, 25, (155 * self.clip_looping,
                                                               155 * (not self.clip_looping), 13, 255))
        if self.clip_looping:
            arcade.draw_text("looping", 45, SCREEN_HEIGHT-45, anchor_x='center', anchor_y='center', font_size=10)

        arcade.draw_line(0, SCREEN_HEIGHT/2-1, SCREEN_WIDTH, SCREEN_HEIGHT/2-1, arcade.color.SAND, 2)

        arcade.draw_lrwh_rectangle_textured(SCREEN_WIDTH/2 - 98 - self.reference_frame*96*2 + self.reference_shift*2,
                                            SCREEN_HEIGHT/2, 768*2, 96*2, self.reference_texture)

        self.last_rendered_pose = self.current_pose.temp_draw(self.world_matrix[0])

        for index, pose in enumerate(self.saved_poses):
            pos = la.Matrix33.all_matrix(la.Vec2(50 + (index % 15)*50, SCREEN_HEIGHT/2 - 50 - 50*math.floor(index/15)),
                                         la.Vec2(48), 0)
            pose.temp_draw(pos)

        if self.selected_joint != -1:
            name = self.current_skeleton.joints[self.selected_joint].joint_name
            pos = self.last_rendered_pose[self.selected_joint]
            arcade.draw_text(name, pos.x, pos.y)

    def save_poses(self):
        poses = list(self.saved_poses)
        if not self.clip_looping:
            poses.append(poses[0])

        clip_name = input("clip name: ")
        animation.convert_clip(poses, clip_name, self.clip_looping, self.clip_fps)
        self.saved_clips.append(clip_name)

        self.saved_poses = []

    def save_clips(self):
        target = self.current_skeleton.skeleton_id
        animation.save_clips(self.file_location, target, self.saved_clips)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.saved_poses.append(deepcopy(self.current_pose))
        elif symbol == arcade.key.Q:
            self.reference_frame = max(self.reference_frame-1, 0)
        elif symbol == arcade.key.E:
            self.reference_frame = min(self.reference_frame+1, 7)
        elif symbol == arcade.key.A:
            self.reference_shift += 2
        elif symbol == arcade.key.D:
            self.reference_shift -= 2
        elif symbol == arcade.key.ENTER:
            if len(self.saved_poses):
                self.save_poses()
            if modifiers & arcade.key.LSHIFT or modifiers & arcade.key.RSHIFT:
                self.save_clips()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if 20 <= x <= 70 and SCREEN_HEIGHT-70 <= y <= SCREEN_HEIGHT-20:
            self.clip_looping = bool(1 - self.clip_looping)
        else:
            distance = 100
            selected_joint = None
            for joint in self.last_rendered_pose:
                dist = la.Vec2(joint.x - x, joint.y - y).square_length
                if dist < distance:
                    selected_joint = joint
                    distance = dist

            if selected_joint is not None:
                self.selected_joint = self.last_rendered_pose.index(selected_joint)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        self.selected_joint = -1

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        if self.selected_joint != -1:
            parent_index = self.current_skeleton.joints[self.selected_joint].parent
            if parent_index != -1:
                parent_matrix = la.Matrix33.lazy_inverse(self.current_pose.model_poses[parent_index])
            else:
                parent_matrix = la.Matrix33()

            pose_angle = self.current_pose.joint_poses[self.selected_joint].translation.theta
            square_length = self.current_pose.joint_poses[self.selected_joint].translation.square_length

            if modifiers & arcade.key.LSHIFT:
                mouse_pos = (la.Vec2(x, y) * self.world_matrix[1] * parent_matrix).item_mul(la.Vec2(0, 1))
            else:
                mouse_pos = la.Vec2(x, y) * self.world_matrix[1] * parent_matrix
                if not modifiers & arcade.key.LCTRL:
                    mouse_pos.square_length = square_length

            self.current_pose.joint_poses[self.selected_joint].translation = mouse_pos
            angle_change = self.current_pose.joint_poses[self.selected_joint].translation.theta - pose_angle

            if parent_index != -1:
                self.current_pose.joint_poses[self.selected_joint].angle += angle_change

            self.current_pose.calculate_model_poses()
