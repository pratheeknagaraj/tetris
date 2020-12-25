#!/usr/bin/python
# -*- coding: latin-1 -*-

import random
import threading
import os
import curses

debug_file = open('debug.txt','w')

def debug(out):
    debug_file = open('debug.txt','a+')
    debug_file.write(out + '\n')
    debug_file.close()

class Cell:

    def __init__(self,x,y):
        self.x = x
        self.y = y

        self.complete = False
        self.dead = False
        self.complete_state = 0

        self.color = None

    def get_char(self):
        if self.complete == True:
            WAIT_MULTIPLIER = 5
            self.complete_state += 1
            if self.complete_state <= 1 * WAIT_MULTIPLIER:
                return '-'
            elif self.complete_state <= 2 * WAIT_MULTIPLIER:
                return '\\'
            elif self.complete_state <= 3 * WAIT_MULTIPLIER:
                return '|'
            elif self.complete_state <= 4 * WAIT_MULTIPLIER:
                self.dead = True
                return '/'
        
            return ''

        return '*'
        #return '█'

    def set_color(self,color):
        self.color = color

    def get_color(self):
        return self.color

    def get_state(self):
        return self.complete

    def __equals__(cell1,cell2):
        if cell1.x == cell2.x and cell1.y == cell2.y:
            return True
        return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '(%d,%d)' % (self.x, self.y)

class Piece:

    def __init__(self,shape_type,cells,uuid=None):
        self.default_cells = cells
        self.cells = cells
        self.shape_type = shape_type
        self.uuid = uuid
        self.orientation = 0

        self.set_color()

    def set_color(self):
        for cell in self.cells:
            cell.set_color(piece_colors[self.shape_type])

        for cell in self.default_cells:
            cell.set_color(piece_colors[self.shape_type])

    def get_rotation_cells(self,direction):
        if self.shape_type == 'o':
            return self.cells

        delta_func = None
        if self.shape_type == 'j':
            delta_func = j_deltas
        elif self.shape_type == 'l':
            delta_func = l_deltas
        elif self.shape_type == 'i':
            delta_func = i_deltas
        elif self.shape_type == 't':
            delta_func = t_deltas
        elif self.shape_type == 's':
            delta_func = s_deltas
        elif self.shape_type == 'z':
            delta_func = z_deltas

        if direction == 'COUNTER':
            new_orientation = (self.orientation - 1) % 4
        elif direction == 'CLOCK':
            new_orientation = (self.orientation + 1) % 4
        else:
            debug("ERROR: direction %s" % (direction))
            return None

        add_cells = delta_func(new_orientation)
        sub_cells = delta_func(self.orientation)
        return add_sub_cells(self.cells, add_cells, sub_cells)

    def get_translation_cells(self,direction,count=1):
        add_cells = None
        if direction == 'LEFT':
            add_cells = [(-1,0)]*4
        elif direction == 'RIGHT':
            add_cells = [(1,0)]*4
        elif direction == 'DOWN':
            add_cells = [(0,1*count)]*4
        elif direction == 'UP':
            add_cells = [(1,0)]*4

        return add_sub_cells(self.cells, add_cells)

    def get_down_cells(self):
        cells = []
        for cell in self.cells:
            cells.append(Cell(cell.x,cell.y + 1))
        return cells

    def update_cells(self,cells,orientation_del=0):
        self.cells = cells
        self.orientation = (self.orientation + orientation_del) % 4
        self.set_color()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'Piece\n\tUUID: %d\n\tType: %s\n\tCells: %s' % (self.uuid, self.shape_type, self.cells)

def gen_o(uuid):
    return Piece('o', [Cell(0,0),Cell(1,0),Cell(0,1),Cell(1,1)], uuid )

def gen_j(uuid):
    return Piece('j', [Cell(1,0),Cell(1,1),Cell(1,2),Cell(0,2)], uuid)

def gen_l(uuid):
    return Piece('l', [Cell(0,0),Cell(0,1),Cell(0,2),Cell(1,2)], uuid)

def gen_i(uuid):
    return Piece('i', [Cell(0,0),Cell(0,1),Cell(0,2),Cell(0,3)], uuid)

def gen_t(uuid):
    return Piece('t', [Cell(0,0),Cell(1,0),Cell(2,0),Cell(1,1)], uuid)

def gen_s(uuid):
    return Piece('s', [Cell(1,0),Cell(2,0),Cell(0,1),Cell(1,1)], uuid)

def gen_z(uuid):
    return Piece('z', [Cell(0,0),Cell(1,0),Cell(1,1),Cell(2,1)], uuid)

def add_sub_cells(cells,add=None,sub=None):
    new_cells = []
    for cell in cells:
        new_cells.append( Cell(cell.x, cell.y) )

    if sub != None:
        for new_cell, delta in zip(new_cells, sub):
            new_cell.x -= delta[0]
            new_cell.y -= delta[1]

    if add != None:
        for new_cell, delta in zip(new_cells, add):
            new_cell.x += delta[0]
            new_cell.y += delta[1]

    return new_cells

def l_deltas(orientation):
    if orientation == 0:
        return [(0,0),(0,1),(0,2),(1,2)]
    elif orientation == 1:
        return [(-1,1),(0,1),(1,1),(1,0)]
    elif orientation == 2:
        return [(-1,0),(0,0),(0,1),(0,2)]
    elif orientation == 3:
        return [(-1,2),(-1,1),(0,1),(1,1)]
    return None

def j_deltas(orientation):
    if orientation == 0:
        return [(1,0),(1,1),(1,2),(0,2)]
    elif orientation == 1:
        return [(0,1),(1,1),(2,1),(2,2)]
    elif orientation == 2:
        return [(1,2),(1,1),(1,0),(2,0)]
    elif orientation == 3:
        return [(2,1),(1,1),(0,1),(0,0)]

def i_deltas(orientation):
    if orientation == 0:
        return [(0,0),(0,1),(0,2),(0,3)]
    elif orientation == 1:
        return [(-1,1),(0,1),(1,1),(2,1)]
    elif orientation == 2:
        return [(-1,2),(-1,1),(-1,0),(-1,-1)]
    elif orientation == 3:
        return [(1,2),(0,2),(-1,2),(-2,2)]
    return None

def t_deltas(orientation):
    if orientation == 0:
        return [(0,0),(1,0),(2,0),(1,1)]
    elif orientation == 1:
        return [(1,1),(1,0),(1,-1),(2,0)]
    elif orientation == 2:
        return [(2,0),(1,0),(0,0),(1,-1)]
    elif orientation == 3:
        return [(1,-1),(1,0),(1,1),(0,0)]
    return None

def s_deltas(orientation):
    if orientation == 0:
        return [(1,0),(2,0),(0,1),(1,1)]
    elif orientation == 1:
        return [(2,1),(2,2),(1,0),(1,1)]
    elif orientation == 2:
        return [(1,2),(0,2),(2,1),(1,1)]
    elif orientation == 3:
        return [(0,1),(0,0),(1,2),(1,1)]
    return None

def z_deltas(orientation):
    if orientation == 0:
        return [(0,0),(1,0),(1,1),(2,1)]
    elif orientation == 1:
        return [(2,0),(2,1),(1,1),(1,2)]
    elif orientation == 2:
        return [(2,2),(1,2),(1,1),(0,1)]
    elif orientation == 3:
        return [(0,2),(0,1),(1,1),(1,0)]
    return None

piece_types = ['o','j','l','i','t','s','z']

piece_gen = {
    'o': gen_o,
    'j': gen_j,
    'l': gen_l,
    'i': gen_i,
    't': gen_t,
    's': gen_s,
    'z': gen_z,
}

piece_colors = {
    'o': 'YELLOW',
    'j': 'BLUE',
    'l': 'ORANGE',
    'i': 'CYAN',
    't': 'PURPLE',
    's': 'GREEN',
    'z': 'RED',
}

class Tetris:

    def __init__(self,cols,rows):
        self.rows = rows
        self.cols = cols

        self.filled_cells = []

        self.pieces = []
        self.cur_piece = None

        self.inputs = []
        self.input_lock = threading.Lock()

        self.TICK_STEP_MIN = 10
        self.TICK_STEP_MAX = 100
        self.TICK_GRADIENT = 5

        self.tick_step = self.TICK_STEP_MAX 
        self.ticks = 0  

        self.SOFT_DROP_MULT = 1
        self.HARD_DROP_MULT = 2
        self.COMBO_MULT = 1.5

        self.combo_count = 0

        self.score = 0
        self.piece_count = 0

        self.level = 1
        self.level_advance = 10
        self.lines = 0

        self.queuing = True
        self.piece_history = []
        if self.queuing:
            self.queued_piece = self.get_new_piece()

        self.game_over = False

        self.set_new_piece()

    def tick(self):
        # tick step
        self.time_step()

        # clean up
        self.check_filled_cells()

        # tick action
        if self.check_tick_count():

            # check if placed
            if self.check_if_placed(self.cur_piece):
                self.set_new_piece()
            else:
                # move piece
                self.tick_move_piece()
                #if self.check_if_placed(self.cur_piece):
                #    self.set_new_piece()

            self.check_complete_rows()

        self.game_over = self.is_game_over()
        return not self.game_over

    def get_level(self):
        return self.level

    def check_filled_cells(self):
        cells_cleared = 0
        
        new_cells_by_row = {}

        new_filled_cells = []
        for cell in self.filled_cells:
            if not cell.dead:
                new_filled_cells.append(cell)

                if cell.y not in new_cells_by_row:
                    new_cells_by_row[cell.y] = []
                new_cells_by_row[cell.y].append(cell)

        cells_cleared = len(self.filled_cells) - len(new_filled_cells)
        self.filled_cells = new_filled_cells
                
        if cells_cleared % self.cols != 0:
            debug("ERROR: cells cleared not multiple of cols")
            return

        if cells_cleared > 0:

            # Shift cells down
            current_fill_by_col = {}
            keys = new_cells_by_row.keys()
            keys = sorted(keys, reverse=True)
            for row in keys:
                for cell in new_cells_by_row[row]:
                    x = cell.x
                    y = cell.y
                    if x not in current_fill_by_col:
                        cell.y = self.rows-1
                        current_fill_by_col[x] = cell.y
                    else:
                        cell.y = current_fill_by_col[x]-1
                        current_fill_by_col[x] -= 1

            displacement = cells_cleared / self.cols
            #for cell in self.filled_cells:
            #    cell.y += displacement

            self.rows_cleared(displacement)

    def rows_cleared(self, count):
        BASE = 100
        MULT = {1: 1, 2: 3, 3: 5, 4: 8} # Rows to Mult

        # Combos (additive)
        combo_mult = 1
        if self.combo_count > 0:
            combo_mult = self.COMBO_MULT * self.combo_count
            self.combo_count += 2
        else:
            self.combo_count = 2

        self.score += BASE * MULT[count] * self.level * combo_mult
        self.lines += count

        self.level = self.lines/self.level_advance + 1
        self.set_tick_step()

    def set_tick_step(self):
        proposed = self.TICK_STEP_MAX - (self.level-1)*self.TICK_GRADIENT
        self.tick_step = max(self.TICK_STEP_MIN, proposed)

    def get_lines(self):
        return self.lines

    def get_score(self):
        return self.score

    def get_cells_to_fill(self):
        cells = []
        cells.extend(self.filled_cells)
        if self.cur_piece != None:
            cells.extend(self.cur_piece.cells)
        return cells

    def set_new_piece(self):
        self.piece_count += 1
        self.combo_count -= 1

        if self.cur_piece != None:
            self.fill_cells(self.cur_piece)
        
        piece = None
        if self.queuing:
            piece = self.queued_piece
            self.queued_piece = self.get_new_piece()
        else:
            piece = self.get_new_piece()
        self.cur_piece = piece
        self.pieces.append(piece)

    def time_step(self):
        self.ticks += 1

    def input(self,cmd):

        with self.input_lock:
            if self.game_over == False:
                if cmd == 0:
                    # UP
                    self.inputs.append('UP')
                elif cmd == 1:
                    # RIGHT
                    self.inputs.append('RIGHT')
                elif cmd == 2:
                    # DOWN
                    self.inputs.append('DOWN')
                elif cmd == 3:
                    # LEFT
                    self.inputs.append('LEFT')
                elif cmd == 4:
                    # SPACE
                    self.inputs.append('SPACE')
                elif cmd == 5:
                    # Q
                    self.inputs.append('Q')
                elif cmd == 6:
                    # E
                    self.inputs.append('E')
                elif cmd == 7:
                    # W
                    self.inputs.append('W')
        self.key_move_piece()
        return

    def is_game_over(self):
        if self.cur_piece != None:
            for cell in self.filled_cells:
                for cur_cell in self.cur_piece.cells:
                    if  cur_cell.x == cell.x and \
                        cur_cell.y == cell.y:
                        return True

        return False

    def fill_cells(self,piece):
        self.filled_cells.extend(piece.cells)

    def soft_drop(self):        
        # SOFT DROP
        self.score += self.SOFT_DROP_MULT

    def hard_drop(self, line_count):
        self.score += self.HARD_DROP_MULT * line_count

    def key_move_piece(self):
        key = None
        if len(self.inputs) > 0:
            with self.input_lock:
                key = self.inputs.pop(0)

        if key != None:
            # Perform rotation, or down
            new_cells = None
            orientation_del = 0
            move_count = None

            if key == 'UP':
                orientation_del = -1
                new_cells = self.cur_piece.get_rotation_cells('COUNTER')
            elif key == 'LEFT':
                new_cells = self.cur_piece.get_translation_cells('LEFT')
            elif key == 'RIGHT':
                new_cells = self.cur_piece.get_translation_cells('RIGHT')
            elif key == 'DOWN':
                new_cells = self.cur_piece.get_translation_cells('DOWN')
            elif key == 'Q':
                orientation_del = -1
                new_cells = self.cur_piece.get_rotation_cells('COUNTER')                
            elif key == 'E':
                orientation_del = 1
                new_cells = self.cur_piece.get_rotation_cells('CLOCK')
            elif key == 'W':
                new_cells = self.cur_piece.cells
                move_count = 0
                while self.is_valid_cells(new_cells):
                    move_count += 1
                    new_cells = self.cur_piece.get_translation_cells('DOWN', move_count)
                move_count -= 1
                new_cells = self.cur_piece.get_translation_cells('DOWN', move_count)

            if new_cells != None:
                if self.is_valid_cells(new_cells):
                    if key == 'DOWN' and self.different_cells(self.cur_piece.cells, new_cells):
                        self.soft_drop()
                    elif key == 'W' and self.different_cells(self.cur_piece.cells, new_cells):
                        self.hard_drop(move_count)

                    self.cur_piece.update_cells(new_cells, orientation_del)
   
        self.moved_piece()

    def different_cells(self,a,b):
        for c1, c2 in zip(a,b):
            if c1.x != c2.x or c1.y != c2.y:
                return True
        return False

    def moved_piece(self):
        # TODO: anything?
        pass

    def check_complete_rows(self):
        row_counts = {}
        for filled_cell in self.filled_cells:
            y = filled_cell.y
            if y not in row_counts:
                row_counts[y] = []
            row_counts[y].append(filled_cell)

        for row, cells in row_counts.items():
            if len(cells) == self.cols:
                for cell in cells:
                    cell.complete = True 
                    # TODO: More

    def check_tick_count(self):
        if self.ticks >= self.tick_step:
            self.ticks = 0
            return True
        return False

    def tick_move_piece(self):
        new_cells = self.cur_piece.get_down_cells()
        self.cur_piece.update_cells(new_cells)

        self.moved_piece()

    def is_valid_cells(self,cells):
        # TODO: Allow Wall Kicking

        for cell in cells:
            # Check against filled cells
            for filled_cell in self.filled_cells:
                if filled_cell.x == cell.x and \
                   filled_cell.y == cell.y:
                       return False

            # Check against boundaries
            if cell.x >= self.cols:
                return False
            if cell.x < 0:
                return False
            if cell.y < 0:
                return False
            if cell.y >= self.rows:
                return False

        return True

    def get_piece_count(self):
        return self.piece_count

    def get_new_piece(self):
        passed = False
        piece_type = None

        while not passed:
            pieces_count = len(piece_types)
            piece_num = int(pieces_count*random.random())
            piece_type = piece_types[piece_num]

            # Check Four S or Z Rule
            if piece_type not in ['s','z']:
                passed = True
            else:
                last = self.piece_history[-4:]
                count_last = 0
                for prev in last:
                    if prev in ['s','z']:
                        count_last += 1
                
                if count_last < 4:
                    passed = True

        self.piece_history.append(piece_type)

        piece_func = piece_gen[piece_type]
                
        piece = piece_func(self.piece_count)

        # Center
        # TODO: Rotate?
        piece.update_cells(add_sub_cells(piece.cells,self.center_cells()))

        return piece

    def center_cells(self):
        x_mid = self.cols/2
        y_mid = 0
        return [(x_mid,y_mid)]*4

    def check_if_placed(self,piece):
        new_cells = piece.get_down_cells()

        for new_cell in new_cells:
            if new_cell.y == self.rows:
                return True

            for filled_cell in self.filled_cells:
                if new_cell.y == filled_cell.y and \
                   new_cell.x == filled_cell.x:
                    return True

        return False
