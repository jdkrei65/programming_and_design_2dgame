import shapes
import pymunk

class Level:
    def __init__(self, id, space, ui):
        self.ID = id
        self.space = space
        self.ui = ui
        self.goals = []
        self.spawn_pos = (0, 0)

    def load(self, pl, id, Actor=None):
        self.ID = id
        goals = []
        ball_pos = None
        for obj in level_layouts[self.ID]:
            if obj[0] == "segment":
                seg = shapes.GenericSegment(self.space.static_body, obj[1], obj[2], 3, obj[3])
                seg.can_have_joints = False
                seg.color = (140, 150, 200, 1)
                self.space.add(seg)
            elif obj[0] == "point":
                pt = Actor("connector")
                pt.center = obj[1]
                pl.append(pt)
            elif obj[0] == "ball":
                ball_body = pymunk.Body(1, float("inf"))
                ball_body.position = obj[1]
                ball = pymunk.Circle(ball_body, 10)
                ball_body.friction = 0.1
                ball.color = (46, 72, 135, 1)
                ball.filter = shapes.ball_filter
                self.space.add(ball_body, ball)
                ball_pos = obj[1]
            elif obj[0] == "goal":
                ng = pymunk.Circle(self.space.static_body, obj[2], obj[1])
                ng.sensor = True
                ng.color = (140, 200, 150, 1)
                self.space.add(ng)
                goals.append(ng)
            else:
                raise NotImplementedError(f"Cannot use '{obj[0]}' to construct a level!")
        self.goals = goals
        self.spawn_pos = ball_pos

        return None

level_layouts = {
    0: [
        ("segment", (370, 350), (370, 297), shapes.prepl_filter),
        ("segment", (215, 290), (90, 235), shapes.prepl_filter),
        ("point",   (215, 290)),
        ("point",   (520, 290)),
        ("ball",    (93, 222)),
        ("goal",    (575, 301), 20)
    ]
}
