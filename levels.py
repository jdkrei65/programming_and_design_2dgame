import shapes

# I don't have' anything here yet, this is what I'm working on now.

class Level:
    def __init__(self, id, space, ui):
        self.ID = id
        self.space = space
        self.ui = ui

    def load(self):
        pass

level_layouts = {
    0: [
        ("segment", (370, 350), (370, 297), "beam", True),
        ("segment", (215, 290), (90, 235), "beam", True),
        ("point", (215, 290)),
        ("point", (520, 290)),
        ()
    ]
}