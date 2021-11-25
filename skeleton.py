# The main skeleton classes. These will start by being rendered as arcade.draw_lines (child to parent)
#   The aims are to get sprites working with the skeleton, and then to generated 2d meshes with joint weights.
#
#   The system I am following has the skeleton and all the other classes as simple data classes. These are then used
#   by the animation system to make a list of model space to world space matrices which are passed each update to the
#   render engine.
#
#   This leaves most of the joint calculations on the CPU. Since there is no proper support for compute shaders within
#   arcade this may be the largest bottleneck. I could send stripped down joint data along to the render engine.
#   This would allow me to construct the final model space to world space matrices in the vertex shader.
#
#   An issue for later, and something that will need to be profiled.

from typing import List, Dict
from copy import deepcopy
import json

import arcade

import lin_al as la
from lin_al import RotTrans
from memory import cache


class Joint:

    def __init__(self, inv_matrix, joint_name, parent):
        self.inv_bind_pose_matrix: la.Matrix33 = inv_matrix
        self.joint_model_pos: la.Vec2 = la.Vec2(0) * la.Matrix33.lazy_inverse(inv_matrix)
        self.joint_name: str = joint_name
        self.parent: int = parent


class Skeleton:

    def __init__(self, joint_list, name):
        self.skeleton_id: str = name
        self.joint_count: int = len(joint_list)
        self.joints: List[Joint] = joint_list


def draw_skeleton(skeleton: Skeleton, world_matrix: la.Matrix33):
    joint_parents = []
    for joint in skeleton.joints:
        position = joint.joint_model_pos * world_matrix

        if joint.parent != -1:
            parent_position = joint_parents[joint.parent]
            arcade.draw_line(position.x, position.y, parent_position.x, parent_position.y, arcade.color.RADICAL_RED, 2)
        arcade.draw_point(position.x, position.y, arcade.color.ORANGE, 5)

        joint_parents.append(position)


skeleton_cache: Dict[str, Skeleton] = {}


def make_skeleton_joint(joint_list: List[Joint], parent_index: int, joint_data: dict):
    new_joint = Joint(la.Matrix33(joint_data['matrix']), joint_data['id'], parent_index)
    joint_index = len(joint_list)
    joint_list.append(new_joint)

    for child_data in joint_data['children']:
        make_skeleton_joint(joint_list, joint_index, child_data)


def create_skeleton(file, target, cache_imperative=1):
    """
    Generate a skeleton object from a json file or loads one from cache.
    :param file: the file location
    :param target: The target skeleton to load.
    :param cache_imperative: the cache imperative. This decides whether the skeleton should be cached.
     0 = don't cache, 1 = cache and return, 2 = cache copy and return.
    :return:
    """
    if target in skeleton_cache:
        if cache_imperative == 2:
            return deepcopy(skeleton_cache[target])
        else:
            return skeleton_cache[target]

    json_data = json.load(open(file))
    master_joint = Joint(la.Matrix33(json_data['matrix']), json_data['id'], -1)
    joint_list = [master_joint]

    for child_data in json_data['children']:
        make_skeleton_joint(joint_list, 0, child_data)

    skeleton = Skeleton(joint_list, json_data['name'])
    cache(skeleton, json_data['name'], skeleton_cache, cache_imperative)

    return skeleton


class SkeletonPose:

    def __init__(self, skeleton, joint_poses, model_poses=None):
        self.skeleton: Skeleton = skeleton
        self.joint_poses: List[RotTrans] = joint_poses  # relative to parent joint
        self.model_poses: List[la.Matrix33] = model_poses  # relative to model space
        if model_poses is None:
            self.calculate_model_poses()

    def calculate_model_poses(self):
        model_poses = []
        for index, joint in enumerate(self.skeleton.joints):
            if joint.parent != -1:
                former_matrix = model_poses[joint.parent]
            else:
                former_matrix = la.Matrix33()

            current_matrix = self.joint_poses[index].to_matrix() * former_matrix
            model_poses.append(current_matrix)

        self.model_poses = model_poses
        return model_poses

    def temp_draw(self, temp_matrix):
        """
        Draws the Skeleton Pose for debugging.
        :param temp_matrix: a model -> world view matrix
        """
        world_pos_joints = []
        index = 0
        while index < len(self.skeleton.joints):
            skeleton_joint = self.skeleton.joints[index]
            joint_pose = self.model_poses[index]

            current_point = la.Vec2(0) * joint_pose * temp_matrix
            x_axis = la.Vec2(0.1, 0.0) * joint_pose * temp_matrix
            y_axis = la.Vec2(0.0, 0.1) * joint_pose * temp_matrix

            world_pos_joints.append(current_point)

            if skeleton_joint.parent >= 0:
                parent = world_pos_joints[skeleton_joint.parent]
                arcade.draw_line(current_point.x, current_point.y, parent.x, parent.y, arcade.color.ORANGE, 2)

            arcade.draw_circle_filled(current_point.x, current_point.y, 4, arcade.color.LILAC)
            arcade.draw_line(current_point.x, current_point.y, x_axis.x, x_axis.y, arcade.color.RED)
            arcade.draw_line(current_point.x, current_point.y, y_axis.x, y_axis.y, arcade.color.GREEN)

            index += 1

        return world_pos_joints


pose_cache: Dict[str, SkeletonPose] = {}


def get_pose(file, target_pose, cache_imperative: int = 1):
    """
    Generate a skeleton pose from a json file or cache.
    :param file: The target json file
    :param target_pose: The specific pose, either from the cache or the json file
    :param cache_imperative: the cache imperative. This decides whether the skeleton should be cached.
     0 = don't cache, 1 = cache and return, 2 = cache copy and return.
    :return:
    """
    if target_pose in pose_cache:
        if cache_imperative == 2:
            return deepcopy(pose_cache[target_pose])
        else:
            return pose_cache[target_pose]

    json_data = json.load(open(file))
    skeleton = create_skeleton(f"skeletons/{json_data['target']}.json", json_data['target'])
    pose_data = json_data['poses'][target_pose]

    joint_poses = []
    model_poses = []

    for index, joint in enumerate(skeleton.joints):
        pose = pose_data[index]
        current_pose = RotTrans(*pose)

        if joint.parent != -1:
            former_matrix = model_poses[joint.parent]
        else:
            former_matrix = la.Matrix33()

        current_matrix = current_pose.to_matrix() * former_matrix

        joint_poses.append(current_pose)
        model_poses.append(current_matrix)

    pose = SkeletonPose(skeleton, joint_poses, model_poses)
    cache(pose, target_pose, pose_cache, cache_imperative)

    return pose
