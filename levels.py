import shapes

class Level:
    def __init__(self, id, space, ui):
        self.ID = id
        self.space = space
        self.ui = ui

    def load(self, space=self.space, id=self.ID):
        self.space = space
        self.ID = id
        for obj in level_layouts[self.ID]:
            if obj[0] == "segment":
                seg = shapes.GenericSegment(self.space.static_body, obj[1], obj[2], 3, )

level_layouts = {
    0: [
        ("segment", (370, 350), (370, 297), "beam", True),
        ("segment", (215, 290), (90, 235), "beam", True),
        ("point", (215, 290)),
        ("point", (520, 290)),
        ()
    ]
}