from func import *


TAM_TABLE_FILE = '/home/nt/file.json'

def main(main_win):
    curses.curs_set(False)

    file = open(TAM_TABLE_FILE)

    task_time_dt = json.loads(file.read())

    task_lt = list(task_time_dt)
    time_lt = list(task_time_dt.values())

    task_col_w = len(max(task_lt, key=len))
    time_col_w = len(max(time_lt, key=len))

    task_pad_lt, time_pad_lt = init_task_time_pads(main_win, task_lt, time_lt,
                                                   task_col_w, time_col_w)

    draw_tam_table(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
                   task_col_w, time_col_w)

    task_pad_lt[0].keypad(True)
    
    # black on white, highlight.
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # white on black, de-highlight.
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    row = col = -1
    while True:
        key = task_pad_lt[0].getch()
        if (key == curses.KEY_UP or chr(key) == 'k') and row >= 0: # up.
            row = len(task_lt)-1 if row == 0 else row-1
        elif (key == curses.KEY_DOWN or chr(key) == 'j') and row >= 0: # down.
            row = 0 if row == len(task_lt)-1 else row+1
        elif (key  == curses.KEY_LEFT or chr(key) == 'h') and row >= 0: # left.
            col = 1 if col == 0 else 0
        elif (key == curses.KEY_RIGHT or chr(key) == 'l') and row >= 0: # right.
            col = 0 if col == 1 else 1
        elif (key == 10) and row >= 0: # enter.
            selected_pad = get_selected_pad(task_pad_lt, time_pad_lt, row, col)
            if col == 0: # task col.
                task_lt = modify_task_name(main_win, selected_pad, task_pad_lt,
                                           time_pad_lt, task_lt, time_lt,
                                           task_col_w, time_col_w, row, col)

                task_col_w = len(max(task_lt, key=len))
                time_col_w = len(max(time_lt, key=len))

                draw_tam_table(main_win, task_pad_lt, time_pad_lt, task_lt, time_lt,
                           task_col_w, time_col_w)
            else: # time col.
                time_lt = modify_time(main_win, time_lt, selected_pad, time_col_w, row)
                highlight_pad(selected_pad, True)

        elif chr(key) == 'q': # quit.
            break
        else: # first ever selected since executing program.
            if row == -1 and is_key_valid(key):
                row = col = 0
                selected_pad = get_selected_pad(task_pad_lt, time_pad_lt, row,
                                                col)
                selected_pad_content = pad_content(task_lt, time_lt,
                                                   time_col_w, row, col)

                highlight_pad(selected_pad)
                
                refresh_pad(selected_pad, selected_pad.getbegyx(),
                            len(selected_pad_content))

                prev_selected_pad = selected_pad
                prev_selected_pad_content = selected_pad_content
            continue

        selected_pad = get_selected_pad(task_pad_lt, time_pad_lt, row, col)

        selected_pad_content = pad_content(task_lt, time_lt, time_col_w, row,
                                           col)
        
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

    #update_task_time_file(task_lt, time_lt, task_time_dt)
    
curses.wrapper(main)
