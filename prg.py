from time import sleep
import curses.panel
import curses.textpad
import curses
import json

FILE_PATH = '/home/nt/file.json'


def format_task_str(s, len_max):
    return s.ljust(len_max)

def draw_layout(main_win, task_time_pairs_n, time_lt, task_col_w, time_col_w,
                y=0, x=0):
    for y in range(task_time_pairs_n+1):
        line_pos = y*2
        main_win.addstr(line_pos, x, f'{"-"*(task_col_w+1)} '
                        f'{"-"*(time_col_w+1)}')
        if y < task_time_pairs_n:
            main_win.addstr(line_pos+1, task_col_w+1, '|')

def draw_left_layout(main_win, task_time_pairs, task_col_w, y=0, x=0):
    for y in range(task_time_pairs+1): # +1 for last line.
        line_pos = y*2
        main_win.addstr(line_pos, x, f'{"-"*(task_col_w+1)} ')

def draw_right_layout(main_win, task_time_pairs, time_col_w, x, time_lt):
    for y in range(task_time_pairs+1): # +1 for last line.
        line_pos = y*2
        main_win.addstr(line_pos, x, f'{"-"*(time_col_w+1)}')
        if y < task_time_pairs:
            main_win.addstr(line_pos+1, x-1, '|')

def insert_txt_task_time_pads(task_lt, time_lt, task_pad_lt, time_pad_lt,
                              task_col_w, time_col_w):
    for i in range(len(task_lt)):
        task_str = format_task_str(task_lt[i], task_col_w)
        time_str = time_lt[i]
        
        task_pad = task_pad_lt[i]
        time_pad = time_pad_lt[i]

        task_pad.erase(); time_pad.erase()
        
        if len(task_str) > task_pad.getmaxyx()[1]:
            task_pad.resize(1, len(task_str))
        if len(time_str) > time_pad.getmaxyx()[1]:
            time_pad.resize(1, len(time_str))
        
        task_pad.insstr(task_str)
        time_pad.insstr(time_str)

        task_pad.noutrefresh(0, 0, i*2+1, 0, i*2+1, task_col_w)
        time_pad.noutrefresh(0, 0, i*2+1, task_col_w+3, i*2+1, task_col_w+3+time_col_w)

def init_task_time_pads(main_win, task_lt, time_lt, task_col_w, time_col_w):
    # +1 pattern for strs on windows/wins/pads.
    task_pad_lt = []; time_pad_lt = []
    y = 1
    for i in range(len(task_lt)):
        task_str = format_task_str(task_lt[i], task_col_w)
        time_str = time_lt[i]

        task_pad = curses.newpad(1, len(task_str)) #y, 0)
        time_pad = curses.newpad(1, len(time_str)) #y, len(task_str)+3)

        task_pad_lt.append(task_pad); time_pad_lt.append(time_pad)
        y += 2
    return task_pad_lt, time_pad_lt

def highlight_pad(win, selected=False):
    win.bkgd(' ', curses.color_pair(2) if selected else curses.color_pair(1))

def pad_content(task_lt, time_lt, row, col, time_col_w):
    if col == 0:
        return task_lt[row]
    return time_lt[row]

def is_key_valid(key):
    valid_keys_normal = 'kjhl'
    valid_keys_special = [curses.KEY_UP, curses.KEY_DOWN,
                          curses.KEY_LEFT, curses.KEY_RIGHT, 10]
    if chr(key) in valid_keys_normal or key in valid_keys_special:
        return True
    return False

def extend_task_pad_width(task_pad, time_pad, task_pad_width, time_pad_width):
    time_pad_beg_y, time_pad_beg_x = time_pad.getbegyx()
    time_pad_beg_x += abs(time_pad_beg_x-time_pad_width)
    time_pad.refresh(0, 0, time_pad_beg_y, time_pad_beg_x, time_pad_beg_y,
                     time_pad_beg_x+time_pad_width)

def task_usr_inp(main_win, pad, task_pad_lt, time_pad_lt, task_lt, time_lt,
                 task_col_w, time_col_w, row, col):
    inp = key = ''
    y, x = pad.getbegyx()
    pad_width = task_col_w
    main_win.move(row*2+1, 0)
    # cursor in off location, that's the reason for the random chars. write in notebook the pattern?.
    while key != 10:
        if key == curses.KEY_BACKSPACE:
            if x == 0:
                key = main_win.getch()
                continue
            x -= 1
            main_win.delch(y, x)
            main_win.clrtoeol()
            main_win.refresh()
            inp = inp[:len(inp)]
            if x >= pad_width:
                main_win.addstr(y, x+1, '|')
                main_win.refresh()
                refresh_pad(time_pad_lt[y//2], (y, x+3), time_col_w)
                main_win.move(y, x)
            else:
                main_win.addstr(y, task_col_w+1, '|')
                main_win.refresh()
                refresh_pad(time_pad_lt[y//2], (y, task_col_w+3), time_col_w)
                main_win.move(y, x)
        elif key:
            if x > pad_width-1:
                main_win.delch(y, x)
                main_win.addstr(y, x+2, '|')
                main_win.refresh()
                refresh_pad(time_pad_lt[y//2], (y, x+4), time_col_w)
            main_win.addstr(y, x, chr(key))
            inp += chr(key)
            x += 1
        key = main_win.getch()
    return inp
        
def modify_task_name(main_win, pad, task_pad_lt, time_pad_lt, task_lt, time_lt,
                     task_col_w, time_col_w, row, col):
    curses.curs_set(True)
    curses.echo()
    pad.erase()
    highlight_pad(pad, selected=True)
    refresh_pad(pad, pad.getbegyx(), len(task_lt[row]))
    inp = task_usr_inp(main_win, pad, task_pad_lt, time_pad_lt, task_lt,
                       time_lt, task_col_w, time_col_w, row, col)
    curses.noecho()
    curses.curs_set(False)
    if not inp or inp.isspace():
        return task_lt
    task_lt[row] = inp; return task_lt

def change_time(time_pad, time_lt, time_col_w, start_time, end_time, selected, hour_min, y):
    key = None
    if selected == 1:
        hour, minute = start_time.split(':')
    else:
        hour, minute = end_time.split(':')

    while (key != 10 if key else True):
        key = time_pad.getch()
        if chr(key) == 'k' or key == curses.KEY_UP:
            if hour_min == 1:
                if int(hour) == 23:
                    hour = '00'
                else:
                    hour = str(int(hour)+1)
                    hour = '0'+hour if int(hour) < 10 else hour
            else:
                if minute == '59':
                    minute = '00'
                    hour += str(int(hour)+1) if int(hour) != '23' else '00'
                else:
                    minute = str(int(minute)+1)
                    minute = '0'+minute if int(minute) < 10 else minute
        elif chr(key) == 'j' or key == curses.KEY_DOWN:
            if hour_min == 1:
                if int(hour) == 0:
                    hour = '23'
                else:
                    hour = str(int(hour)-1)
                    hour = '0'+hour if int(hour) < 10 else hour
            else:
                if int(minute) == 0:
                    minute = '59'
                    hour += str(int(hour)-1) if hour != '00' else '23'
                else:
                    minute = str(int(minute)+1)
                    minute = '0'+minute if int(minute) < 10 else minute
        
        if selected == 1:
            highlight_time_pad(time_pad, time_lt, time_col_w, hour+':'+minute,
                               end_time, selected, hour_min)
        elif selected == 2:
            highlight_time_pad(time_pad, time_lt, time_col_w, start_time,
                               hour+':'+minute, selected, hour_min)
    if selected == 1:
        time_lt[y] = f'{hour}:{minute}-'+time_lt[y].split('-')[1]

    else:
        time_lt[y] = time_lt[y].split('-')[0]+f'-{hour}:{minute}'

    return time_lt

def highlight_time_pad(time_pad, time_lt, time_col_w, start_time, end_time,
                       selected, hour_min):
    time_pad.erase()
    hour, minute = start_time.split(':') if selected == 1 else end_time.split(':')
    if selected == 1: # start time.
        if hour_min == 1: # hour.
            time_pad.insstr(end_time, curses.color_pair(2))
            time_pad.insstr('-', curses.color_pair(2))
            time_pad.insstr(f':{minute}', curses.color_pair(2))
            time_pad.insstr(hour, curses.color_pair(1))
        else: # minuteute.
            time_pad.insstr(end_time, curses.color_pair(2))
            time_pad.insstr('-', curses.color_pair(2))
            time_pad.insstr(minute, curses.color_pair(1))
            time_pad.insstr(':', curses.color_pair(2))
            time_pad.insstr(hour, curses.color_pair(2))
    else: # end time.
        if hour_min == 1: # hour.
            time_pad.insstr(f':{minute}', curses.color_pair(2))
            time_pad.insstr(hour, curses.color_pair(1))
            time_pad.insstr('-', curses.color_pair(2))
            time_pad.insstr(start_time, curses.color_pair(2))
        else: # minute.
            time_pad.insstr(minute, curses.color_pair(1))
            time_pad.insstr(':', curses.color_pair(2))
            time_pad.insstr(hour, curses.color_pair(2))
            time_pad.insstr('-', curses.color_pair(2))
            time_pad.insstr(start_time, curses.color_pair(2))

    refresh_pad(time_pad, time_pad.getbegyx(), len(start_time)+len(end_time))


def modify_time(main_win, time_lt, time_pad, time_col_w,  y):
    start_end = time_lt[y]
    start_time, end_time = start_end.split('-')

    highlight_time_pad(time_pad, time_lt, time_col_w, start_time, end_time, 1, 1)
    key = None
    col = 1
    time_pad.keypad(True)
    while key != 10:
        key = time_pad.getch()
        if chr(key) == 'h' or key == curses.KEY_LEFT:
            col -= 1 if col > 1 else -3
        elif chr(key) == 'l' or key == curses.KEY_RIGHT:
            col += 1 if col < 4 else -3

        highlight_time_pad(time_pad, time_lt, time_col_w,
                           start_time, end_time,
                           1 if col < 3 else 2, 1 if col % 2 else 2)
    
    if col < 3:
        hour, minute = start_time.split(':')
    else:
        hour, minute = end_time.split(':')

    return change_time(time_pad, time_lt, time_col_w, start_time, end_time, 1 if col < 3 else 2,
                       1 if col % 2 else 2, y)

def get_selected_pad(task_pad_lt, time_pad_lt, row, col):
    return task_pad_lt[row] if col == 0 else time_pad_lt[row]

def refresh_pad(pad, yx, width):
    y, x = yx
    pad.refresh(0, 0, y, x, y, x+width)
     
def update_scr(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
               task_col_w, time_col_w):
    main_win.erase()
    draw_layout(main_win, len(task_lt), time_lt, task_col_w, time_col_w)
    main_win.refresh()
    insert_txt_task_time_pads(task_lt, time_lt, task_pad_lt, time_pad_lt,
                              task_col_w, time_col_w)
    curses.doupdate()
#    draw_left_layout(main_win, len(task_lt), task_col_w)
#    draw_right_layout(main_win, len(task_lt), time_col_w, task_col_w+2, time_lt)

def update_task_time_file(task_lt, time_lt, task_time_dt):
    old_task_lt = list(task_time_dt); old_time_lt = list(task_time_dt.values())
    for i in range(len(task_lt)):
        task_time_dt[task_lt[i]] = time_lt[i]
    return task_time_dt

def main(main_win):
    curses.curs_set(False)

    file = open(FILE_PATH)

    task_time_dt = json.loads(file.read())

    task_lt = list(task_time_dt)
    time_lt = list(task_time_dt.values())

    task_col_w = len(max(task_lt, key=len))
    time_col_w = len(max(time_lt, key=len))

    task_pad_lt, time_pad_lt = init_task_time_pads(main_win, task_lt, time_lt,
                                                   task_col_w, time_col_w)

    update_scr(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
               task_col_w, time_col_w)

    task_pad_lt[0].keypad(True)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    row = col = -1
    while True:
        key = task_pad_lt[0].getch()
        if (key == curses.KEY_UP or chr(key) == 'k') and row >= 0:
            row = len(task_lt)-1 if row == 0 else row-1
        elif (key == curses.KEY_DOWN or chr(key) == 'j') and row >= 0:
            row = 0 if row == len(task_lt)-1 else row+1
        elif (key  == curses.KEY_LEFT or chr(key) == 'h') and row >= 0:
            col = 1 if col == 0 else 0
        elif (key == curses.KEY_RIGHT or chr(key) == 'l') and row >= 0:
            col = 0 if col == 1 else 1
        elif (key == 10) and row >= 0: # enter.
            selected_pad = get_selected_pad(task_pad_lt, time_pad_lt, row, col)
            if col == 0:
                task_lt = modify_task_name(main_win, selected_pad,
                                           task_pad_lt, time_pad_lt,
                                           task_lt, time_lt,
                                           task_col_w, time_col_w,
                                           row, col)

                task_col_w = len(max(task_lt, key=len))
                time_col_w = len(max(time_lt, key=len))

                update_scr(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
                           task_col_w, time_col_w)
            else:
                time_lt = modify_time(main_win, time_lt, selected_pad, time_col_w, row)
                highlight_pad(selected_pad, True)

        elif chr(key) == 'q':
            break
        else:
            if row == -1 and is_key_valid(key):
                row, col = 0, 0
                selected_pad = get_selected_pad(task_pad_lt, time_pad_lt, row,
                                                col)
                selected_pad_content = pad_content(task_lt, time_lt, row, col,
                                                   time_col_w)

                highlight_pad(selected_pad)
                
                refresh_pad(selected_pad, selected_pad.getbegyx(),
                            len(selected_pad_content))
                prev_selected_pad = selected_pad
                prev_selected_pad_content = selected_pad_content
            continue

        selected_pad_content = pad_content(task_lt, time_lt, row, col,
                                           time_col_w)
        selected_pad = get_selected_pad(task_pad_lt, time_pad_lt, row, col)
        
        if selected_pad == prev_selected_pad:
            highlight_pad(selected_pad)
            refresh_pad(selected_pad, selected_pad.getbegyx(),
                        len(selected_pad_content))
            prev_selected_pad = selected_pad
            prev_selected_pad_content = selected_pad_content
            continue

        highlight_pad(prev_selected_pad, True)
        highlight_pad(selected_pad)
        
        refresh_pad(prev_selected_pad, prev_selected_pad.getbegyx(),
                    len(prev_selected_pad_content))
        refresh_pad(selected_pad, selected_pad.getbegyx(),
                    len(selected_pad_content))

        prev_selected_pad = selected_pad
        prev_selected_pad_content = selected_pad_content

    update_task_time_file(task_lt, time_lt, task_time_dt)
    
curses.wrapper(main)
