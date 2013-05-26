from numpy.random import random

from .driveto import DriveTo


class DriveToObject(DriveTo):
    def __init__(self, robot, point, lookpoint, **kwargs):
        """
        Robot is positioned oposed to the lookpoint.
        lookPoint, object and robot stay aligned (and on this exact order)
        e.g.:     point: ball
              lookpoint: goal
                  robot: robot

        In adition to those, checkout DriveTo parameters as they are also
        valid for this skill, EXCEPT for b_point, which is mapped to point.
        """
        super(DriveToObject, self).__init__(robot, threshold=robot.front_cut, b_point=point, **kwargs)
        self.lookpoint = lookpoint

    def step(self):
        # the angle from the object to the lookpoint, thanks to shapely is this
        # that's the angle we want to be at
        self.angle = self.b_point.angle(self.lookpoint)

        # nondeterministically we should add a random spice to our
        # target angle, of course, within the limits of max_ang_var
        if not self.deterministic:
            self.angle += self.max_ang_var * (0.5 - random())

        # ultimately we should update our base angle to the oposite
        # of our target angle and let drive to object to its thing
        self.b_angle = self.angle + 180
        super(DriveToObject, self).step()