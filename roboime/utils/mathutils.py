import math

_trigonom_ = ['sin', 'cos', 'tan']
_invtrigonom_ = ['a' + f for f in _trigonom_] + ['atan2']
_restricted_ = ['trunc']

for fun in dir(math):
    if fun in _restricted_:
        pass
    elif fun in _trigonom_:
        exec '{0} = lambda x: math.{0}(math.radians(x))'.format(fun) in globals()
    elif fun in _invtrigonom_:
        exec '{0} = lambda x: math.degrees(math.{0}(x))'.format(fun) in globals()
    else:
        exec '{0} = math.{0}'.format(fun)