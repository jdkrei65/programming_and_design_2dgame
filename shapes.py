import pymunk
import copy
from typing import Any, ClassVar, Dict, List, Tuple, TypeVar

T = TypeVar("T", bound="PickleMixin")
_State = Dict[str, List[Tuple[str, Any]]]

steel_filter = pymunk.ShapeFilter(0, 0b0000001, 0b1000000)  # pymunk shapefilters
plank_filter = pymunk.ShapeFilter(0, 0b0000010, 0b1011101)  # these manage what shapes collide with what
beam_filter  = pymunk.ShapeFilter(0, 0b0000100, 0b1001011)
ball_filter  = pymunk.ShapeFilter(0, 0b0001000, 0b0011110)
prepl_filter = pymunk.ShapeFilter(0, 0b0010000, 0b1001010)
joint_filter = pymunk.ShapeFilter(0, 0b0100000, 0b0000000)
any_structure= pymunk.ShapeFilter(0, 0b1000000, 0b0010111)

#   Apparently copying subclassed stuff from pymunk breaks things.
#   So I had to copy and modify the __get/setattr__ functions from the pymunk code.
#   I'm not sure exactly how it works,
#   But it does work now now.

class SegmentBody(pymunk.Body):
    def __init__(self, friction=0.2):
        super().__init__(1, float("inf"))
        self.position = 0, 0
        self.elasticity = 0.0
        self.friction = friction

    def __getstate__(self) -> _State:
        """Return the state of this object

        This method allows the usage of the :mod:`copy` and :mod:`pickle`
        modules with this class.
        """

        d: _State = {
            "init": [],  # arguments for init
            "general": [],  # general attributes
            "custom": [],  # custom attributes set by user
            "special": [],  # attributes needing special handling
        }
        #for a in type(self)._pickle_attrs_init:
        #    d["init"].append((a, self.__getattribute__(a)))

        d["init"] = [
            ("friction", self.__getattribute__("friction"))
        ]

        for a in type(self)._pickle_attrs_general:
            d["general"].append((a, self.__getattribute__(a)))

        for k, v in self.__dict__.items():
            if k[0] != "_":
                d["custom"].append((k, v))

        d["special"].append(("is_sleeping", self.is_sleeping))
        d["special"].append(("_velocity_func", self._velocity_func_base))
        d["special"].append(("_position_func", self._position_func_base))
        return d

class GenericSegment(pymunk.Segment):
    def __init__(self, body, a, b, radius, sfilter):
        super().__init__(body, a, b, radius)
        self.mass = 1
        self.elasticity = 0.0
        self.filter = sfilter
        self.can_have_joints = True
        self.is_prepl = False

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

    def copy(self: T) -> T:
        return copy.deepcopy(self)

    def __getstate__(self) -> _State:
        """Return the state of this object

        This method allows the usage of the :mod:`copy` and :mod:`pickle`
        modules with this class.
        """

        d: _State = {
            "init": [],  # arguments for init
            "general": [],  # general attributes
            "custom": [],  # custom attributes set by user
            "special": [],  # attributes needing special handling
        }
        for a in type(self)._pickle_attrs_init:
            d["init"].append((a, self.__getattribute__(a)))

        d["init"].append(("sfilter", self.__getattribute__("filter")))

        for a in type(self)._pickle_attrs_general:
            d["general"].append((a, self.__getattribute__(a)))

        for k, v in self.__dict__.items():
            if k[0] != "_":
                d["custom"].append((k, v))

        return d

    def __setstate__(self, state: _State) -> None:
        """Unpack this object from a saved state.

        This method allows the usage of the :mod:`copy` and :mod:`pickle`
        modules with this class.
        """

        init_attrs: List[str] = []

        init_args = [v for k, v in state["init"]]
        self.__init__(*init_args)  # type: ignore

        for k, v in state["general"]:
            self.__setattr__(k, v)

        for k, v in state["custom"]:
            self.__setattr__(k, v)

class MovingJoint(pymunk.Body):
    def __init__(self, pos, bfilter, poo1=False, poo2=False):
        if poo1 or poo2:
            print(pos, bfilter, poo1, poo2)

        super().__init__(1, float("inf"))
        circle = pymunk.Circle
        circle.color = (99, 149, 155, 1)
        circle.filter = bfilter
        self.position = pos

        self.joint = pymunk.constraints.PinJoint(tracker_body, line.body, (0, 0), line.body.world_to_local(pos))
        self.joint.collide_bodies = False

    def __getstate__(self) -> _State:
        """Return the state of this object

        This method allows the usage of the :mod:`copy` and :mod:`pickle`
        modules with this class.
        """

        d: _State = {
            "init": [],  # arguments for init
            "general": [],  # general attributes
            "custom": [],  # custom attributes set by user
            "special": [],  # attributes needing special handling
        }
        #for a in type(self)._pickle_attrs_init:
        #    d["init"].append((a, self.__getattribute__(a)))

        d["init"] = [
            ("pos", self.__getattribute__("position")),
            ("bfilter", self.__getattribute__("filter"))
        ]

        for a in type(self)._pickle_attrs_general:
            d["general"].append((a, self.__getattribute__(a)))

        for k, v in self.__dict__.items():
            if k[0] != "_":
                d["custom"].append((k, v))

        d["special"].append(("is_sleeping", self.is_sleeping))
        d["special"].append(("_velocity_func", self._velocity_func_base))
        d["special"].append(("_position_func", self._position_func_base))
        return d

    def __setstate__(self, state: _State) -> None:
        """Unpack this object from a saved state.

        This method allows the usage of the :mod:`copy` and :mod:`pickle`
        modules with this class.
        """
        init_attrs: List[str] = []

        init_args = [v for k, v in state["init"]]
        self.__init__(*init_args)  # type: ignore

        for k, v in state["general"]:
            self.__setattr__(k, v)

        for k, v in state["custom"]:
            self.__setattr__(k, v)

        for k, v in state["special"]:
            if k == "is_sleeping" and v:
                pass
            elif k == "_velocity_func" and v != None:
                self.velocity_func = v
            elif k == "_position_func" and v != None:
                self.position_func = v

    def copy(self: T) -> T:
        """Create a deep copy of this object."""
        return copy.deepcopy(self)