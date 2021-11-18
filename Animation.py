import skeleton
from typing import List


class FramePose:

    def __init__(self):
        self.JointPose: List[skeleton.JointPose]


class Clip:

    def __init__(self):
        self.skeleton = skeleton.Skeleton
