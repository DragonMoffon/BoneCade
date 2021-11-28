import json
from typing import List, Dict, Tuple
from array import array

import arcade
import arcade.gl as gl

import lin_al as la
from memory import cache


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

    def __init__(self, segments: List[SegmentPrimitive], name):
        self.model_name = name

        self.segment_list: List[SegmentPrimitive] = segments
        self.master_joint: SegmentPrimitive = segments[0]


prim_cache: Dict[str, PrimitiveModel] = {}


def make_prim_segment(joint_list: List[SegmentPrimitive], parent_index: int, joint_data: dict):
    """
    Recursive generation of Joint Primitive.
    :param joint_list: Model's primitive segments
    :param parent_index: Index of parent
    :param joint_data: The joint data dict
    :return: a Joint Primitive
    """
    new_joint = SegmentPrimitive(joint_data["id"], joint_data["colour"], joint_data["thickness"],
                                 la.Vec2(*joint_data["pos"]), len(joint_list), parent_index)
    joint_list.append(new_joint)
    for child_data in joint_data["children"]:
        make_prim_segment(joint_list, new_joint.segment_index, child_data)


def create_primitive_model(file, cache_imperative=1):
    """
    Generates a positioned 2D Primitive Model from a json file.

    :param file: a json file in a parent->child joint tree.
    :param cache_imperative: the cache imperative. This decides whether the model should be cached.
     0 = don't cache, 1 = cache and return, 2 = cache copy and return.
    :return: a 2D primitive Model
    """
    json_data = json.load(open(file))
    master_segment = SegmentPrimitive(json_data["id"], json_data["colour"], json_data["thickness"],
                                      la.Vec2(*json_data["pos"]), 0, -1)
    joint_list = [master_segment]
    for child_data in json_data["children"]:
        make_prim_segment(joint_list, master_segment.segment_index, child_data)

    model = PrimitiveModel(joint_list, json_data['name'])
    cache(model, json_data['name'], prim_cache, cache_imperative)
    return model

# -- SPRITE MODEL --
# This implementation uses multiple separate sprites to draw the model.
# the model assumes that each sprite's center is in the middle of the segment, rather than the end.
# This makes the maths to find where the sprite should sit a little longer and more computationally intensive, but
# saves on a little bit of memory (smaller, and more compact textures)


class SpriteSegment:

    def __init__(self, seg_id, sprite, target_joint, position, depth):
        self.id: str = seg_id
        self.target_joint: int = target_joint
        self.sprite: arcade.Sprite = sprite
        self.model_pos: la.Vec2 = position
        self.depth: float = depth


class SpriteModel:

    def __init__(self, model_name, pixel_scale, segments, sprites=None):
        self.model_name: str = model_name
        self.model_pixel_scale: la.Vec2 = pixel_scale
        # the model pixel scale is the scaling required to map model space to pixel space

        self._sprite_list: arcade.SpriteList = sprites  # a sprite list which is not ordered correctly
        self.segment_list: List[SpriteSegment] = segments  # a list of segments ordered correctly.

        if sprites is None:
            sprite_list = [seg.sprite for seg in sorted(segments, key=lambda seg: seg.depth)
                           if seg.depth != float('inf')]
            self._sprite_list = arcade.SpriteList()
            self._sprite_list.extend(sprite_list)

    def draw(self):
        self._sprite_list.draw(pixelated=True)


sprite_cache: Dict[str, SpriteModel] = {}


def make_sprite_segment(sprite_data, sprite_scale, texture_location, seg_list):
    """
    creates a single sprite segment. By creating a sprite and storing it's depth and id.
    :param sprite_data: a dict of data to create the sprite.
    :param sprite_scale: the scale the sprite must be shrunk to make it that one pixel in the sprite is one screen pixel
    :param texture_location: the location of the texture.
    :param seg_list: all the sprite segments
    :return: a SpriteSegment
    """
    details = sprite_data['piece_data']
    position = sprite_data['position']
    texture = arcade.load_texture(texture_location, details[0], details[1], details[2], details[3])

    sprite = arcade.Sprite()
    sprite.texture = texture
    sprite.scale = sprite_scale

    segment = SpriteSegment(sprite_data['id'], sprite, sprite_data['target_joint'],
                            la.Vec2(position[0], position[1]), position[2])
    seg_list.append(segment)
    for child in sprite_data['children']:
        make_sprite_segment(child, sprite_scale, texture_location, seg_list)


def create_sprite_model(file, cache_imperative=2):
    """
    Generates a model made of a list of sprites derived from a json file.
    :param file: a json file detailing the model.
    :param cache_imperative: the cache imperative. This decides whether the model should be cached.
     0 = don't cache, 1 = cache and return, 2 = cache copy and return.
    :return: a generated model.
    """
    json_data = json.load(open(file))
    segments = []
    sprite_scale = 1/json_data['sprite_scale']
    text_location = json_data['sprite_location']

    for child in json_data['children']:
        make_sprite_segment(child, sprite_scale, text_location, segments)

    model = SpriteModel(json_data['name'], la.Vec2(*json_data['model_pixel_scale']), segments)
    cache(model, json_data['name'], sprite_cache, cache_imperative)

    return model


# -- VERTEX MODEL --
# This implementation uses a vertex buffer to store the values, and uses a vertex shader to position the vertices.
# By doing it this way the 2D characters will not suffer from any splitting when being animated like there is for the
# other two implementations.

class Vertex:

    def __init__(self, pos: la.Vec2, depth: float, uv: la.Vec2,
                 indices: Tuple[int, int, int, int], weights: Tuple[float, float, float]):
        self.pos: la.Vec2 = pos
        self.depth: float = depth
        self.uv: la.Vec2 = uv
        self.joint_indices: Tuple[int, int, int, int] = indices
        self.joint_weights: Tuple[float, float, float] = weights

    def get_data(self):
        # Return indices as vec4
        for index in self.joint_indices:
            print(index)
            yield index
        # yield weights as vec3
        for weight in self.joint_weights:
            print(weight)
            yield weight
        # yield pos and depth as vec3
        yield self.pos.x
        yield self.pos.y
        yield self.depth
        # yield uv values as vec2
        yield self.uv.x
        yield self.uv.y


class MeshModel:

    def __init__(self, model_name, vertices, indices):
        self.model_name: str = model_name

        self.vertices: Tuple[Vertex, ...] = vertices
        self.indices: Tuple[int, ...] = indices
        self.vertex_buffer: gl.Buffer = None
        self.index_buffer: gl.Buffer = None

    def calculate_buffers(self, context: arcade.context.Context):
        self.vertex_buffer = context.buffer(data=array('f', self.get_vertices_data()))
        self.index_buffer = context.buffer(data=array('H', self.get_indices()))

    def get_vertices_data(self):
        for vertex in self.vertices:
            yield from vertex.get_data()

    def get_indices(self):
        for index in self.indices:
            yield index


def load_mesh_model(model_name):
    vertex_positions = []
    vertex_uvs = []
    vertex_weights = []
    vertices_data: List[Tuple[int, int]] = []
    triangles = []

    def get_position(data: List[str]):
        position = la.Vec2(float(data[0]), -float(data[2]))
        depth = float(data[1])
        vertex_positions.append((position, depth))

    def get_uvs(data: List[str]):
        uv = la.Vec2(float(data[0]), float(data[1]))
        vertex_uvs.append(uv)

    def make_triangle(data: List[str]):
        for index in data:
            index = index.split('/')
            vert = (int(index[0])-1, int(index[1])-1)
            if vert not in vertices_data:
                vertices_data.append(vert)
            triangles.append(vertices_data.index(vert))

    obj_line_starters = {'v': get_position, 'vt': get_uvs, 'f': make_triangle}

    with open(f"resources/blends/{model_name}.obj", 'rt') as model_obj:
        for line in model_obj.readlines():
            line = line.rstrip('\n')
            line_data = line.split(' ')
            if line_data[0] in obj_line_starters:
                obj_line_starters[line_data[0]](line_data[1:])

    with open(f"resources/blends/{model_name}.wt", 'rt') as model_weights:
        for line in model_weights.readlines():
            line = line.rstrip("\n").split("|")
            joint_indices = tuple(map(int, line[0].split()))
            joint_weights = tuple(map(float, line[1].split()))
            vertex_weights.append((joint_indices, joint_weights))

    vertices = []
    for vertex, uv in vertices_data:
        pos = vertex_positions[vertex][0]
        depth = vertex_positions[vertex][1]
        uv = vertex_uvs[uv]
        indices = vertex_weights[vertex][0]
        weights = vertex_weights[vertex][1]
        vertices.append(Vertex(pos, depth, uv, indices, weights))

    return MeshModel(model_name, vertices, triangles)
