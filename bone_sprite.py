import arcade
from typing import List

import lin_al as la
import skeleton
import model
import animation


class SkinnedSkeletonPrimitive:
    """
    A skeleton and a primitive model.
    """

    def __init__(self, prim_model: model.PrimitiveModel, prim_skeleton: skeleton.Skeleton = None):
        self.skeleton: skeleton.Skeleton = prim_skeleton
        self.model: model.PrimitiveModel = prim_model
        self.last_pose: skeleton.SkeletonPose = None

