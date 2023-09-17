
from PySide6.QtWidgets import QWidget

def change_stylesheet(widget: QWidget, stylesheet: str):
    old_ss = widget.styleSheet()
    old_ss = {(pair:=ss.split(':'))[0].strip(' '):pair[1].strip(' ') for ss in old_ss.strip(' ').split(';') if len(ss)>0}
    new_ss = stylesheet
    new_ss = {(pair:=ss.split(':'))[0].strip(' '):pair[1].strip(' ') for ss in new_ss.strip(' ').split(';') if len(ss)>0}
    old_ss.update(new_ss)
    new_ss = ''.join([f"{key}: {val}; " for key, val in old_ss.items()])
    widget.setStyleSheet(new_ss)

