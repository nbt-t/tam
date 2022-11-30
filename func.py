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

def init_task_time_pads(main_win, task_lt, time_lt, task_col_w, time_col_w):
    """
    Create (initialize) task-time pads.

    Returns
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
    Fetches and returns pad's content. From task_lt if col is 0, and time_lt
    if otherly.

    Parameters
    ----------
    * row   
        Pad's row (y).

    * col
        Pad's col (x).

    Returns
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
    Returns True if key is valid.

    Parameters
    ----------
    * key.

    Returns
    -------
    * Boolean value (True/False).
    """
    valid_keys_normal = 'kjhl'
    valid_keys_special = [curses.KEY_UP, curses.KEY_DOWN,
                          curses.KEY_LEFT, curses.KEY_RIGHT, 10]
    if chr(key) in valid_keys_normal or key in valid_keys_special:
        return True
    return False

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

    Returns
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
    time_range = time_lt[y]
    start_time, end_time = time_range.split('-')

    highlight_time_pad(time_pad, time_lt, time_col_w, start_time, end_time, 1, 1)
    key = None
    col = 1
    time_pad.keypad(True)
    while True if not key else (chr(key) != 'H'):
        key = time_pad.getch()
        if chr(key) == 'h' or key == curses.KEY_LEFT:
            col -= 1 if col > 1 else -3
        elif chr(key) == 'l' or key == curses.KEY_RIGHT:
            col += 1 if col < 4 else -3

        highlight_time_pad(time_pad, time_lt, time_col_w,
                           start_time, end_time,
                           1 if col < 3 else 2, 1 if col % 2 else 2)
        if key == 10:
            time_lt = change_time(time_pad, time_lt, time_col_w, start_time,
                                  end_time, 1 if col < 3 else 2, 1 if col % 2 else 2, y)
            time_range = time_lt[y]
            start_time, end_time = start_end.split('-')
            highlight_time_pad(time_pad, time_lt, time_col_w, start_time,
                               end_time, 1 if col < 3 else 2, 1 if col % 2 else 2)

    return time_lt
    
def get_selected_pad(task_pad_lt, time_pad_lt, row, col):
    return task_pad_lt[row] if col == 0 else time_pad_lt[row]

def refresh_pad(pad, yx, width):
    y, x = yx
    pad.refresh(0, 0, y, x, y, x+width)
     
def draw_tam_table(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
               task_col_w, time_col_w):
    main_win.erase()
    draw_layout(main_win, len(task_lt), time_lt, task_col_w, time_col_w)
    main_win.refresh()
    insert_val_task_time_pads(task_lt, time_lt, task_pad_lt, time_pad_lt,
                              task_col_w, time_col_w)
    curses.doupdate()

def update_task_time_file(task_lt, time_lt, task_time_dt):
    old_task_lt = list(task_time_dt); old_time_lt = list(task_time_dt.values())
    for i in range(len(task_lt)):
        task_time_dt[task_lt[i]] = time_lt[i]
    return task_time_dt
