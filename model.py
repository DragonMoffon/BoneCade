import json
from typing import List

import arcade

import lin_al as la


# -- PRIMITIVE MODELS --
# This implementation creates stick figures made of python arcade primitives.


class SegmentPrimitive:

    def __init__(self, joint_id, colour, thickness, model_pos, index, parent_index):
        self.id: str = joint_id
        self.colour: arcade.Color = colour
        self.thickness: int = thickness

        self.model_view_pos: la.Vec2 = model_pos

        self.segment_index: int = index

        self.parent_primitive_index: int = parent_index


class PrimitiveModel:
    """
    A model created out of primitive lines.
    """

    def __init__(self, joints: List[SegmentPrimitive], world_space_position, world_space_rotation, name):
        self.model_name = name

        self.segment_list: List[SegmentPrimitive] = joints
        self.master_joint: SegmentPrimitive = joints[0]

        self._pos: la.Vec2 = world_space_position
        self._scale: la.Vec2 = la.Vec2(50)
        self._rotation: float = world_space_rotation

        self.world_matrix = la.Matrix33.all_matrix(self._pos, self._scale, self._rotation)  # model -> world matrix

    def update_world_matrix(self):
        self.world_matrix = la.Matrix33.all_matrix(self._pos, self._scale, self._rotation)

    def draw(self):
        for primitive in self.segment_list:
            point_one = primitive.model_view_pos * self.world_matrix
            if primitive.parent_primitive_index != -1:
                point_two = self.segment_list[primitive.parent_primitive_index].model_view_pos * self.world_matrix
                arcade.draw_line(point_one.x, point_one.y, point_two.x, point_two.y,
                                 primitive.colour, primitive.thickness)
            arcade.draw_point(point_one.x, point_one.y, primitive.colour, 5)

    def reposition(self, new_pos, new_scale, new_rotation):
        self._pos = new_pos
        self._scale = new_scale
        self._rotation = new_rotation

        self.update_world_matrix()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value: la.Vec2):
        self._pos = value
        self.update_world_matrix()

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value: la.Vec2):
        self._scale = value
        self.update_world_matrix()

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value: float):
        self._rotation = value
        self.update_world_matrix()


def make_prim_segment(joint_list: List[SegmentPrimitive], parent_index: int, joint_data: dict):
    """
    Recursive generation of Joint Primitive.
    :param joint_list: Model's primitive joints
    :param parent_index: Index of parent
    :param joint_data: The joint data dict
    :return: a Joint Primitive
    """
    new_joint = SegmentPrimitive(joint_data["id"], joint_data["colour"], joint_data["thickness"],
                                 la.Vec2(*joint_data["pos"]), len(joint_list), parent_index)
    joint_list.append(new_joint)
    for child_data in joint_data["children"]:
        make_prim_segment(joint_list, new_joint.segment_index, child_data)


def create_primitive_model(file, position=la.Vec2(0), rotation=0):
    """
    Generates a positioned 2D Primitive Model from a json file.

    :param file: a json file in a parent->child joint tree.
    :param position: 2D position vector
    :param rotation: the rotation of the model in radians (from the model's origin which may not be it's center)
    :return: a 2D primitive Model
    """
    json_data = json.load(open(file))
    master_segment = SegmentPrimitive(json_data["id"], json_data["colour"], json_data["thickness"],
                                      la.Vec2(*json_data["pos"]), 0, -1)
    joint_list = [master_segment]
    for child_data in json_data["children"]:
        make_prim_segment(joint_list, master_segment.segment_index, child_data)

    return PrimitiveModel(joint_list, position, rotation, json_data['name'])


# -- SPRITE MODEL --
# This implementation uses multiple separate sprites to draw the model.
# the model assumes that each sprite's center is in the middle of the segment, rather than the end.
# This makes the maths to find where the sprite should sit a little longer and more computationally intensive, but
# saves on a little bit of memory (smaller, and more compact textures)


# -- VERTEX MODEL --
# This implementation uses a vertex buffer to store the values, and uses a vertex shader to position the vertices.
# By doing it this way the 2D characters will not suffer from any splitting when being animated like there is for the
# other two implementations.
