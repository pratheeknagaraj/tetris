#!/usr/bin/python
# -*- coding: latin-1 -*-

from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from tetris import Tetris
import curses
import threading
import time
import sys
import locale

try:
    def debug(out):
        debug_file = open('debug.txt','a+')
        debug_file.write(out + '\n')
        debug_file.close()

    locale.setlocale(locale.LC_ALL, '')    # set your locale
    
    game_size = (10,20)

    panel_width = 16

    curses.initscr()
    curses.start_color()
    curses.use_default_colors()

    win = curses.newwin(game_size[1]+4,game_size[0]*2+panel_width+4,0,0)
    win.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    win.border(0)
    win.nodelay(1)

    def create_game():
        game = Tetris(game_size[0],game_size[1])
        return game

    tick_time = 0.01
    end = False
    reset = False
    input = None
    lock = threading.Lock()
    stored_exc = None

    class InputThread(threading.Thread):

        def __init__(self, game):
            super(InputThread, self).__init__()
            self.game = game

        def set_game(self,game):
            self.game = game

        def run(self):
            global input
            global end
            global stored_exc
            global reset
            try:
                while input != 27:
                    if input:
                        with lock:
                            if input == KEY_UP:
                                self.game.input(0)
                            elif input == KEY_RIGHT or input == ord('d'):
                                self.game.input(1)
                            elif input == KEY_DOWN or input == ord('s'):
                                self.game.input(2)
                            elif input == KEY_LEFT  or input == ord('a'):
                                self.game.input(3)
                            elif input == ord(' '):
                                # NEW GAME:
                                self.game.input(4)
                                reset = True
                                return
                            elif input == ord('q'):
                                self.game.input(5)
                            elif input == ord('e'):
                                self.game.input(6)
                            elif input == ord('w'):
                                self.game.input(7)
                        input = None
                    time.sleep(0.001)
            except Exception:
                stored_exc = sys.exc_info()
                debug(str(stored_exc))

            end = True

    curses.init_color(10,1000,500,0)    # Orange
    curses.init_color(11,1000,0,1000)   # Purple
    curses.init_color(12,250,250,250)   # Grey
    curses.init_color(13,100,100,100)   # Grey 2
    curses.init_color(14,200,50,50)     # Red-Grey
    
    # Foreground & Background

    curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_YELLOW)
    curses.init_pair(2,curses.COLOR_BLUE,curses.COLOR_BLUE)
    curses.init_pair(3,10,10)
    curses.init_pair(4,curses.COLOR_CYAN,curses.COLOR_CYAN)
    curses.init_pair(5,11,11)
    curses.init_pair(6,curses.COLOR_GREEN,curses.COLOR_GREEN)
    curses.init_pair(7,curses.COLOR_RED,curses.COLOR_RED)
    
    # Foreground

    curses.init_pair(11,curses.COLOR_YELLOW,-1)
    curses.init_pair(12,curses.COLOR_BLUE,-1)
    curses.init_pair(13,10,-1)
    curses.init_pair(14,curses.COLOR_CYAN,-1)
    curses.init_pair(15,11,-1)
    curses.init_pair(16,curses.COLOR_GREEN,-1)
    curses.init_pair(17,curses.COLOR_RED,-1)

    # Other

    curses.init_pair(20,12,-1)
    curses.init_pair(21,curses.COLOR_WHITE,14)
    curses.init_pair(22,curses.COLOR_WHITE,13)
    
    colors = {
        'YELLOW': 1,
        'BLUE': 2,
        'ORANGE': 3,
        'CYAN': 4,
        'PURPLE': 5,
        'GREEN': 6,
        'RED': 7,
    }

    def get_color(color):
        if color in colors: 
            return colors[color]

        return 0

    def draw():
        win.clear()
        win.border(0)

        for cell in game.get_cells_to_fill():
            color_num = get_color(cell.get_color())
            complete = cell.get_state()
            if complete:
                color_num += 10

            win.addstr(cell.y + 2, cell.x*2 + 2, cell.get_char(), curses.color_pair(color_num))
            win.addstr(cell.y + 2, cell.x*2+1 + 2, cell.get_char(), curses.color_pair(color_num))

        draw_game_frame()
        draw_panel()

        #win.box(10,10)
        #game_frame.refresh()
        #win.refresh()
        #win.getch()
        #game_frame.refresh()

    def draw_game_frame():
        x = game_size[0]*2
        y = game_size[1]
        frame = []
        #frame.extend( [(1   ,2+i,curses.ACS_HLINE) for i in xrange(x)] )
        #frame.extend( [(y+2 ,2+i,curses.ACS_HLINE) for i in xrange(x)] )
        #frame.extend( [(2+j ,1  ,curses.ACS_VLINE) for j in xrange(y)] )
        #frame.extend( [(2+j ,x+2,curses.ACS_VLINE) for j in xrange(y)] )
        frame.append( (1    ,1  ,curses.ACS_ULCORNER) )
        frame.append( (1    ,2+x,curses.ACS_URCORNER) )
        frame.append( (2+y  ,1  ,curses.ACS_LLCORNER) )
        frame.append( (2+y  ,2+x,curses.ACS_LRCORNER) )

        for frame_cell in frame:
            win.addch(frame_cell[0], frame_cell[1], frame_cell[2])

        #box = curses.newwin(y,x,1,1)
        #box.immedok(True)

        #box.box()
        #box.refresh()
        #return box

    def draw_panel():
        x = game_size[0]*2
        y = game_size[1]
        win.addstr(2, x+5, '%10s' % 'TETRIS', curses.A_BOLD )
        win.addstr(4, x+5, 'Score: %6d' % game.get_score(), curses.color_pair(21))
        win.addstr(5, x+5, 'Level: %6d' % game.get_level(), curses.color_pair(20))
        win.addstr(6, x+5, 'Lines: %6d' % game.get_lines(), curses.color_pair(20))
        win.addstr(7, x+5, 'Pieces: %5d' % game.get_piece_count(), curses.color_pair(20))

        if game.queuing:
            # Draw next piece
            win.addstr(9, x+5, 'Next')
            
            off_x = x+5
            off_y = 11

            for cell in game.queued_piece.default_cells:
                color_num = get_color(cell.get_color())

                win.addstr(off_y+cell.y,off_x+cell.x*2+1,cell.get_char(),curses.color_pair(color_num))
                win.addstr(off_y+cell.y,off_x+cell.x*2+2,cell.get_char(),curses.color_pair(color_num))


    def draw_game_over():
        x = game_size[0]
        y = game_size[1]

        win.addstr(12, x/2 + 4, 'Game Over', curses.color_pair(22))
        win.addstr(13, x/2, '[SPACE] - New Game', curses.color_pair(22))

    # draw()

    while True:
        game = create_game()

        assert(game != None)

        end = False
        reset = False
        input = None

        input_thread = InputThread(game)
        # input_thread.daemon - True
        input_thread.start()

        # Play Game
        while not end and game.tick():
            if reset:
                break

            draw()
            ch = win.getch()
            if ch != -1:
                with lock:
                    input = ch
            time.sleep(tick_time)

        # Game Over
        while not reset:
            draw()
            draw_game_over()
            ch = win.getch()
            if ch != -1:
                with lock:
                    input = ch
            time.sleep(tick_time)

        # debug(str(input_thread.is_alive()))
        debug(str(end) + ',' + str(reset))
        input_thread.join()

    curses.endwin()
    print '\nScore:', game.score

except:
    curses.endwin()
    raise

if stored_exc:
    raise stored_exc[0], stored_exc[1], stored_exc[2]
