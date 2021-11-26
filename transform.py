import lin_al as la


class Transform:

    def __init__(self, position: la.Vec2, scale: la.Vec2, rotation: float, depth=0):
        self.position: la.Vec2 = position
        self.scale: la.Vec2 = scale
        self.rotation: float = rotation
        self.depth: float = depth

    def set_all(self, position, scale, rotation, depth=0):
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self.depth = depth

    def to_matrix(self):
        return la.Matrix33.all_matrix(self.position, self.scale, self.rotation)

    def to_inverse(self):
        return la.Matrix33.inverse_all_matrix(self.position, self.scale, self.rotation)
