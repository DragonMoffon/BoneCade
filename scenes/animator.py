import json
import math
from copy import deepcopy
from os.path import isfile

import arcade

import lin_al as la
import transform
import model
import skeleton
import animation
import skinned_renderer
from clock import GAME_CLOCK
from global_access import SCREEN_WIDTH, SCREEN_HEIGHT


# ANIMATOR SPECIFIC HELPER FUNCTIONS


def prim_model_from_skeleton(base_skeleton: skeleton.Skeleton):
    segments = []
    for joint in base_skeleton.joints:
        segment_name = joint.joint_name
        if 'right' in segment_name:
            segment_color = arcade.color.RADICAL_RED
        elif 'left' in segment_name:
            segment_color = arcade.color.LIME_GREEN
        else:
            segment_color = arcade.color.WHITE

        model_pos = la.Vec2(0) * la.Matrix33.lazy_inverse(joint.inv_bind_pose_matrix)
        index = base_skeleton.joints.index(joint)

        segment = model.SegmentPrimitive(segment_name, segment_color, 2, model_pos, index, joint.parent)
        segments.append(segment)
    return model.PrimitiveModel(segments, base_skeleton.skeleton_id)


def calculate_model_poses(joints, joint_poses):
    model_poses = []
    for index, joint in enumerate(joints):
        if joint.parent != -1:
            former_matrix = model_poses[joint.parent]
        else:
            former_matrix = la.Matrix33()

        current_matrix = joint_poses[index].to_matrix() * former_matrix
        model_poses.append(current_matrix)

    return model_poses


def save_clips(target_skeleton: skeleton.Skeleton, target_file: str, clips: dict):
    save_data = {"target": target_skeleton.skeleton_id, "clips": []}
    for clip_id, clip in clips.items():
        clip_data = {
            "id": clip_id,
            "loop": clip.is_looping,
            "fps": clip.frames_per_second,
            "frames": [[[t_r.angle, t_r.translation.x, t_r.translation.y] for t_r in frame.joint_poses]
                       for frame in clip.frames]
        }
        save_data['clips'].append(clip_data)

    print(save_data)
    if isfile(f"resources/poses/animations/{target_file}"):
        json.dump(save_data, open(f"resources/poses/animations/{target_file}", 'wt'))
    else:
        json.dump(save_data, open(f"resources/poses/animations/{target_file}", 'xt'))


class AnimatorWindow(arcade.Window):

    def __init__(self, current_skeleton, clips, current_clip, current_pose, t_pose, target_clips):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "skeleton animator")
        self.t_pose = t_pose
        self.target_clips = target_clips

        self.current_skeleton: skeleton.Skeleton = current_skeleton
        self.clips = clips

        self.current_clip: animation.Clip = current_clip
        self.current_frame = 0
        self.pending_frame = 0

        self.current_pose: animation.FramePose = current_pose
        self.model_world_matrices = calculate_model_poses(self.current_skeleton.joints, current_pose.joint_poses)

        self.selected_joint = -1

        self.world_transform = transform.Transform(la.Vec2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2), la.Vec2(64*4), 0)

        self.frame_renderer = skinned_renderer.Primitive(self.current_skeleton,
                                                         prim_model_from_skeleton(self.current_skeleton),
                                                         self.world_transform)

        self.animation: animation.Animation = self.frame_renderer.animator.add_animation(self.current_clip, 1,
                                                                                         GAME_CLOCK.run_time, -1, 0.375)

        self.test_mesh_renderer = skinned_renderer.create_sample_mesh_renderer(self.ctx)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.PERIOD:
            self.current_frame = (self.current_frame + 1) % self.current_clip.frame_count
            self.current_pose = self.current_clip.frames[self.current_frame]
            self.model_world_matrices = calculate_model_poses(self.current_skeleton.joints,
                                                              self.current_pose.joint_poses)
        elif symbol == arcade.key.COMMA:
            self.current_frame = (self.current_frame - 1) % self.current_clip.frame_count
            self.current_pose = self.current_clip.frames[self.current_frame]
            self.model_world_matrices = calculate_model_poses(self.current_skeleton.joints,
                                                              self.current_pose.joint_poses)
        elif symbol == arcade.key.SPACE:
            if self.animation is not None:
                self.animation.smooth_stop()
                self.animation = None
            else:
                self.animation = self.frame_renderer.animator.add_animation(self.current_clip, 1,
                                                                            GAME_CLOCK.run_time, -1, 0.375)

        elif symbol == arcade.key.P:
            self.current_frame = self.pending_frame
            self.current_pose = self.current_clip.frames[self.pending_frame]
            self.model_world_matrices = calculate_model_poses(self.current_skeleton.joints,
                                                              self.current_pose.joint_poses)
        elif symbol == arcade.key.EQUAL:
            self.current_frame += 1

            self.current_clip.frames.insert(self.current_frame, deepcopy(self.t_pose))
            self.current_clip.frame_count = len(self.current_clip.frames)

            self.current_pose = self.current_clip.frames[self.current_frame]
            self.pending_frame = self.current_frame

            self.model_world_matrices = calculate_model_poses(self.current_skeleton.joints,
                                                              self.current_pose.joint_poses)
        elif symbol == arcade.key.MINUS and self.current_clip.frame_count > 1:
            self.current_clip.frames.remove(self.current_pose)
            self.current_clip.frame_count = len(self.current_clip.frames)

            self.current_frame = (self.current_frame - 1) % self.current_clip.frame_count
            self.current_pose = self.current_clip.frames[self.current_frame]
            self.pending_frame = self.current_frame

            self.model_world_matrices = calculate_model_poses(self.current_skeleton.joints,
                                                              self.current_pose.joint_poses)
        elif symbol == arcade.key.S:
            if modifiers & arcade.key.LCTRL:
                save_clips(self.current_skeleton, self.target_clips, self.clips)

    def on_update(self, delta_time: float):
        GAME_CLOCK.increment(delta_time)

    def on_draw(self):
        arcade.start_render()

        arcade.draw_line(0, SCREEN_HEIGHT/2-1, SCREEN_WIDTH, SCREEN_HEIGHT/2-1, arcade.color.WHITE, 2)

        self.test_mesh_renderer.draw()

        if not self.frame_renderer.animator.animations:
            self.frame_renderer.pose_draw(self.current_pose)
        else:
            self.frame_renderer.draw()

        arcade.draw_text(f"Frame: {self.current_frame+1}/{self.current_clip.frame_count}", 15, SCREEN_HEIGHT-15)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        mouse_pos = la.Vec2(x, y)
        if button == arcade.MOUSE_BUTTON_LEFT:
            distance = 100
            closest_joint = None
            for segment in self.frame_renderer.last_world_space_joints:
                dist = (segment - mouse_pos).square_length
                if dist <= distance:
                    distance = dist
                    closest_joint = segment
            if closest_joint is not None:
                self.selected_joint = self.frame_renderer.last_world_space_joints.index(closest_joint)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        if self.selected_joint != -1:
            parent_index = self.current_skeleton.joints[self.selected_joint].parent
            if parent_index != -1:
                parent_matrix = la.Matrix33.lazy_inverse(self.model_world_matrices[parent_index])
            else:
                parent_matrix = la.Matrix33()

            pose_angle = self.current_pose.joint_poses[self.selected_joint].translation.theta
            square_length = self.current_pose.joint_poses[self.selected_joint].translation.square_length

            if modifiers & arcade.key.LSHIFT:
                mouse_pos = (la.Vec2(x, y) * self.world_transform.to_inverse() * parent_matrix).item_mul(la.Vec2(0, 1))
            else:
                mouse_pos = la.Vec2(x, y) * self.world_transform.to_inverse() * parent_matrix
                if not modifiers & arcade.key.LCTRL:
                    mouse_pos.square_length = square_length

            self.current_pose.joint_poses[self.selected_joint].translation = mouse_pos
            angle_change = self.current_pose.joint_poses[self.selected_joint].translation.theta - pose_angle
            if parent_index != -1:
                self.current_pose.joint_poses[self.selected_joint].angle += angle_change

            self.model_world_matrices = calculate_model_poses(self.current_skeleton.joints,
                                                              self.current_pose.joint_poses)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        GAME_CLOCK.run_speed += scroll_y/15


def animator_setup():
    target_skeleton = input("Which skeleton would you like to animate? ")
    current_skeleton = skeleton.create_skeleton(target_skeleton)

    target_clips = input("What is the location of the clip file you would like to work with?"
                         " resources/poses/animations/")
    if not isfile(target_clips):
        json_data = json.load(open(f"resources/poses/animations/{target_clips}"))
    else:
        json_data = {"target": target_skeleton, "clips": []}

    clips = {data['id']: animation.generate_clip(data, current_skeleton) for data in json_data['clips']}

    target_clip = input("which clip would you like to create/modify? ")

    print(target_clip, json_data)
    if target_clip not in clips:
        current_clip = animation.Clip(current_skeleton, [], 1/30, True)
        clips[target_clip] = current_clip
    else:
        current_clip = clips[target_clip]

    t_pose = animation.generate_frame(json.load(open(f"resources/poses/{target_skeleton}.json"))['poses']['t'])

    if not current_clip.frames:
        current_pose = deepcopy(t_pose)
        current_clip.frames.append(current_pose)
        current_clip.frame_count = len(current_clip.frames)
    else:
        current_pose = current_clip.frames[0]

    return AnimatorWindow(current_skeleton, clips, current_clip, current_pose, t_pose, target_clips)


