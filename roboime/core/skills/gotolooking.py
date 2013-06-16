from .goto import Goto


class GotoLooking(Goto):
    def __init__(self, robot, lookpoint=None, **kwargs):
        """
        lookpoint: Where you want it to look, what were you expecting?
        """
        super(GotoLooking, self).__init__(robot, **kwargs)
        self.lookpoint = lookpoint

    def _step(self):
        self.angle = self.robot.angle_to_point(self.lookpoint)
        super(GotoLooking, self)._step()
