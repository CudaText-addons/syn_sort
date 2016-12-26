import os
from sw import *

def get_ini_fn():
    return os.path.join(app_ini_dir(), 'syn_sort.ini')

def ed_set_text_all(lines):
    ed.set_caret_xy(0, 0)
    ed.set_text_all('\n'.join(lines)+'\n')
    
def ed_get_text_all():
    n = ed.get_line_count()
    if ed.get_text_line(n-1)=='': n-=1
    return [ed.get_text_line(i) for i in range(n)]    

def ed_insert_to_lines(lines, line1, line2):
    pos1 = ed.xy_pos(0, line1)
    pos2 = ed.xy_pos(0, line2+1)
    ed.replace(pos1, pos2-pos1, '\n'.join(lines)+'\n')
    ed.set_sel(pos1, pos2-pos1)

def ed_set_tab_title(s):
    pass

def ed_convert_tabs_to_spaces(s):
    return s
   
def msg_show_error(s):
    msg_box(MSG_ERROR, s)

def ed_get_sel_lines():
    n1, n2 = ed.get_sel_lines()
    if n1==n2: 
        n1, n2 = -1, -1
    return n1, n2
