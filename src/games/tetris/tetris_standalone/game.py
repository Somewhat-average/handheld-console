from settings import *
from random import choice

from timer_class import Timer

class Game:
    def __init__(self, get_next_shape, update_score, play_land_sound):

        # general
        self.surf = pygame.Surface((g_w, g_h))
        self.disp_surf = pygame.display.get_surface()
        self.rect = self.surf.get_rect(topleft = (hori_padding, vert_padding))
        self.sprites = pygame.sprite.Group()
        self.running = True
        self.play_land_sound = play_land_sound

        # game connection
        self.get_next_shape = get_next_shape
        self.update_score = update_score

        # lines
        self.line_surf = self.surf.copy()
        self.line_surf.fill((0, 255, 0))
        self.line_surf.set_colorkey((0, 255, 0))
        self.line_surf.set_alpha(120)

        # tetromino
        self.field_data = [[0 for x in range(cols)] for y in range(rows)]
        self.tetromino = Tetromino(
            choice(list(TETROMINOES.keys())), 
            self.sprites, 
            self.create_tetr, 
            self.field_data,
            self.play_land_sound
            )

        # timers
        self.down_speed = update_start_speed
        self.down_speed_fast = self.down_speed * update_start_speed_fast_perc
        self.down_pressed = False
        self.timers = {
            'vert move': Timer(self.down_speed, True, self.move_down),
            'hori move': Timer(move_wait_time),
            'rotate': Timer(rotate_wait_time)
        }
        self.timers['vert move'].activate()

        # score
        self.curr_sc = 0
        self.curr_lv = 1
        self.curr_li = 0

        self.update_score(self.curr_sc, self.curr_lv, self.curr_li)

    def calc_score(self, num_lines):
        self.curr_li += num_lines
        self.curr_sc += score_data[num_lines] * self.curr_lv

        # every 10 lines += level by 1
        if self.curr_li / 10 > self.curr_lv:
            self.curr_lv += 1
            self.down_speed *= level_down_speed_perc
            self.down_speed_fast = self.down_speed * update_start_speed_fast_perc
            self.timers['vert move'].duration = self.down_speed
        self.update_score(self.curr_sc, self.curr_lv, self.curr_li)

    def create_tetr(self):

        self.check_full_rows()
        self.tetromino = Tetromino(
            self.get_next_shape(), 
            self.sprites, 
            self.create_tetr, 
            self.field_data,
            self.play_land_sound
            )
        
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            if y >= 0 and self.field_data[y][x]:
                self.running = False
                break

    def disp_game_over(self):
        self.font = get_font(60)
        text_surf1 = self.font.render('Game Over', True, 'white')
        text_rect1 = text_surf1.get_rect(center = (self.disp_surf.get_width()/2, self.disp_surf.get_height()/2 - 3*vert_padding))
        self.disp_surf.blit(text_surf1, text_rect1)

        self.font = get_font(20)
        text_surf2 = self.font.render('\'w\' to quit', True, 'white')
        text_rect2 = text_surf2.get_rect(center = (self.disp_surf.get_width()/2, self.disp_surf.get_height()/2 + 2*vert_padding))
        self.disp_surf.blit(text_surf2, text_rect2)

        self.font = get_font(20)
        text_surf3 = self.font.render('\'a\' to play again', True, 'white')
        text_rect3 = text_surf3.get_rect(center = (self.disp_surf.get_width()/2, self.disp_surf.get_height()/2 + 5*vert_padding))
        self.disp_surf.blit(text_surf3, text_rect3)

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        self.tetromino.move_down()
    
    def draw_grid(self):
        self.line_surf.fill((0, 255, 0))

        for col in range(1, cols):
            x = col * cell_sz
            pygame.draw.line(self.line_surf, LINE_COLOR, (x, 0), (x, self.surf.get_height()), 1)

        for row in range(1, rows):
            y = row * cell_sz
            pygame.draw.line(self.line_surf, LINE_COLOR, (0, y), (self.surf.get_width(), y))
        
        self.surf.blit(self.line_surf, (0, 0))

    def input(self):
        keys = pygame.key.get_pressed()

        # check horizontal movement
        if not self.timers['hori move'].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_hori(-1)
                self.timers['hori move'].activate()
            if keys[pygame.K_RIGHT]:
                self.tetromino.move_hori(1)
                self.timers['hori move'].activate()

        # check rotation
        if not self.timers['rotate'].active:
            if keys[pygame.K_UP]:
                self.tetromino.rotate()
                self.timers['rotate'].activate()

        # check soft drop
        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers['vert move'].duration = self.down_speed_fast
        
        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers['vert move'].duration = self.down_speed

    def check_full_rows(self):

        # get full row indices
        full_rows = []
        for idx, row in enumerate(self.field_data):
            if all(row):
                full_rows.append(idx)

        if full_rows:
            for full_row in full_rows:
                
                # delete full row
                for block in self.field_data[full_row]:
                    block.kill()

                # move everything above down
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < full_row:
                            block.pos.y += 1

            # rebuild field data
            self.field_data = [[0 for x in range(cols)] for y in range(rows)]
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
        
            self.calc_score(len(full_rows))

    def update(self):

        # update
        if self.running:
            self.input()
            self.timer_update()
            self.sprites.update()

    def draw(self):

        # drawing
        self.surf.fill(GRAY)
        self.sprites.draw(self.surf)

        self.draw_grid()
        self.disp_surf.blit(self.surf, (hori_padding, vert_padding))
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 2)

class Tetromino:
    def __init__(self, shape, group, create_tetr, field_data, play_land_sound):

        # setup
        self.block_positions = TETROMINOES[shape]['shape']
        self.color = TETROMINOES[shape]['color']
        self.shape = shape
        self.create_tetr = create_tetr
        self.field_data = field_data
        self.running = True
        self.play_land_sound = play_land_sound

        # create blocks
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    # collision
    def next_move_vert_coll(self, amount):
        coll_list = [block.vert_coll(int(block.pos.y + amount), self.field_data) for block in self.blocks]
        return any(coll_list)
    
    def next_move_hori_coll(self, amount):
        coll_list = [block.hori_coll(int(block.pos.x + amount), self.field_data) for block in self.blocks]
        return any(coll_list)

    # movement
    def move_down(self):
        if not self.next_move_vert_coll(1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            self.play_land_sound()
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            
            self.create_tetr()

    def move_hori(self, amount):
        if not self.next_move_hori_coll(amount):
            for block in self.blocks:
                block.pos.x += amount

    def rotate(self):
        if self.shape != 'O':
            pivot_pos = self.blocks[0].pos

            new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

            for pos in new_block_positions:
                # horizontal collision check
                if pos.x < 0 or pos.x >= cols:
                    return
                
                # vertical collision check
                if pos.y >= rows or pos.y < 0:
                    return
                
                # block collision check
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return

            for idx, block in enumerate(self.blocks):
                block.pos = new_block_positions[idx]

class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color):
        
        # general
        super().__init__(group)
        self.image = pygame.Surface((cell_sz, cell_sz))
        self.image.fill(color)

        # position
        self.pos = pygame.Vector2(pos) + pygame.Vector2(block_offset)
        self.rect = self.image.get_rect(topleft = self.pos * cell_sz)

    def vert_coll(self, y, field_data):
        if y >= rows:
            return True
        if y >= 0 and field_data[int(y)][int(self.pos.x)]:
            return True
        return False

    def hori_coll(self, x, field_data):
        if not 0 <= x < cols:
            return True
        if field_data[int(self.pos.y)][int(x)]:
            return True
        return False

    def rotate(self, pivot_pos):
        return pivot_pos + (self.pos - pivot_pos).rotate(90)

    def update(self):
        self.rect.topleft = self.pos * cell_sz