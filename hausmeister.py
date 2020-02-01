import pygame
import io


SCR_W = 320
SCR_H = 176

WIN_W = 1366
WIN_H = 768

TILE_W = 16
TILE_H = 16

FPS = 60

FULLSCREEN = False

DEBUG_MODE = False


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


debugList = []

scrolly = 0
scroll = False

tiles = {'#': pygame.image.load('gfx/wall.png'),
         ' ': pygame.image.load('gfx/background.png'),
         '-': pygame.image.load('gfx/floor.png'),
         '=': pygame.image.load('gfx/floor_2.png'),
         'D': pygame.image.load('gfx/door.png'),
         'H': pygame.image.load('gfx/stairs.png'),
         'L': pygame.image.load('gfx/lamp.png'),
         'R': pygame.image.load('gfx/rat.png'),
         'S': pygame.image.load('gfx/spider.png'),
         }

OBSTACLES = ['#', '-', '=']
CLIMBABLE = ['H']

playerSprites = [(pygame.image.load('gfx/player_left_1.png'), pygame.image.load('gfx/player_left_2.png')),
                 (pygame.image.load('gfx/player_right_1.png'), pygame.image.load('gfx/player_right_2.png')),
                 (pygame.image.load('gfx/player_up_1.png'), pygame.image.load('gfx/player_up_2.png')),
                 (pygame.image.load('gfx/player_down_1.png'), pygame.image.load('gfx/player_down_2.png')),
                 ]

debugSprite = pygame.image.load('gfx/debug.png')

    
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
        self.ydir = -1
        self.facedir = UP
        
    def moveDown(self):
        self.ydir = 1
        self.facedir = DOWN
        
    def doJump(self):
        if not self.jumpBlocked:
            self.ydir = -4
            self.jumpBlocked = True
        
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
        pass
        
        
class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.climb = False
        
    def update(self):
            
        # horizontal collision
        
        newxdir = self.xdir * self.speed
        newydir = self.ydir * self.speed

        newx = self.x + newxdir
        newy = self.y
        
        x1 = int(newx / TILE_W)
        x2 = int((newx + TILE_W -1) / TILE_W)
        y1 = int(newy / TILE_H)
        y2 = int((newy + TILE_H -1) / TILE_H)

        colltile1 = level[y1][x1]  # upper left
        colltile2 = level[y1][x2]  # upper right
        colltile3 = level[y2][x1]  # lower left
        colltile4 = level[y2][x2]  # lower right

        global debugList
        debugList.append((x1 * TILE_W, y1 * TILE_H))
        debugList.append((x2 * TILE_W, y1 * TILE_H))
        debugList.append((x1 * TILE_W, y2 * TILE_H))
        debugList.append((x2 * TILE_W, y2 * TILE_H))

        if self.xdir < 0:
            if colltile1 in OBSTACLES and colltile3 in OBSTACLES:
                newxdir = 0
            elif colltile1 in OBSTACLES and colltile3 not in OBSTACLES:
                newxdir = 0
                #newydir = SPEED
            elif colltile1 not in OBSTACLES and colltile3 in OBSTACLES:
                newxdir = 0
                #newydir = -SPEED
        elif self.xdir > 0:
            if colltile2 in OBSTACLES and colltile4 in OBSTACLES:
                newxdir = 0
            elif colltile2 in OBSTACLES and colltile4 not in OBSTACLES:
                newxdir = 0
                #newydir = SPEED
            elif colltile2 not in OBSTACLES and colltile4 in OBSTACLES:
                newxdir = 0
                #newydir = -SPEED

        # collision with screen bounds (left/right)
        newx = self.x + newxdir
        
        if newx < 0:
            newx = 0
        elif newx > SCR_W - TILE_W -self.speed:
            newx = SCR_W - TILE_W -self.speed

        self.x = newx
        
        # vertical collision
        
        
        if self.climb:
            gravity = 0
        else:
            gravity = self.gravity

        newxdir = self.xdir * self.speed
        newydir = self.ydir * self.speed + gravity

        newx = self.x
        newy = self.y + newydir
        
        x1 = int(newx / TILE_W)
        x2 = int((newx + TILE_W -1) / TILE_W)
        y1 = int(newy / TILE_H)
        y2 = int((newy + TILE_H -1) / TILE_H)

        colltile1 = level[y1][x1]  # upper left
        colltile2 = level[y1][x2]  # upper right
        colltile3 = level[y2][x1]  # lower left
        colltile4 = level[y2][x2]  # lower right

        debugList.append((x1 * TILE_W, y1 * TILE_H))
        debugList.append((x2 * TILE_W, y1 * TILE_H))
        debugList.append((x1 * TILE_W, y2 * TILE_H))
        debugList.append((x2 * TILE_W, y2 * TILE_H))

        if self.ydir + gravity < 0:
            if colltile1 in OBSTACLES and colltile2 in OBSTACLES:
                newydir = 0
            elif colltile1 in OBSTACLES and colltile2 not in OBSTACLES:
                newydir = 0
                #newxdir = SPEED
            elif colltile1 not in OBSTACLES and colltile2 in OBSTACLES:
                newydir = 0
                #newxdir = -SPEED
        elif self.ydir + gravity > 0:
            if colltile3 in OBSTACLES and colltile4 in OBSTACLES:
                newydir = 0
                self.jumpBlocked = False
            elif colltile3 in OBSTACLES and colltile4 not in OBSTACLES:
                newydir = 0
                self.jumpBlocked = False
                #newxdir = SPEED
            elif colltile3 not in OBSTACLES and colltile4 in OBSTACLES:
                newydir = 0
                self.jumpBlocked = False
                #newxdir = -SPEED

        self.y += newydir
        
        # climb
        
        if colltile1 in CLIMBABLE or colltile2 in CLIMBABLE or colltile3 in CLIMBABLE or colltile4 in CLIMBABLE:
            if self.ydir != 0:
                self.climb = True
        else:
            self.climb = False
            
        # jump
        
        if self.ydir < 0:
            self.ydir += 0.25
            

class Spider(GameObject):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.dir = "down"
        self.tile = "S"

        self.wait_frames = 0

        self.speed = 1

    def update(self):
        if self.dir == "down":
            if level[round(self.y / TILE_H + self.speed)][int(self.x / TILE_W)] in [" "]: 
                self.y+=self.speed
            else:
                self.dir = "up"
                
        elif self.dir == "up":
            if level[round(self.y / TILE_H - self.speed)][int(self.x / TILE_W)] in [" "]: 
                self.y-=self.speed/4
            else:
                self.dir = "wait"
                self.wait_frames = 40
                
        elif self.dir ==  "wait":
            if self.wait_frames == 0 :
                self.dir= "down"
            else:
                self.wait_frames-=1


class Rat(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tile = "R"
        


def get_entities(level):
    tmp_entities =[]

    y=0
    for line in level:
        x=0
        for char in line:
            
            if char == "R":
                tmp_entities.append(Rat(x * TILE_W, y * TILE_H))

                tmp_str =list(level[y])
                tmp_str[x]=" "
                level[y]="".join(tmp_str)
            elif char == "S":
                tmp_entities.append(Spider(x * TILE_W, y * TILE_H))

                tmp_str =list(level[y])
                tmp_str[x]=" "
                level[y]="".join(tmp_str)
            elif char == "@":
                tmp_entities.append(Player(x * TILE_W, y * TILE_H))
                
                tmp_str =list(level[y])
                tmp_str[x]=" "
                level[y]="".join(tmp_str)
                
            x+=1
        
        y+=1
    
    return tmp_entities
        


entities = get_entities(level)

for e in entities:
    if type(e) is Player:
        player = e
        entities.remove(e)
        break


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
                
            if e.key == pygame.K_F11:
                global FPS
                if FPS == 20:
                    FPS = 60
                else:
                    FPS = 20
                    
            if e.key == pygame.K_F12:
                global DEBUG_MODE
                DEBUG_MODE = not DEBUG_MODE
                
    return True
    
def render():
    screen.fill((0, 0, 0))
    
    global scrolly, scroll
    camy = player.y - SCR_H * 0.5
    
    if scrolly < camy - 3 * TILE_H:
        scroll = True
    if scrolly > camy + 3 * TILE_H:
        scroll = True
    
    if scroll:
        if scrolly < camy -2:
            scrolly += 2
        elif scrolly > camy +2:
            scrolly -= 2
        else:
            scroll = False
    
    if scrolly > LEV_H * TILE_H - SCR_H * 0.5:
        scrolly = LEV_H * TILE_H - SCR_H * 0.5

    for y in range(LEV_H):
        for x in range(LEV_W):
            tile = level[y][x]
            
            if tile in tiles:                
                screen.blit(tiles[tile], (x * TILE_W, y * TILE_H - scrolly))
    
    for entity in entities:
        screen.blit(tiles[entity.tile], (entity.x, entity.y - scrolly))
    
    spr = playerSprites[player.facedir][int(tick % 20 / 10)]
    screen.blit(spr, (player.x, player.y - scrolly))

    if DEBUG_MODE:
        global debugList
        for x, y in debugList:
            screen.blit(debugSprite, (x, y - scrolly))
        
    debugList = []

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
    
    clock.tick(FPS)



