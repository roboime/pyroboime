#
# Copyright (C) 2013-2015 RoboIME
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
from numpy import pi, sign, array, sin
from numpy.linalg import norm

from ...utils.mathutils import sqrt
from ...utils.pidcontroller import PidController
from .. import Skill


KICKPOWER = 5.0
#KICKPOWER = 1.0 # check this value...


def kick_power(distance, initial_speed=0.0, final_speed=0.0):
    mi = 0.4
    g = 9.81
    a = mi * g
    return abs(initial_speed * final_speed + 2 * a * distance) / sqrt(KICKPOWER)


class KickTo(Skill):
    """
    This class is an alternative to SampledKick.
    Meanwhile it's experimental, depending on the results it'll stay or not.
    """
    #TODO: Change parameter back once we have real control.
    #angle_kick_min_error = 0.5
    #distance_kick_min_error = 0.8
    angle_kick_min_error = 10
    angle_approach_min_error = 5
    angle_tolerance = 5
    orientation_tolerance = 0.7
    distance_tolerance = 0.14
    walkspeed = 0.2

    def __init__(self, robot, lookpoint=None, force_kick=False, minpower=0.0, maxpower=1.0, **kwargs):
        """
        """
        super(KickTo, self).__init__(robot, deterministic=True, **kwargs)
        self._lookpoint = lookpoint
        self.force_kick = force_kick
        self.minpower = minpower
        self.maxpower = maxpower
        self.angle_controller = PidController(kp=0.1, ki=0.5, kd=0.05, integ_max=300., output_max=0.8)
        self.distance_controller = PidController(kp=0.1, ki=0.5, kd=0.05, integ_max=300., output_max=0.8)

    @property
    def final_target(self):
        return self.lookpoint

    @property
    def lookpoint(self):
        if callable(self._lookpoint):
            return self._lookpoint() or self.robot.enemy_goal
        else:
            return self._lookpoint or self.robot.enemy_goal

    @lookpoint.setter
    def lookpoint(self, value):
        self._lookpoint = value

    @lookpoint.setter
    def lookpoint(self, value):
        self._lookpoint = value

    def bad_position(self):
        bad_distance = self.robot.kicker.distance(self.ball) > self.distance_tolerance + .01
        #bad_orientation = abs(self.delta_orientation()) >= self.orientation_tolerance + 3
        bad_angle = abs(self.delta_angle()) >= self.angle_tolerance + 5
        return bad_distance or bad_angle

    def good_position(self):
        good_distance = self.robot.kicker.distance(self.ball) <= self.distance_tolerance
        #good_orientation = abs(self.delta_orientation()) < self.orientation_tolerance
        good_angle = abs(self.delta_angle()) < self.angle_tolerance
        return good_distance and good_angle

    def delta_angle(self):
        delta = self.robot.angle_to_point(self.ball) - self.ball.angle_to_point(self.lookpoint)
        return (180 + delta) % 360 - 180

    def delta_orientation(self):
        delta = self.robot.angle - self.ball.angle_to_point(self.lookpoint)
        return (180 + delta) % 360 - 180

    def _step(self):
        #print 'blasdbflas'
        delta_orientation = self.delta_orientation()

        self.angle_controller.input = delta_orientation
        self.angle_controller.feedback = 0.0
        self.angle_controller.step()

        #d = self.robot.front_cut + self.ball.radius
        d = norm(array(self.robot) - array(self.ball))
        r = self.robot.radius

        w = self.angle_controller.output
        max_w = 180.0 * self.robot.max_speed / r / pi
        if abs(w) > max_w:
            w = sign(w) * max_w
        v = pi * w * d / 180.0
        z = 0.0

        if abs(delta_orientation) < self.angle_kick_min_error or self.force_kick:
        #if abs(sin(delta_orientation) * self.ball.distance(self.lookpoint)) < self.distance_kick_min_error:
            kp = kick_power(self.lookpoint.distance(self.robot))
            kp = min(max(kp, self.minpower), self.maxpower)
            self.robot.action.kick = kp
            self.distance_controller.input = self.robot.kicker.distance(self.ball)
            self.distance_controller.feedback = 0
            self.distance_controller.step()
            z = self.distance_controller.output
            #z = self.walkspeed
        else:
            if abs(delta_orientation) < self.angle_approach_min_error:
                self.distance_controller.input = self.robot.kicker.distance(self.ball)
                self.distance_controller.feedback = 0
                self.distance_controller.step()
                z = self.distance_controller.output
            self.robot.action.dribble = 1.0

        self.robot.action.speeds = (z, v, -w)
