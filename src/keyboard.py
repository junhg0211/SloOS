import slo

lalt = False
ralt = False
lctrl = False
rctrl = False
space = False
escape = False

keydown_unicode = ''
keydown_key = None

input_board = '`1234567890-=~!@#$%^&*()_+qwertyuiop[]\QWERTYUIOP{}|asdfghjkl;\'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?\n '

drill_delay = slo.bucker['input']['key_drill_delay']
drill_remain_delay = slo.bucker['input']['key_drill_delay']
drill_loop_delay = slo.bucker['input']['key_drill_loop_delay']
drill_loop_remain_delay = slo.bucker['input']['key_drill_loop_delay']
drill_mode = 0
drill_input = False