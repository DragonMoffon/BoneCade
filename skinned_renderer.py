from typing import Tuple, List
from math import degrees

import arcade


import lin_al as la
from global_access import SCREEN_WIDTH, SCREEN_HEIGHT
from clock import GAME_CLOCK
import skeleton
import model
import transform
import animation


class SkinnedRenderer:

    def __init__(self, render_skeleton, render_model, position):
        self.skeleton: skeleton.Skeleton = render_skeleton
        self.transform: transform.Transform = position
        self.model = render_model
        self.animator: animation.AnimationSet = animation.AnimationSet()


class Primitive(SkinnedRenderer):
    """
    A skeleton and a primitive model.
    """

    def __init__(self, render_skeleton, render_model, position):
        super().__init__(render_skeleton, render_model, position)
        self.last_world_space_joints: List[la.Vec2] = []

    def calculate_prim_point(self, index, poses, weights, world_matrix):
        inverse_matrix = self.skeleton.joints[index].inv_bind_pose_matrix
        segment = self.model.segment_list[index]

        if not len(poses):
            final_point = segment.model_view_pos * world_matrix
        else:
            final_point = la.Vec2(0)
            for k, pose in enumerate(poses):
                joint_pose = pose[index]
                skinning_matrix = inverse_matrix * joint_pose
                final_point += segment.model_view_pos * skinning_matrix * world_matrix * weights[k]
        return final_point

    def render_points(self, poses, weights):
        index = 0
        world_matrix = self.transform.to_matrix()

        world_space_joints = []
        while index < self.skeleton.joint_count:
            primitive_segment = self.model.segment_list[index]

            final_point = self.calculate_prim_point(index, poses, weights, world_matrix)
            if primitive_segment.parent_primitive_index != -1:
                parent_point = world_space_joints[primitive_segment.parent_primitive_index]
                arcade.draw_line(final_point.x, final_point.y, parent_point.x, parent_point.y,
                                 primitive_segment.colour, primitive_segment.thickness)
            arcade.draw_point(final_point.x, final_point.y, primitive_segment.colour, primitive_segment.thickness * 2)

            world_space_joints.append(final_point)
            index += 1

        self.last_world_space_joints = world_space_joints

    def draw(self):
        poses, weights = self.animator.get_poses()
        self.render_points(poses, weights)

    def pose_draw(self, pose: animation.FramePose):
        poses = []
        for index, joint_pose in enumerate(pose.joint_poses):
            parent = self.skeleton.joints[index].parent
            if parent != -1:
                poses.append(joint_pose.to_matrix() * poses[parent])
            else:
                poses.append(joint_pose.to_matrix())

        self.render_points((poses,), (1,))


def create_sample_prim_renderer():
    clip = animation.generate_clips("resources/poses/animations/basic_motion.json", 'run')

    entity_skeleton = skeleton.create_skeleton("basic")
    entity_model = model.create_primitive_model("resources/models/primitives/basic.json")

    position = transform.Transform(la.Vec2(SCREEN_WIDTH/6, SCREEN_HEIGHT/2), la.Vec2(128), 0)
    sample_prim = Primitive(entity_skeleton, entity_model, position)

    sample_prim.animator.add_animation(clip, 1, GAME_CLOCK.run_time, -1, 0.375)
    return sample_prim


class SpriteRenderData:

    def __init__(self, matrices, angles):
        self.matrices: Tuple[Tuple[la.Matrix33, float]] = matrices
        self.angles: Tuple[float] = angles


class Sprites(SkinnedRenderer):

    def __init__(self, render_skeleton, render_model, render_transform):
        super().__init__(render_skeleton, render_model, render_transform)
        self.render_data: SpriteRenderData = None

    def find_render_data(self):
        poses, weights = self.animator.get_poses()
        world_matrix = self.transform.to_matrix()
        joint_matrices = []
        joint_positions = []
        joint_angles = []
        for index, joint in enumerate(self.skeleton.joints):
            inv_matrix = joint.inv_bind_pose_matrix

            if not poses:
                final_joint = joint.joint_model_pos * world_matrix
                joint_matrices.append((world_matrix,))
                joint_positions.append(final_joint)
                joint_angles.append(0)
            else:
                matrices = []
                final_point = la.Vec2(0)
                for k, pose in enumerate(poses):
                    pose_matrix = (inv_matrix * pose[index] * world_matrix *
                                   la.Matrix33.scale_matrix(la.Vec2(weights[k])))
                    final_point += joint.joint_model_pos * pose_matrix
                    matrices.append(pose_matrix)
                joint_matrices.append(tuple(matrices))
                joint_positions.append(final_point)

                if joint.parent != -1:
                    parent_point = joint_positions[joint.parent]
                    angle = (final_point - parent_point).theta
                    joint_angles.append(angle)
                else:
                    joint_angles.append(0)

        self.render_data = SpriteRenderData(tuple(joint_matrices), tuple(joint_angles))

    def draw(self):
        scale = self.transform.scale.x/self.model.model_pixel_scale.x * self.model.model_pixel_scale.y
        if self.render_data is not None:
            for segment in self.model.segment_list:
                index = segment.target_joint
                sprite = segment.sprite

                if sprite.scale != scale:
                    sprite.scale = scale

                sprite.angle = degrees(self.render_data.angles[index])
                position = la.Vec2(0)
                for matrix in self.render_data.matrices[index]:
                    position += segment.model_pos * matrix

                sprite.position = position.x, position.y

        self.model.draw()


def create_sample_sprite_renderer():
    clip = animation.generate_clips("resources/poses/animations/robot_motion.json", 'run')

    render_skeleton = skeleton.create_skeleton("robot")
    render_model = model.create_sprite_model("resources/models/sprites/robot.json")

    position = transform.Transform(la.Vec2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2), la.Vec2(128), 0)
    sample_sprite = Sprites(render_skeleton, render_model, position)
    sample_sprite.animator.add_animation(clip, 1, GAME_CLOCK.run_time, -1, 0.375)
    return sample_sprite
