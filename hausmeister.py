import pygame
import io


SCR_W = 320
SCR_H = 176

WIN_W = 1366
WIN_H = 768

TILE_W = 16
TILE_H = 16

FULLSCREEN = False




def load_level(path):
    file =io.open(path,"r")
    lvl =file.read().replace("/","").splitlines()
    file.close()
    

    
    return lvl
    




pygame.display.init()
window = pygame.display.set_mode((WIN_W, WIN_H), pygame.FULLSCREEN if FULLSCREEN else 0)
screen = pygame.Surface((SCR_W, SCR_H))

clock = pygame.time.Clock()


level = ['                    ',
         '                    ',
         '    ############    ',
         '                    ',
         '                    ',
         '                    ',
         '#######      #######',
         '                    ',
         '                    ',
         '                    ',
         '####################'
         ]

entities =[]

level =load_level("./lvl/001.lvl")
print(level)


LEV_W = len(level[0])
LEV_H = len(level)




tiles = {'#': pygame.image.load('gfx/wall.png'),
         ' ': pygame.image.load('gfx/background.png'),
         '-': pygame.image.load('gfx/floor.png'),
         'D': pygame.image.load('gfx/door.png'),
         'H': pygame.image.load('gfx/stairs.png'),
         'L': pygame.image.load('gfx/lamp.png'),
         'R': pygame.image.load('gfx/rat.png'),
         'S': pygame.image.load('gfx/spider.png'),
         }


playerSprites = [(pygame.image.load('gfx/player_left_1.png'), pygame.image.load('gfx/player_left_2.png')),
                 (pygame.image.load('gfx/player_right_1.png'), pygame.image.load('gfx/player_right_2.png')),
                 ]


    
def toggleFullscreen():
    global FULLSCREEN, window
    FULLSCREEN = not FULLSCREEN
    window = pygame.display.set_mode((WIN_W, WIN_H), pygame.FULLSCREEN if FULLSCREEN else 0)



LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3


class GameObject():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self.xdir = 0
        self.ydir = 0
        self.facedir = LEFT
        
        self.speed = 2
        self.gravity = 2
        
        self.jumpBlocked = False
        
    def moveLeft(self):
        self.xdir = -1
        self.facedir = LEFT
        
    def moveRight(self):
        self.xdir = 1
        self.facedir = RIGHT
        
    def moveUp(self):
        pass
        
    def moveDown(self):
        pass
        
    def doJump(self):
        if not self.jumpBlocked:
            self.ydir = -4
        
    def stopLeft(self):
        if self.xdir < 0:
            self.xdir = 0
        
    def stopRight(self):
        if self.xdir > 0:
            self.xdir = 0
        
    def stopUp(self):
        pass
        
    def stopDown(self):
        pass
        
    def cancelJump(self):
        pass
        #self.ydir = 0
        
    def update(self):
        updated = False

        newx = self.x
        newy = self.y
        
        newx += self.xdir * self.speed
        newy += (self.ydir + self.gravity) * self.speed
        
        if self.ydir < 0:
            self.ydir += 0.125
            
        # collision with screen bounds (left/right)
        if newx < 0:
            newx = 0
        if newx > SCR_W - TILE_W:
            newx = SCR_W - TILE_W
            
        # collision
        collx = int((newx - TILE_W / 2) / TILE_W)
        colly = int((newy +TILE_H-1) / TILE_H)
        
        if level[colly][collx] == ' ':
            self.y = newy
        else:
            self.jumpBlocked = False
            self.y = (colly -1) * TILE_H

        self.x = newx
        


class Player(GameObject):
    def __init__(self,x,y):
        super().__init__(x,y)


class Rat(GameObject):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.tile = "R"

    def update(self):
        pass

class Spider(GameObject):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.dir = "down"
        self.tile = "S"

        self.wait_frames = 0

        self.speed = 0.1

    def update(self):
        if self.dir == "down":
            if level[round(self.y+self.speed)][self.x] in [" "]: 
                self.y+=self.speed
            else:
                self.dir = "up"
                
        elif self.dir == "up":
            if level[round(self.y-self.speed)][self.x] in [" "]: 
                self.y-=self.speed/4
            else:
                self.dir = "wait"
                self.wait_frames = 40
                
        elif self.dir ==  "wait":
            if self.wait_frames == 0 :
                self.dir= "down"
            else:
                self.wait_frames-=1


        


player = Player(8 * TILE_W, 31 * TILE_H)

def get_entities(level):
    tmp_entities =[]

    y=0
    for line in level:
        x=0
        for char in line:
            
            if char == "R":
                tmp_entities.append(Rat(x,y))

                tmp_str =list(level[y])
                tmp_str[x]=" "
                level[y]="".join(tmp_str)
            elif char == "S":
                tmp_entities.append(Spider(x,y))

                tmp_str =list(level[y])
                tmp_str[x]=" "
                level[y]="".join(tmp_str)
            x+=1
        
        y+=1
    
    return tmp_entities
        


entities = get_entities(level)


def init():
    global player


def controls():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            return False
        
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return False
                
            if e.key == pygame.K_LEFT:
                player.moveLeft()
            if e.key == pygame.K_RIGHT:
                player.moveRight()
            if e.key == pygame.K_UP:
                player.moveUp()
            if e.key == pygame.K_DOWN:
                player.moveDown()
            if e.key == pygame.K_RCTRL:
                player.doJump()
                
            if e.key == pygame.K_RETURN:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_LALT or mods & pygame.KMOD_RALT:
                    toggleFullscreen()
                    
        if e.type == pygame.KEYUP:
            if e.key == pygame.K_LEFT:
                player.stopLeft()
            if e.key == pygame.K_RIGHT:
                player.stopRight()
            if e.key == pygame.K_UP:
                player.stopUp()
            if e.key == pygame.K_DOWN:
                player.stopDown()
            if e.key == pygame.K_RCTRL:
                player.cancelJump()
                
    return True
    
def render():
    screen.fill((0, 0, 0))
    
    scrolly = player.y - SCR_H * 0.75
    
    if scrolly > LEV_H * TILE_H:
        scrolly = LEV_H * TILE_H

    for y in range(LEV_H):
        for x in range(LEV_W):
            tile = level[y][x]
            
            if tile in tiles:                
                screen.blit(tiles[tile], (x * TILE_W, y * TILE_H - scrolly))
    

    for entity in entities:
        screen.blit(tiles[entity.tile],(entity.x*TILE_W,entity.y*TILE_H-scrolly))

    
    spr = playerSprites[player.facedir][int(tick % 20 / 10)]
    screen.blit(spr, (player.x, player.y - scrolly))

    


def update():
    player.update()

    for entity in entities:
        entity.update()
    
    
tick = 0
running = True

init()

while running:
    tick += 1
    
    render()
    
    pygame.transform.scale(screen, (WIN_W, WIN_H), window)
    pygame.display.flip()
    
    cont = controls()
    
    if not cont:
        running = False
        
    update()
    
    clock.tick(60)



