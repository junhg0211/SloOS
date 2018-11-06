import root
import color
from rootobject import rootobject
from rootobject import lockscreen
from rootobject import shutdown

lock = 'state.lock'
home = 'state.home'

def change_state(next_state):
    root.state = next_state

    if root.state == lock:
        rootobject.remove_object_by_type(shutdown.Shutdown)

        rootobject.add_object(lockscreen.LockScreen(color.text, color.background))