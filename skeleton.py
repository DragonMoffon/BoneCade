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


skeleton_cache: Dict[str, Skeleton] = {}


def make_skeleton_joint(joint_list: List[Joint], parent_index: int, joint_data: dict):
    new_joint = Joint(la.Matrix33(joint_data['matrix']), joint_data['id'], parent_index)
    joint_index = len(joint_list)
    joint_list.append(new_joint)

    for child_data in joint_data['children']:
        make_skeleton_joint(joint_list, joint_index, child_data)


def create_skeleton(target, cache_imperative=1):
    """
    Generate a skeleton object from a json file or loads one from cache.
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

    json_data = json.load(open(f"resources/skeletons/{target}.json"))
    master_joint = Joint(la.Matrix33(json_data['matrix']), json_data['id'], -1)
    joint_list = [master_joint]

    for child_data in json_data['children']:
        make_skeleton_joint(joint_list, 0, child_data)

    skeleton = Skeleton(joint_list, json_data['name'])
    cache(skeleton, json_data['name'], skeleton_cache, cache_imperative)

    return skeleton