import pymunk

class SegmentBody(pymunk.Body):
    def __init__(self, friction=0.2):
        super().__init__(1, float("inf"))
        self.position = 0, 0
        self.elasticity = 0.0
        self.friction = friction

class GenericSegment(pymunk.Segment):
    def __init__(self, body, a, b, radius, shapefilter):
        super().__init__(body, a, b, radius)
        self.mass = 1
        self.elasticity = 0.0
        self.filter = shapefilter

    def anchorTo(self, body, point):
        joint = pymunk.constraints.PinJoint(body, self.body, (0, 0), self.body.world_to_local(point))
        joint.collide_bodies = False
        self.space.add(joint)

    def anchorToStatic(self, point):
        joint = pymunk.constraints.PinJoint(self.space.static_body, self.body, point, point)
        joint.collide_bodies = False
        self.space.add(joint)

    def remove(self):
        for constr in self.body.constraints:
            self.space.remove(constr)
        self.space.remove(self)

class MovingJoint(pymunk.Body):
    def __init__(self, pos, shapefilter):
        super().__init__(1, float("inf"))
        circle = pymunk.Circle
        circle.color = (99, 149, 155, 1)
        circle.filter = shapefilter
        self.position = pos

        self.joint = pymunk.constraints.PinJoint(tracker_body, line.body, (0, 0), line.body.world_to_local(pos))
        self.joint.collide_bodies = False