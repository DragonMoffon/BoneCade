import skeleton
from typing import List


class FramePose:
    """
    An individual skeleton pose. This is a "key frame" for an animation which the system interpolates between
    """

    def __init__(self):
        self.JointPose: List[skeleton.JointPose] = None


class Clip:
    """
    A collection of FramePoses with information on the run speed
    """

    def __init__(self):
        self.skeleton: skeleton.Skeleton = None
        self.frames: List[FramePose] = None
        self.frames_per_second: float = None
        self.frame_count: int = None
        self.is_looping: bool = None


class Animation:
    """
    A run-time object with details on which clip to use, plus the clip's playback speed, and if the clip is animating
    """

    def __init__(self):
        self.clip_reference: str = None
        self.clip_time_start: float = None
        self.clip_time_pos: float = None

        self.clip_weight: float = None

        self.clip_enabled: bool = None
        self.clip_looped: bool = None
