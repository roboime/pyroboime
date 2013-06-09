from numpy import linspace, sign
from time import time
from ...utils.geom import Point
from ...utils.geom import Line

from .stop import Stop
from .. import Play
from ..tactics.goalkeeper import Goalkeeper
from ..tactics.blocker import Blocker
from ..tactics.defender import Defender
from ..tactics.zickler43 import Zickler43
from ..skills.gotolooking import GotoLooking
from ..skills.sampledchipkick import SampledChipKick
from ..skills.goto import Goto
from ...utils.statemachine import Machine as StateMachine, State, Transition

class Steppable(object):
    def step(self):
        pass

class IndirectKick(Stop, StateMachine):
    """
    Currently this play will extend StopReferee by performing an
    indirect kick by positioning a robot on a good spot and making
    a pass to it.
    """


    def __init__(self, team, goalkeeper_uid, **kwargs):
        Stop.__init__(self, team, goalkeeper_uid, **kwargs)
        
        self.states = {
            'starting' : State(True, name='Starting'),
            'touched' : State(True, name='Touched'),
            'go_position' : State(True, name='Go to position'),
            'pass' : State(True, name = 'Pass'),
            'end' : State(True, name = 'End')
        }
        
        transitions = [
            Transition(from_state=self.states['starting'], to_state=self.states['end'], condition=lambda : self.passer is None),
            Transition(from_state=self.states['starting'], to_state=self.states['go_position'], condition=lambda : self.passer is not None),
            # TODO: Parametrize this
            Transition(from_state=self.states['go_position'], to_state=self.states['pass'], condition=lambda : self.receiver.distance(self.best_position) < 0.2),
            Transition(from_state=self.states['pass'], to_state=self.states['touched'], condition=lambda : self.passer.is_last_toucher),
            Transition(from_state=self.states['touched'], to_state=self.states['end'], condition=lambda : not self.passer.is_last_toucher),
        ]
        StateMachine.__init__(self, deterministic=True, initial_state=self.states['starting'], transitions=transitions)

        self.goalkeeper_uid = goalkeeper_uid
        self.players = {}
        self.team = team
        self.receiver = None
        self.passer = None
        self.tactics_factory.update({
            'receiver': lambda robot: GotoLooking(robot, lookpoint=self.world.ball),
            'passer': lambda robot: SampledChipKick(robot, receiver=self.receiver, lookpoint=self.receiver),
            'zickler' : lambda robot: Zickler43(robot),
        })
        self.best_position = None

    def restart(self):
        self.current_state = self.states['starting']
        self.receiver = None
        self.passer = None

    @property
    def goalkeeper(self):
        l = [r for r  in self.team if r.uid == self.goalkeeper_uid]
        if l:
            return l[0]
        return None

    def setup_tactics(self):
        Stop.setup_tactics(self)
        print self.current_state
        if self.current_state == self.states['starting']:
            self.best_position = self.team.best_indirect_positions()[0][0]
            robots_closest_to_ball = self.team.closest_robots_to_ball()
            # TODO: Think of a better name
            robots_closest_to_bathtub = self.team.closest_robots_to_point(point=self.best_position)
            
            for robot in self.team:
                if robot.uid == self.goalkeeper_uid:
                    robots_closest_to_ball.remove(robot)                    
                    robots_closest_to_bathtub.remove(robot)
                    break
            
            self.receiver = self.passer = None
            if robots_closest_to_bathtub:
                self.receiver = robots_closest_to_bathtub[0]
            
            for robot in robots_closest_to_ball[:]:
                if robot == self.receiver:
                    robots_closest_to_ball.remove(robot)
                    break
            
            if robots_closest_to_ball:
                self.passer = robots_closest_to_ball[0]
                        
            #for robot in self.team:
            #    robot.current_tactic = Steppable() 

        elif self.current_state == self.states['go_position']:
            self.players[self.receiver.uid]['receiver'].target = self.best_position
            self.receiver.current_tactic = self.players[self.receiver.uid]['receiver']

            #for robot in self.team:
            #    if robot != self.receiver:
            #        robot.current_tactic = Steppable() 
    
        elif self.current_state == self.states['pass']:
            self.best_position = self.team.best_indirect_positions()[0][0]

            self.players[self.passer.uid]['passer'].receiver = self.receiver
            self.players[self.passer.uid]['passer'].lookpoint = self.receiver
            self.passer.current_tactic = self.players[self.passer.uid]['passer']

            self.players[self.receiver.uid]['receiver'].target = self.best_position
            self.receiver.current_tactic = self.players[self.receiver.uid]['receiver']
            #for robot in self.team:
            #    if robot != self.passer and robot != self.receiver:
            #        robot.current_tactic = Steppable() 
        
        elif self.current_state == self.states['touched']: 
            robots_closest_to_ball = self.team.closest_robots_to_ball()
            robots_closest_to_ball.remove(self.goalkeeper)
            robots_closest_to_ball.remove(self.passer)

            attacker = robots_closest_to_ball[0]
            attacker.current_tactic = self.players[attacker.uid]['zickler']

            self.players[self.receiver.uid]['receiver'].target = self.best_position
            self.receiver.current_tactic = self.players[self.receiver.uid]['receiver']
            
            #for robot in self.team:
            #    if robot != attacker and robot != self.receiver:
            #        robot.current_tactic = Steppable() 
        #else:
        #    for robot in self.team:
        #        robot.current_tactic = Steppable() 

        # Executes state machine transitions
        self.execute()
