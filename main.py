import pgzrun
import pymunk
import pymunk.pygame_util
import pymunk.constraints
import math
import shapes
import levels
import random
import UI
import copy

#
# A world where you can place lines, points, and balls to build something.
# Scroll to pick a different tool
# Click to use the tool
#

interface = UI.UserInterface()  # create a user interface instance.

space = pymunk.Space()      # setup the world for pymunk
space.gravity = (0, 50)

SPACE_SAVED = pymunk.Space()    # a savestate variable
TRACKERS_SAVED = []

WIDTH = 800     # set the window size
HEIGHT = 600

BG_COLOR = (78, 96, 98, 1)

tool = 0        # some variables to name the different tools
tools = 11
STEEL = 0
PLANK = 1
BEAM = 2
ROPE = 3
BALL = 4
ANCHOR = 5
MOVING_JOINT = 6
MOTOR = 7
HYDRAULIC = 8
PLAYPAUSE = 9
DELETE = 10
RESET = 11

toolnames = {
    STEEL:  "Steel Beam     (collides with nothing)",
    PLANK:  "Wood Plank     (collides with beams and balls)",
    BEAM:   "Generic Beam   (collides with wood and balls)",
    ROPE:   "Rope           (constrains the distance between two joints)",
    BALL:   "Ball           (it rolls)",
    ANCHOR: "Anchor         (allows you to pin steel/planks/beams to a specific point)",
    MOVING_JOINT:   "Joint          (allows you to pin steel/planks/beams to each other)",
    MOTOR:  "Motor          (makes steel/planks/beams rotate)",
    HYDRAULIC:  "Nothing        (it does nothing)",
    PLAYPAUSE:  "Play/Pause     (starts/pauses the simulation)",
    DELETE: "Delete         (deletes a segment or anchor)",
    RESET:  "Reset          (Deletes everything and resets the simulation)"
}

background = Actor('background')    # set up actors
menu = Actor("menu")
menu.midleft = 0,300
pointer = Actor("selection")
pointer.midleft = 32, 300-48

points = []     # lists to keep track of the objects in the world
lines = []
moving_joint_trackers = []
sel_point = None    # variables to keep track of selected points/joints for lines (and anything else that needs two selections)
sel_joint = None

paused = True

steel_len = 120
plank_len = 50
beam_len = 80

preview_body = pymunk.Body(pymunk.Body.STATIC)  # a static body for "preview" lines.
space.add(preview_body)

LEVEL_ID = 0
current_level = levels.Level(LEVEL_ID, space, interface)

TOP_TEXT = text = UI.Text(WIDTH / 2 - 128, 14, "", (0, 0, 0))
interface.attachElement(TOP_TEXT)

def clear_space():
    global space
    global points
    global lines
    global moving_joint_trackers
    global sel_joint
    global current_level
    global paused
    space = pymunk.Space()
    space.gravity = (0, 50)
    points = []
    lines = []
    moving_joint_trackers = []
    sel_joint = None

    current_level = levels.Level(LEVEL_ID, space, interface)
    current_level.load(points, LEVEL_ID, Actor)
    paused = True

clear_space()

def distance(a, b):
    try:
        ax, ay = a
        bx, by = b
        return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
    except ZeroDivisionError:
        return 0

def draw():
    interface.screen = screen
    interface.clock = clock
    screen.fill(BG_COLOR)
    background.draw()

    surf = screen.surface
    options = pymunk.pygame_util.DrawOptions(surf)  # have pymunk do a debug draw. I need to eventually replace this with something better.
    space.debug_draw(options)

    for shape in moving_joint_trackers:
        screen.draw.filled_circle(shape.position, 7, (79, 189, 195))

    for line in lines:  # draw all the lines and points
        line.draw()
    for point in points:
        point.draw()

    interface.draw()    # draw the user interface

    menu.draw()     # draw the side menu, and the menu pointer.
    pointer.draw()

    if paused:
        screen.draw.text("Simulation Paused", (5, 5))
    screen.draw.text("(scroll to change) Tool:", (5, HEIGHT-45))
    screen.draw.text(toolnames[tool], (5, HEIGHT-20))

def update(dt):
    global LEVEL_ID
    if not paused:      # update the physics engine
        space.step(dt)

    #TOP_TEXT.text = f"{distance(current_level.ball.body.position, current_level.goals[0].offset)}"

    if not current_level.ball in space.shapes:
        if current_level.ball in SPACE_SAVED.shapes:
            SPACE_SAVED.remove(current_level.ball)
        if not current_level.ball_body in space.bodies:
            space.add(current_level.ball_body)
        space.add(current_level.ball)

    if current_level.ball:
        if distance(current_level.ball.body.position, current_level.goals[0].offset) < 25:
            print("level cleared!")
            LEVEL_ID += 1
            clear_space()

        # print(current_level.goals[0].shapes_collide(current_level.ball))
        # if len(current_level.goals[0].shapes_collide(current_level.ball).points) > 0:
        #     print("HIT")

    preview_body.position = 0,0
    pointer.midleft = 32, 300-176+32*tool

def place_bar(pos, sfilter, linecolor=(128, 31, 31, 1), radius=3, max_length=999):  # place a segment
    global sel_point
    global sel_joint
    global interface
    if sel_point:       # if a point is selected
        if sel_joint:
            sel_point = sel_joint.position  # if a joint was selected, set the selected point to the joint's position.
        if distance(sel_point, pos) > max_length:
            TOP_TEXT.text = f"Your line is too long! ({int(distance(sel_point, pos))} >= {max_length})"
            return
        line_body = shapes.SegmentBody()    # create the segment
        line = shapes.GenericSegment(line_body, a=sel_point, b=pos, radius=radius, sfilter=sfilter)
        line.color = linecolor
        space.add(line_body, line)  # add it to the physics space

        if sel_joint:   # attach the line to a joint if one was selected
            line.anchorTo(sel_joint, sel_point)
        for tracker in moving_joint_trackers:   # if the second point is near a joint, attach to it as well
            if distance(pos, tracker.position) < 7:
                line.anchorTo(tracker, pos)
        for point in points:
            if distance(sel_point, point.pos) < 7:  # if either end of the segment is near a static point, attach to it.
                line.anchorToStatic(sel_point)
            if distance(pos, point.pos) < 7:
                line.anchorToStatic(pos)

        sel_point = None
        sel_joint = None
        return line

    else:       # if no first point was selected, then select one
        sel_point = pos
        for tracker in moving_joint_trackers:   # if the selection is near a joint, then select it.
            if distance(pos, tracker.position) < 7:
                sel_joint = tracker
        return None

def place_steel(pos, r):
    if not current_level.options["allow_steel"] == True:
        TOP_TEXT.text = "You can't place steel in this level!"
        return
    # the different segment types
    max_length = WIDTH*2
    if r:
        max_length = steel_len
    place_bar(pos, shapes.steel_filter, (128, 31, 31, 1), 3, max_length)

def place_plank(pos, r):
    if not current_level.options["allow_wood"] == True:
        TOP_TEXT.text = "You can't place planks in this level!"
        return
    max_length = WIDTH * 2
    if r:
        max_length = plank_len
    place_bar(pos, shapes.plank_filter, (120, 92, 13, 1), 3, max_length)

def place_beam(pos, r):
    if not current_level.options["allow_beam"] == True:
        TOP_TEXT.text = "You can't place beams in this level!"
        return
    max_length = WIDTH * 2
    if r:
        max_length = beam_len
    place_bar(pos, shapes.beam_filter, (120, 120, 120, 1), 3, max_length)

def place_rope(pos):    # a "slide" joint. Keeps two points at equal or less distance.
    if not current_level.options["allow_rope"] == True:
        TOP_TEXT.text = "You can't place rope in this level!"
        return
    global sel_point
    global preview_body
    global sel_joint
    if sel_point:
        if sel_joint:
            sel_point = sel_joint.position

        body_b = None

        for point in points:
            if distance(pos, point.pos) < 7:
                body_b = space.static_body

        for tracker in moving_joint_trackers:
            if distance(pos, tracker.position) < 7:
                body_b = tracker

        if sel_joint and body_b:
            body_a = sel_joint
            slide_joint = pymunk.constraints.SlideJoint(body_a, body_b, body_a.world_to_local(sel_point), body_b.world_to_local(pos), 0, distance(sel_point, pos))
            space.add(slide_joint)

        sel_point = None
        sel_joint = None
        for shape in preview_body.shapes:
            space.remove(shape)
        preview_body = pymunk.Body(pymunk.Body.STATIC, float("inf"))
        space.add(preview_body)
    else:
        sel_point = pos
        for tracker in moving_joint_trackers:
            if distance(pos, tracker.position) < 7:
                sel_joint = tracker

def place_anchor(pos):          # place a static anchor point
    if not current_level.options["allow_static_point"] == True:
        TOP_TEXT.text = "You can't place static points/anchors in this level!"
        return
    point = Actor("connector")
    point.center = pos
    points.append(point)

def find_line(pos):         # find the line at the given position
    query = space.point_query_nearest(pos, 3, shapes.any_structure)
    if query:
        return query.shape
    else: return None

def place_motor(line, a):   # add a motor to a line segment
    if not current_level.options["allow_motors"] == True:
        TOP_TEXT.text = "You can't place motors in this level!"
        return
    motor = pymunk.constraints.SimpleMotor(space.static_body, line.body, a)
    space.add(motor)

def spawn_ball(pos):        # spawn a ball at the given position
    for shape in space.shapes:
        if isinstance(shape, pymunk.Circle) and not shape.sensor:
            space.remove(shape)

    ball_body = pymunk.Body(1, float("inf"))
    ball_body.position = current_level.spawn_pos #pos
    ball = pymunk.Circle(ball_body, 10)
    ball_body.friction = 0.1
    ball.color = (46, 72, 135, 1)
    ball.filter = shapes.ball_filter
    space.add(ball_body, ball)

def delete_hovered_bodies(pos):     # delete the segment at the given point
    for point in points:
        if distance(pos, point.pos) < 7:
            points.remove(point)

    query = space.point_query_nearest(pos, 3, shapes.any_structure)
    if query:
        shape = query.shape
        if isinstance(shape, shapes.GenericSegment):
            shape.remove()


def place_moving_joint(pos):    # place a joint on a segment
    if not current_level.options["allow_moving_joint"] == True:
        TOP_TEXT.text = "You can't place joints in this level!"
        return
    query = space.point_query_nearest(pos, 3, shapes.any_structure)
    if query:
        line = query.shape
        if not line.can_have_joints:
            return

        tracker_body = pymunk.Body(1, float("inf"))
        tracker = pymunk.Circle(tracker_body, 4)
        tracker.color = (79, 149, 195, 1)
        tracker.filter = shapes.joint_filter
        tracker_body.position = pos
        space.add(tracker_body, tracker)

        line.anchorTo(tracker_body, pos)
        moving_joint_trackers.append(tracker_body)

def on_mouse_down(pos, button):
    global tool
    global paused
    global points
    global lines
    global moving_joint_trackers
    global space
    global sel_joint
    global interface
    global SPACE_SAVED
    global TRACKERS_SAVED
    if button == mouse.LEFT:    # do the appropriate action for the selected item.
        if interface.mousePressedEvent(pos):
            return

        if tool == STEEL:
            place_steel(pos, True)
        elif tool == PLANK:
            place_plank(pos, True)
        elif tool == BEAM:
            place_beam(pos, True)
        elif tool == ANCHOR:
            place_anchor(pos)
        elif tool == BALL:
            spawn_ball(pos)
        elif tool == MOVING_JOINT:
            place_moving_joint(pos)
        elif tool == ROPE:
            place_rope(pos)
        elif tool == PLAYPAUSE:
            paused = not paused
            if paused:
                moving_joint_trackers = [] #copy.deepcopy(TRACKERS_SAVED)
                if current_level.ball in space.shapes:
                    space.remove(current_level.ball)
                if current_level.ball in SPACE_SAVED.shapes:
                    SPACE_SAVED.remove(current_level.ball)

                if current_level.ball_body in space.bodies:
                    space.remove(current_level.ball_body)
                if current_level.ball_body in SPACE_SAVED.bodies:
                    SPACE_SAVED.remove(current_level.ball_body)

                space = None
                space = copy.deepcopy(SPACE_SAVED)
                current_level.ball_body.position = current_level.spawn_pos
                current_level.ball_body.velocity = (0, 0)
                for j in moving_joint_trackers:
                    space.add(j)
            else:
                if current_level.ball in SPACE_SAVED.shapes:
                    SPACE_SAVED.remove(current_level.ball)
                if current_level.ball in space.shapes:
                    space.remove(current_level.ball)

                if current_level.ball_body in space.bodies:
                    space.remove(current_level.ball_body)
                if current_level.ball_body in SPACE_SAVED.bodies:
                    SPACE_SAVED.remove(current_level.ball_body)

                TRACKERS_SAVED = copy.deepcopy(moving_joint_trackers)
                SPACE_SAVED = None
                SPACE_SAVED = copy.deepcopy(space)
                #for j in TRACKERS_SAVED:
                #    SPACE_SAVED.remove(j)

        elif tool == DELETE:
            delete_hovered_bodies(pos)
        elif tool == MOTOR:
            line = find_line(pos)
            if line:
                if "placemotor" in interface.events:
                    return
                interface.createEvent("placemotor", place_motor, line, once=True)
                cwa = Actor('clockwise.png', center=(WIDTH/2 - 4, HEIGHT/2 + 2))
                cwBtn = UI.Button(cwa, 'clockwise.png', 'clockwise_h.png')
                cwBtn.addEvent("placemotor", -1)

                ccwa = Actor('counterclockwise.png', center=(WIDTH/2 + 36, HEIGHT/2 + 2))
                ccwBtn = UI.Button(ccwa, 'counterclockwise.png', 'counterclockwise_h.png')
                ccwBtn.addEvent("placemotor", 1)

                bg = UI.UIActor(Actor('uiselection.png', center=(WIDTH/2, HEIGHT/2)))
                icon = UI.Button(Actor('motor.png', center=(WIDTH/2 - 46, HEIGHT/2 + 2)), 'motor.png', 'cancel.png')
                text = UI.Text(WIDTH/2 - 64, HEIGHT/2 - 36, "Pick a direction:", (0, 0, 0))

                ccwBtn.addEvent("_removeelements", cwBtn, ccwBtn, bg, icon, text)
                cwBtn.addEvent("_removeelements", cwBtn, ccwBtn, bg, icon, text)
                icon.addEvent("_removeelements", cwBtn, ccwBtn, bg, icon, text)
                icon.addEvent("_discardevents", "placemotor")

                interface.attachElement(bg)
                interface.attachElement(icon)
                interface.attachElement(text)

                interface.attachElement(cwBtn)
                interface.attachElement(ccwBtn)

        elif tool == RESET:     # reset the entire space.
            if "clearspace" in interface.events:
                return
            interface.createEvent("clearspace", clear_space, once=True)
            cwa = Actor('yes.png', center=(WIDTH / 2 - 4, HEIGHT / 2 + 2))
            cwBtn = UI.Button(cwa, 'yes.png', 'yes_h.png')
            cwBtn.addEvent("clearspace")

            ccwa = Actor('no.png', center=(WIDTH / 2 + 36, HEIGHT / 2 + 2))
            ccwBtn = UI.Button(ccwa, 'no.png', 'no_h.png')
            ccwBtn.addEvent("_discardevents", "clearspace")

            bg = UI.UIActor(Actor('uiselection.png', center=(WIDTH / 2, HEIGHT / 2)))
            icon = UI.Button(Actor('cancel.png', center=(WIDTH / 2 - 46, HEIGHT / 2 + 2)), 'cancel.png', 'cancel.png')
            text = UI.Text(WIDTH / 2 - 64, HEIGHT / 2 - 36, "Reset the level?", (0, 0, 0))

            ccwBtn.addEvent("_removeelements", cwBtn, ccwBtn, bg, icon, text)
            cwBtn.addEvent("_removeelements", cwBtn, ccwBtn, bg, icon, text)

            interface.attachElement(bg)
            interface.attachElement(icon)
            interface.attachElement(text)

            interface.attachElement(cwBtn)
            interface.attachElement(ccwBtn)

    elif button == mouse.RIGHT: # useful for debugging.
        print(pos)

    elif button == mouse.WHEEL_UP:
        tool -= 1
        if tool < 0:
            tool = tools
    elif button == mouse.WHEEL_DOWN:
        tool += 1
        if tool > tools:
            tool = 0

def on_mouse_move(pos):
    global sel_point
    global preview_body
    interface.mouseMotionEvent(pos) # send the event to the UI
    for shape in preview_body.shapes:
        space.remove(shape)
    preview_body = pymunk.Body(pymunk.Body.STATIC, float("inf"))    # reset the preview body
    space.add(preview_body)
    if not sel_point == None:   # preview the segment you're creating, if any
        tool_max_len = 999
        if tool == STEEL:
            tool_max_len = steel_len
        elif tool == PLANK:
            tool_max_len = plank_len
        elif tool == BEAM:
            tool_max_len = beam_len
        dist = distance(sel_point, pos)
        line = pymunk.Segment(preview_body, a=sel_point, b=pos, radius=3)
        line.color = (173, 152, 94, 1)
        if dist > tool_max_len:
            line.color = (255, 152, 94, 1)
        line.sensor = True
        space.add(line)
    if tool == DELETE:      # if the tool is set to delete, highlight the segment that will be deleted.
        query = space.point_query_nearest(pos, 3, shapes.any_structure)
        if query:
            shape = query.shape
            if isinstance(shape, pymunk.Segment):
                preview_body = pymunk.Body(pymunk.Body.STATIC, float("inf"))
                space.add(preview_body)
                line = pymunk.Segment(preview_body, a=shape.a, b=shape.b, radius=shape.radius+2)
                line.color = (255, 0, 0, 1)
                line.sensor = True
                space.add(line)

pgzrun.go()