from time import sleep
import curses.panel
import curses.textpad
import curses
import json


#   def draw_left_layout(main_win, task_time_pairs, task_col_w, y=0, x=0):
#       for y in range(task_time_pairs+1): # +1 for last line.
#           line_pos = y*2
#           main_win.addstr(line_pos, x, f'{"-"*(task_col_w+1)} ')

#   def draw_right_layout(main_win, task_time_pairs, time_col_w, x, time_lt):
#       for y in range(task_time_pairs+1): # +1 for last line.
#           line_pos = y*2
#           main_win.addstr(line_pos, x, f'{"-"*(time_col_w+1)}')
#           if y < task_time_pairs:
#               main_win.addstr(line_pos+1, x-1, '|')

"""
Global Parameters
-----------------
* main_win
    stdscr

* task_lt
    List of task names.

* time_lt
    List of time ranges.

* task_pad_lt

* time_pad_lt

* task_col_w
    Width of the task column.

* time_col_w
    Width of the time column.
"""

def draw_layout(main_win, task_time_pairs_n, time_lt, task_col_w, time_col_w,
                init_y=0, init_x=0):
    """
    Draws a task-time table; without the actual values of each cell, just the
    frame.

    Parameters
    ----------
    * task_time_pairs_n
        Number of task-time pairs.

    * init_y
        Initial y position in main_win.

    * init_x
        Initial x position in main_win.
    """
    # Each line's y position is going to be a multiple of 2, starting from 0.
    # Therefore, task_time_pairs_n*2 and a step of 2.
    for y in range(init_y, task_time_pairs_n*2+1, 2): # +1 cuz last line.
        main_win.addstr(y, init_x, f'{"-"*(task_col_w+1)} '
                        f'{"-"*(time_col_w+1)}')
        if y < task_time_pairs_n*2: # only draw '|' while y isn't last line
            main_win.addstr(y+1, task_col_w+1, '|')

def init_task_time_pads(main_win, task_lt, time_lt, task_col_w, time_col_w):
    """
    Create (initialize) task-time pads.

    Return
    -------
    * task_pad_lt
        List of newly created task pads.

    * time_pad_lt
        List of newly created time pads.
    """
    # +1 pattern for strs on windows/wins/pads.
    task_pad_lt = []; time_pad_lt = []
    for i in range(len(task_lt)):
        task_str = task_lt[i].ljust(task_col_w)
        time_str = time_lt[i]

        task_pad = curses.newpad(1, len(task_str))
        time_pad = curses.newpad(1, len(time_str))

        task_pad_lt.append(task_pad); time_pad_lt.append(time_pad)
    return task_pad_lt, time_pad_lt

def insert_val_task_time_pads(task_lt, time_lt, task_pad_lt, time_pad_lt,
                              task_col_w, time_col_w):
    """Inserts corresponding values in task-time pads."""
    for i in range(len(task_lt)):
        task_str = task_lt[i].ljust(task_col_w)
        time_str = time_lt[i]
        
        task_pad = task_pad_lt[i]
        time_pad = time_pad_lt[i]

        task_pad.erase(); time_pad.erase()
        
        if len(task_str) > task_pad.getmaxyx()[1]:
            task_pad.resize(1, len(task_str))
        if len(time_str) > time_pad.getmaxyx()[1]:
            time_pad.resize(1, len(time_str))
        
        # insstr doesn't move cursor in character insertion vs. addstr, so pad
        # of same length as value.
        task_pad.insstr(task_str)
        time_pad.insstr(time_str)
            
        # i*2+1 is one more after layout line.
        task_pad.noutrefresh(0, 0, i*2+1, 0, i*2+1, task_col_w)
        time_pad.noutrefresh(0, 0, i*2+1, task_col_w+3, i*2+1,
                             task_col_w+3+time_col_w)

def draw_tam_table(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
               task_col_w, time_col_w):
    main_win.erase()
    draw_layout(main_win, len(task_lt), time_lt, task_col_w, time_col_w)
    main_win.refresh()
    insert_val_task_time_pads(task_lt, time_lt, task_pad_lt, time_pad_lt,
                              task_col_w, time_col_w)
    curses.doupdate()

def get_selected_pad(task_pad_lt, time_pad_lt, row, col):
    return task_pad_lt[row] if col == 0 else time_pad_lt[row]

def refresh_pad(pad, yx, width):
    y, x = yx
    pad.refresh(0, 0, y, x, y, x+width)
     

def highlight_pad(pad, selected=False):
    """
    Highlights or de-highlights pad according to selected, by default highlight;
    if selected is true, change color to white on black (de-highlight),
    otherwise black on white.

    Parameters
    ----------
    * pad
    
    * selected
    """
    pad.bkgd(' ', curses.color_pair(2) if selected else curses.color_pair(1))

def pad_content(task_lt, time_lt, time_col_w, row, col):
    """
    Fetches and Return pad's content. From task_lt if col is 0, and time_lt
    if otherly.

    Parameters
    ----------
    * row   
        Pad's row (y).

    * col
        Pad's col (x).

    Return
    -------
    * task_lt[row] OR time_lt[row]
        Task name of task_lt at row.
        Time range of time_lt at row.
    """
    if col == 0:
        return task_lt[row]
    return time_lt[row]

def is_key_valid(key):
    """
    Return True if key is valid.

    Parameters
    ----------
    * key.

    Return
    -------
    * Boolean value (True/False).
    """
    valid_keys_normal = 'kjhl'
    valid_keys_special = [curses.KEY_UP, curses.KEY_DOWN,
                          curses.KEY_LEFT, curses.KEY_RIGHT, 10]
    if chr(key) in valid_keys_normal or key in valid_keys_special:
        return True
    return False

def update_task_time_file(task_lt, time_lt, task_time_dt):
    old_task_lt = list(task_time_dt); old_time_lt = list(task_time_dt.values())
    for i in range(len(task_lt)):
        task_time_dt[task_lt[i]] = time_lt[i]
    return task_time_dt


def task_usr_inp(main_win, pad, task_pad_lt, time_pad_lt, task_lt, time_lt,
                 task_col_w, time_col_w, row, col):
    """
    Reads and writes user input in the selected task pad.

    Parameters
    ----------
    * row
        Pad's row (y)

    * col
        Pad's col (x)

    Return
    -------
    * inp
    """
    inp = key = ''
    y, x = pad.getbegyx()
    main_win.move(row*2+1, 0) # move cursor position to selected task pad.
    # cursor in off location, that's the reason for the random chars. write in notebook the pattern?.
    while key != 10:
        if key == curses.KEY_BACKSPACE:
            if x == 0: #  no more chars to delete.
                key = main_win.getch()
                continue
            x -= 1
            main_win.delch(y, x)
            main_win.clrtoeol()
            main_win.refresh()
            inp = inp[:len(inp)-1]
            # x exceeds or equals current task column width. draw '|' after
            # cursor and draw time pad two spaces after it.
            if x >= task_col_w:
                main_win.addstr(y, x+1, '|')
                refresh_pad(time_pad_lt[y//2], (y, x+3), time_col_w)
            # x < current task column width. draw '|' two spaces after task
            # name and draw time pad four spaces after it.
            else:
                main_win.addstr(y, task_col_w+1, '|')
                refresh_pad(time_pad_lt[y//2], (y, task_col_w+3), time_col_w)
            # addstr moves cursor to after added char, '|', so fix position.
            main_win.move(y, x) 
        elif key:
            if x > task_col_w-1:
                main_win.delch(y, x) # delete '|'.
                main_win.addstr(y, x+2, '|') # re-draw it farther.
                main_win.refresh()
                # re-draw pad so it is 1 space after '|'.
                refresh_pad(time_pad_lt[y//2], (y, x+4), time_col_w)
            main_win.addstr(y, x, chr(key)) # add char to pad.
            inp += chr(key) # add char to inp str.
            x += 1 # increment cursor position.
        key = main_win.getch()
    return inp
        
def modify_task_name(main_win, pad, task_pad_lt, time_pad_lt, task_lt, time_lt,
                     task_col_w, time_col_w, row, col):
    """
    User input in task pad and replace task name with such input.

    Parameters
    ----------
    * row
        Pad's row (y).

    * col
        Pad's col (x)

    Return
    ------
    * task_lt
        Modifed list of task names.
    """
    curses.curs_set(True)
    curses.echo()
    pad.erase()
    highlight_pad(pad, selected=True)
    refresh_pad(pad, pad.getbegyx(), len(task_lt[row]))
    inp = task_usr_inp(main_win, pad, task_pad_lt, time_pad_lt, task_lt,
                       time_lt, task_col_w, time_col_w, row, col)
    curses.noecho()
    curses.curs_set(False)
 
    if not inp or inp.isspace(): # nothing in inp or inp only spaces.
        return task_lt

    task_lt[row] = inp; return task_lt # replace current task name with inp.

def highlight_timestamp(time_pad, time_lt, time_col_w, start_time, end_time,
                       selected_time, hour_min):
    time_pad.erase()

    if selected_time == 1:
        hour, minute = start_time.split(':')
    else:
        hour, minute = end_time.split(':')

    if selected_time == 1:
        time_pad.insstr(end_time, curses.color_pair(2))
        time_pad.insstr('-', curses.color_pair(2))
        if hour_min == 1:
            time_pad.insstr(f':{minute}', curses.color_pair(2))
            time_pad.insstr(hour, curses.color_pair(1))
        else:
            time_pad.insstr(minute, curses.color_pair(1))
            time_pad.insstr(':', curses.color_pair(2))
            time_pad.insstr(hour, curses.color_pair(2))
    else: 
        if hour_min == 1:
            time_pad.insstr(f':{minute}', curses.color_pair(2))
            time_pad.insstr(hour, curses.color_pair(1))
            time_pad.insstr('-', curses.color_pair(2))
            time_pad.insstr(start_time, curses.color_pair(2))
        else:
            time_pad.insstr(minute, curses.color_pair(1))
            time_pad.insstr(':', curses.color_pair(2))
            time_pad.insstr(hour, curses.color_pair(2))
            time_pad.insstr('-', curses.color_pair(2))
            time_pad.insstr(start_time, curses.color_pair(2))

    refresh_pad(time_pad, time_pad.getbegyx(), len(start_time)+len(end_time))

def int_to_time(n, hour_min):
    return n % (24 if hour_min == 1 else 60)

def time_pad_inp(time_pad, time_lt, time_col_w, row, start_time, end_time,
                 selected_time, hour_min):
    """
    Perform user input operations in timestamps of time pad: increment or
    decrement time.

    Parameters
    ----------
    * start_time

    * end_time

    * selected_time
        start_time (1) or end_time (2)

    * hour_min
        hour (1) or minute (2)

    Return
    ------
    * time_lt
        Modified time range list.
    """
    key = None
    if selected_time == 1:
        hour, minute = start_time.split(':')
    else:
        hour, minute = end_time.split(':') 

    hour, minute = int(hour), int(minute)
    
    # mod operator pattern?
    while (key != 10 if key else True):
        key = time_pad.getch()
        if chr(key) == 'k' or key == curses.KEY_UP: # increment time.
            if hour_min == 1:
                hour = int_to_time(hour+1, 1)
            else:
                minute = int_to_time(minute+1, 2)
        elif chr(key) == 'j' or key == curses.KEY_DOWN: # decrement time.
            if hour_min == 1:
                hour = int_to_time(hour+1, 1)
            else:
                minute = int_to_time(minute+1, 2)
        elif hour_min == 2:
            if chr(key) == 'K':
                minute = int_to_time(minute+10, 2)
            elif chr(key) == 'J':
                minute = int_to_time(minute-10, 2)

        # prepend zero for uniformity in length; to not have to deal with
        # string justification in table.
        hour_str = '0'+str(hour) if len(str(hour)) == 1 else str(hour)
        minute_str = '0'+str(minute) if len(str(minute)) == 1 else str(minute)
        
        if selected_time == 1:
            highlight_timestamp(time_pad, time_lt, time_col_w,
                                hour_str+':'+minute_str, end_time,
                                selected_time, hour_min)
        elif selected_time == 2:
            highlight_timestamp(time_pad, time_lt, time_col_w, start_time,
                               hour_str+':'+minute_str, selected_time, hour_min)

    if selected_time == 1:
        # modified start time plus end time.
        time_lt[row] = f'{hour_str}:{minute_str}-'+time_lt[row].split('-')[1]

    else:
        # start time plus modified end time.
        time_lt[row] = time_lt[row].split('-')[0]+f'-{hour_str}:{minute_str}'

    return time_lt

def modify_time_range(main_win, time_lt, time_pad, time_col_w, row):
    time_range = time_lt[row]
    start_time, end_time = time_range.split('-')

    highlight_timestamp(time_pad, time_lt, time_col_w, start_time, end_time, 1, 1)
    key = None
    col = 1
    time_pad.keypad(True)
    while True if not key else (chr(key) != 'H'):
        key = time_pad.getch()
        if chr(key) == 'h' or key == curses.KEY_LEFT:
            col -= 1 if col > 1 else -3
        elif chr(key) == 'l' or key == curses.KEY_RIGHT:
            col += 1 if col < 4 else -3

        selected = 1 if col < 3 else 2
        hour_min = 1 if col % 2 else 2

        highlight_timestamp(time_pad, time_lt, time_col_w, start_time,
                            end_time, selected, hour_min)
        if key == 10:
            time_lt = time_pad_inp(time_pad, time_lt, time_col_w, row, start_time,
                                  end_time, selected, hour_min)
            time_range = time_lt[row]
            start_time, end_time = time_range.split('-')
            highlight_timestamp(time_pad, time_lt, time_col_w, start_time,
                               end_time, selected, hour_min)

    return time_lt

def new_task_time_pair_lt(task_pad_lt, time_pad_lt, task_lt, time_lt,
                             task_col_w, time_col_w, row):
    task_pad_lt.insert(row, curses.newpad(1, task_col_w))
    time_pad_lt.insert(row, curses.newpad(1, time_col_w))

    task_lt.insert(row, ''); time_lt.insert(row, '')

    return task_pad_lt, time_pad_lt, task_lt, time_lt

def shift_hour(time_lt, row, left_right):
    if left_right == 1:
        for i in range(row, len(time_lt)):
            start_time, end_time = time_lt[i].split('-')

            start_time_h, start_time_m = start_time.split(':')
            end_time_h, end_time_m = end_time.split(':')

            start_time_h = int_to_time(int(start_time_h)+1, 1)
            end_time_h = int_to_time(int(end_time_h)+1, 1)

            time_lt[i] = f'{start_time_h}:{start_time_m}-{end_time_h}:{end_time_m}'
    else:
        # FIXME
        for i in range(1 if row == 0 else row):
            start_time, end_time = time_lt[i].split('-')

            start_time_h, start_time_m = start_time.split(':')
            end_time_h, end_time_m = end_time.split(':')

            start_time_h = int_to_time(int(start_time_h)-1, 1)
            end_time_h = int_to_time(int(end_time_h)-1, 1)

            time_lt[i] = f'{start_time_h}:{start_time_m}-{end_time_h}:{end_time_m}'

    return time_lt

def add_time_range(time_pad, time_lt, row, up_down):
    key = time_pad.getkey()

    if key == 'y' and row < len(time_lt)-1 and row > 0:
        time_range = time_lt[row+up_down]
        time_lt = shift_hour(time_lt, row+up_down, up_down)
    else:
        time_range = '00:00-00:00'

    time_lt[row] = time_range; return time_lt

def add_task_time_pair(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
                       task_col_w, time_col_w, row, col, up_down):

    task_pad_lt, time_pad_lt, task_lt, time_lt = new_task_time_pair_lt(
            task_pad_lt, time_pad_lt, task_lt, time_lt, task_col_w, time_col_w,
            row
            )
    draw_tam_table(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
                   task_col_w, time_col_w)
    selected_pad = get_selected_pad(task_pad_lt, time_pad_lt, row-up_down, col)
    selected_pad_content = pad_content(task_lt, time_lt, time_col_w, row-up_down,
                                       col)
    highlight_pad(selected_pad, True)
    refresh_pad(selected_pad, selected_pad.getbegyx(),
                task_col_w)

    task_lt = modify_task_name(main_win, task_pad_lt[row], task_pad_lt,
                               time_pad_lt, task_lt, time_lt, task_col_w,
                               time_col_w, row, col)
    time_lt = add_time_range(time_pad_lt[row], time_lt, row, up_down)

    insert_val_task_time_pads(task_lt, time_lt, task_pad_lt, time_pad_lt,
                              task_col_w, time_col_w)
    
    return task_pad_lt, time_pad_lt, task_lt, time_lt 
