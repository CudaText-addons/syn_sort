import os
from sw import *

fn_ini = os.path.join(app_ini_dir(), 'syn_sort.ini')    
section = 'op'


def get_offsets():
    if ed.get_sel_mode()==SEL_COLUMN:
        r = ed.get_sel_rect()
        return r[0], r[2]
    else:
        return -1, -1


def get_num_and_text(s):
    n = 0
    while n<len(s) and s[n].isdigit(): n += 1
    try:
        num = int(s[:n])
    except:
        num = 0
    text = s[n:]
    return (num, text)
        

def do_sort(is_reverse, 
            is_nocase, 
            del_dups=False, 
            del_blanks=True,
            is_numeric=False,
            offset1=-1, 
            offset2=-1):

    #option enables to sort all, if no selection            
    op_sort_all = ini_read(fn_ini, section, 'sort_all', '0')=='1'
            
    is_all = False
    nlines = ed.get_line_count()
    line1, line2 = ed.get_sel_lines()
    
    if line1==line2 or line1<0:
        if op_sort_all:
            is_all = True
        else:
            msg_status('Sort: needed multiline selection')
            return
      
    if is_all:
        lines = [ed.get_text_line(i) for i in range(nlines)]
    else:  
        #add last empty line
        if ed.get_text_line(nlines-1) != '':
            ed.set_text_line(-1, '')
        lines = [ed.get_text_line(i) for i in range(line1, line2+1)]
    
    if del_blanks:
        lines = [s for s in lines if s.strip()]
    if del_dups:
        lines = list(set(lines))

    def _key(item):
        s = item
        if is_nocase: 
            s = s.lower()

        if (offset1>=0) or (offset2>=0):
            #todo: s = ed.convert(CONVERT_LINE_TABS_TO_SPACES,..
            if offset2>=0: s = s[:offset2]
            if offset1>=0: s = s[offset1:]
                   
        #numeric after offsets
        if is_numeric:        
            num, text = get_num_and_text(s.lstrip())
            #print('parts "%s": %d %s' % (s, num, text))
            s = '%20.20d ' % num + text
            
        return s

        
    lines = sorted(lines, 
        key=_key, 
        reverse=is_reverse
        )

    if is_all:
        ed.set_text_all('\n'.join(lines)+'\n')
    else:
        pos1 = ed.xy_pos(0, line1)
        pos2 = ed.xy_pos(0, line2+1)
        ed.replace(pos1, pos2-pos1, '\n'.join(lines)+'\n')
        ed.set_sel(pos1, pos2-pos1)
        
    
    text = 'Sorted' \
        + (', all text' if is_all else '') \
        + (', reverse' if is_reverse else '') \
        + (', ignore case' if is_nocase else '') \
        + (', numeric' if is_numeric else '') \
        + (', offsets %d..%d' % (offset1, offset2) if (offset1>=0) or (offset2>=0) else '')
    msg_status(text)


def do_dialog():
    size_x = 330
    size_y = 240
    id_rev = 0
    id_nocase = 1
    id_del_dup = 2
    id_del_sp = 3
    id_numeric = 4
    id_offset1 = 7
    id_offset2 = 9
    id_ok = 10
    
    op_rev = ini_read(fn_ini, section, 'rev', '0')
    op_nocase = ini_read(fn_ini, section, 'nocase', '0')
    op_del_dup = ini_read(fn_ini, section, 'del_dup', '1')
    op_del_sp = ini_read(fn_ini, section, 'del_sp', '1')
    op_numeric = ini_read(fn_ini, section, 'numeric', '0')
    
    op_offset1, op_offset2 = get_offsets()
    
    c1 = chr(1)
    text = '\n'.join([
      c1.join(['type=check', 'pos=6,6,300,0', 'cap=&Sort descending (reverse)', 'val='+op_rev]),
      c1.join(['type=check', 'pos=6,30,300,0', 'cap=&Ignore case', 'val='+op_nocase]),
      c1.join(['type=check', 'pos=6,54,300,0', 'cap=Delete d&uplicate lines', 'val='+op_del_dup]),
      c1.join(['type=check', 'pos=6,78,300,0', 'cap=Delete &blank lines', 'val='+op_del_sp]),
      c1.join(['type=check', 'pos=6,102,300,0', 'cap=Numeric (treat beginning as number)', 'val='+op_numeric]),
      c1.join(['type=label', 'pos=6,130,300,0', 'cap=Sort only by substring, offsets 0-based:']),
      c1.join(['type=label', 'pos=30,152,130,0', 'cap=&From:']),
      c1.join(['type=spinedit', 'pos=30,170,110,0', 'props=-1,5000,1', 'val='+str(op_offset1)]),
      c1.join(['type=label', 'pos=120,152,230,0', 'cap=&To:']),
      c1.join(['type=spinedit', 'pos=120,170,200,0', 'props=-1,5000,1', 'val='+str(op_offset2)]),
      c1.join(['type=button', 'pos=60,210,160,0', 'cap=OK', 'props=1']),
      c1.join(['type=button', 'pos=164,210,264,0', 'cap=Cancel']),
      ])
    
    res = dlg_custom('Sort', size_x, size_y, text)
    if res is None: return
    btn, text = res
    if btn != id_ok: return
    text = text.splitlines()
    
    ini_write(fn_ini, section, 'rev', text[id_rev])
    ini_write(fn_ini, section, 'nocase', text[id_nocase])
    ini_write(fn_ini, section, 'del_dup', text[id_del_dup])
    ini_write(fn_ini, section, 'del_sp', text[id_del_sp])
    ini_write(fn_ini, section, 'numeric', text[id_numeric])
    
    is_rev = text[id_rev]=='1'
    is_nocase = text[id_nocase]=='1'
    is_del_dup = text[id_del_dup]=='1'
    is_del_sp = text[id_del_sp]=='1'
    is_numeric = text[id_numeric]=='1'
    offset1 = int(text[id_offset1])
    offset2 = int(text[id_offset2])
    
    if (offset1>=0) and (offset2>=0) and (offset1>=offset2):
        msg_box(MSG_ERROR, 'Incorrect offsets: %d..%d' % (offset1, offset2))
        return
    
    return (is_rev, is_nocase, is_del_dup, is_del_sp, is_numeric, offset1, offset2)
    

class Command:
    def sort_asc(self):
        do_sort(False, False)
    def sort_desc(self):
        do_sort(True, False)
        
    def sort_asc_nocase(self):
        do_sort(False, True)
    def sort_desc_nocase(self):
        do_sort(True, True)

    def sort_dlg(self):
        res = do_dialog()
        if res is None: return
        do_sort(*res)
        
    def config(self):
        if not os.path.isfile(fn_ini):
            with open(fn_ini, 'w') as f:
                f.write('[op]\n')
        file_open(fn_ini)
