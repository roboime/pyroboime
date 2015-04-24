#
# Copyright (C) 2013 RoboIME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
from .. import Tactic
from ..skills.gotolooking import GotoLooking


class Waiter(Tactic):
    """Wait wherever you are, looking at the ball."""

    def __init__(self, robot):
        super(Waiter, self).__init__(robot, initial_state=GotoLooking(
            robot,
            name='Wait',
            target=robot,
            lookpoint=robot.world.ball
        ))

    @property
    def target(self):
        return self.robot
