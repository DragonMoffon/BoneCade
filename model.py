import json
from typing import List

import arcade

import lin_al as la


class JointPrimitive:

    def __init__(self, joint_id, colour, thickness, model_pos, index, parent_index):
        self.id: str = joint_id
        self.colour: arcade.Color = colour
        self.thickness: int = thickness

        self.model_view_pos: la.Vec2 = model_pos

        self.joint_index: int = index

        self.parent_primitive_index: int = parent_index


class PrimitiveModel:
    """
    A model created out of primitive lines.
    """

    def __init__(self, joints: List[JointPrimitive], world_space_position, world_space_rotation):
        self.joint_list: List[JointPrimitive] = joints
        self.master_joint: JointPrimitive = joints[0]

        self.pos: la.Vec2 = world_space_position
        self.scale: la.Vec2 = la.Vec2(50)
        self.rotation: float = world_space_rotation

    def draw(self):
        world_matrix = la.Matrix33.all_matrix(self.pos, self.scale, self.rotation)

        for primitive in self.joint_list:
            point_one = primitive.model_view_pos * world_matrix
            if primitive.parent_primitive_index != -1:
                point_two = self.joint_list[primitive.parent_primitive_index].model_view_pos * world_matrix
                arcade.draw_line(point_one.x, point_one.y, point_two.x, point_two.y,
                                 primitive.colour, primitive.thickness)
            arcade.draw_point(point_one.x, point_one.y, primitive.colour, 5)


def make_prim_joint(joint_list: List[JointPrimitive], parent_index: int, joint_data: dict):
    """
    Recursive generation of Joint Primitive.
    :param joint_list: Model's primitive joints
    :param parent_index: Index of parent
    :param joint_data: The joint data dict
    :return: a Joint Primitive
    """
    new_joint = JointPrimitive(joint_data["id"], joint_data["colour"], joint_data["thickness"],
                               la.Vec2(*joint_data["pos"]), len(joint_list), parent_index)
    joint_list.append(new_joint)
    for child_data in joint_data["children"]:
        make_prim_joint(joint_list, new_joint.joint_index, child_data)


def create_primitive_model(file, position=la.Vec2(0), rotation=0):
    """
    Generates a positioned 2D Primitive Model from a json file.

    :param file: a json file in a parent->child joint tree.
    :param position: 2D position vector
    :param rotation: the rotation of the model in radians (from the model's origin which may not be it's center)
    :return: a 2D primitive Model
    """
    json_data = json.load(open(file))
    master_joint = JointPrimitive(json_data["id"], json_data["colour"], json_data["thickness"],
                                  la.Vec2(*json_data["pos"]), 0, -1)
    joint_list = [master_joint]
    for child_data in json_data["children"]:
        make_prim_joint(joint_list, master_joint.joint_index, child_data)

    return PrimitiveModel(joint_list, position, rotation)
