from pynput import keyboard

def on_activate_h():
    print('<ctrl>+<alt>+h pressed')
    return True

def on_activate_i():
    print('<ctrl>+<alt>+i pressed')
    return False

with keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+h': on_activate_h}) as h:
    h.join()