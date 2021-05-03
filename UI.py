
class UserInterface:
    def __init__(self):
        self.parent = None
        self.screen = None
        self.clock = None
        self.mouse_position = (0, 0)
        self.elements = []
        self.events = {}
        self.builtinEvents()

    def clear(self):            # remove all the elements and events
        self.elements = []
        self.events = {}
        self.builtinEvents()

    def builtinEvents(self):    # create some events for basic functions so that they can be called when buttons are pressed.
        self.createEvent("_removeelements", self.removeElements)
        self.createEvent("_discardevents", self.discardEvents)
        self.createEvent("_scheduleevents", self.scheduleEvents)

    def scheduleEvents(self, *events, time=1.0):
        for event in events:
            self.clock.schedule(lambda: self.callEvent(event), time)

    def attachElement(self, element):   # add an element to the user interface
        element.parent = self
        self.elements.append(element)

    def draw(self):             # draw all the attached elements
        for element in self.elements:
            element.draw()

    def mouseMotionEvent(self, position):   # update each element with the new mouse position
        self.mouse_position = position
        for element in self.elements:
            element.mouseMotionEvent(position)

    def mousePressedEvent(self, position):  # notify each element of the button press. When calling this, it returns True if something was pressed
        elmts = self.elements.copy()
        elmts.reverse()
        for element in elmts:
            if element.mousePressedEvent(position):
                return True
        return False

    def createEvent(self, name, function, *args, once=False):   # create an event that can be called
        self.events[name] = (function, args, once)

    def callEvent(self, name, *args):   # call a created event
        f, a, o = self.events[name]
        f(*a, *args)
        if o:
            self.discardEvents(name)

    def removeElements(self, *elems):   # remove an element from the interface
        for element in elems:
            self.elements.pop(self.elements.index(element))

    def discardEvents(self, *names):       # remove an event from the interface
        for name in names:
            self.events.pop(name)

    def set_screen(self, screen):       # set the pygamezero screen
        self.screen = screen

class UIElement:        # a generic UI element
    def __init__(self):
        self.parent = None
        self.hovered = False
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
    def mouseMotionEvent(self, position):   # when the mouse is moved, if the element is hovered, call the onHover function
        x2 = self.x + self.width
        y2 = self.y + self.height
        a, b = position
        if self.x <= a and self.y <= b and x2 >= a and y2 >= b:
            self.onHover((a-self.x, b-self.x))
            self.hovered = True
        else:
            self.endHover()
            self.hovered = False

    def mousePressedEvent(self, position):  # when the mouse is pressed, if it's over the button, call the onPress function
        x2 = self.x + self.width
        y2 = self.y + self.height
        a, b = position
        if self.x <= a and self.y <= b and x2 >= a and y2 >= b:
            if hasattr(self, 'onPress'):    # call the onPress event if the click is over the button, and the subclass has it
                self.onPress((a - self.x, b - self.x))
                return True
        return False

    def onHover(self, position):
        pass

    def endHover(self):
        pass

    def draw(self):
        pass

class Button(UIElement):
    def __init__(self, actor, image, himage):
        super().__init__()
        self.x = actor.left
        self.y = actor.top
        self.width = actor.width
        self.height = actor.height
        self.image = image
        self.himage = himage
        self.actor = actor
        self.events = []
        self.eventargs = []

    def onHover(self, position):
        if self.hovered == False:
            self.actor.image = self.himage

    def endHover(self):
        if self.hovered == True:
            self.actor.image = self.image

    def addEvent(self, event, *args):   # add an event to be called when pressed
        self.events.append(event)
        self.eventargs.append(args)

    def onPress(self, position):        # call all the events that the button has
        for i, event in enumerate(self.events):
            self.parent.callEvent(event, *self.eventargs[i])

    def draw(self):
        self.actor.draw()

class UIActor(UIElement):
    def __init__(self, actor):
        super().__init__()
        self.x = actor.left
        self.y = actor.top
        self.width = actor.width
        self.height = actor.height
        self.actor = actor
    def draw(self):
        self.actor.draw()

class Text(UIElement):
    def __init__(self, x, y, text, color):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.color = color
    def draw(self):
        self.parent.screen.draw.text(self.text, (self.x, self.y), color=self.color)