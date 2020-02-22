from __future__ import division

import pygame
import io
import random

from bitmapfont import BitmapFont

import os


SCR_W = 320
SCR_H = 176

WIN_W = 1280
WIN_H = 720

TILE_W = 16
TILE_H = 16

FPS = 60

FULLSCREEN = False

DEBUG_MODE = False

JOY_DEADZONE = 0.4

NUM_TOOLS = 9


STATE_GAME = 0
STATE_GAMEOVER = 1


state = STATE_GAME
statecnt = 0




pygame.display.init()

if FULLSCREEN:
    window = pygame.display.set_mode(pygame.display.list_modes()[0], pygame.FULLSCREEN)
else:
    window = pygame.display.set_mode((WIN_W, WIN_H), 0)

screen = pygame.Surface((SCR_W, SCR_H))

clock = pygame.time.Clock()

pygame.mixer.init(44100)
pygame.joystick.init()

for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()
    
pygame.mouse.set_visible(False)

font = BitmapFont('gfx/heimatfont.png', scr_w=SCR_W, scr_h=SCR_H, colors=[(255,255,255), (240,0,240)])


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



def load_level(path):
    file =io.open(path,"r")
    lvl =file.read().splitlines()
    file.close()
    
    return lvl


LEV_W = len(level[0])
LEV_H = len(level)

entities = []
collectibles = []
particles = []

debugList = []

scrolly = 0
scroll = False

score = 0
playtime = 90 * FPS
haswon = False

player = None

lu_bg_tiles =   [' ','.',',']
lu_wall_tiles = ['#','-','=']

tiles = {'#': pygame.image.load('gfx/wall.png'),
         ' ': pygame.image.load('gfx/background.png'),
         '.': pygame.image.load('gfx/background_2.png'),
         ',': pygame.image.load('gfx/background_4.png'),
         '-': pygame.image.load('gfx/floor.png'),
         '=': pygame.image.load('gfx/floor_2.png'),
         'D': pygame.image.load('gfx/door.png'),
         'H': pygame.image.load('gfx/stairs.png'),
         'L': pygame.image.load('gfx/lamp_1.png'),
         'U': pygame.image.load('gfx/lamp_2.png'),
         'R': pygame.image.load('gfx/rat.png'),
         'S': pygame.image.load('gfx/spider.png'),
         "BOX":pygame.image.load('gfx/box.png'),
         'BUBBLE': pygame.image.load('gfx/bubble.png'),
         
         'TOOL1': pygame.image.load('gfx/tool_1.png'),
         'TOOL2': pygame.image.load('gfx/tool_2.png'),
         'TOOL3': pygame.image.load('gfx/tool_3.png'),
         'TOOL4': pygame.image.load('gfx/tool_4.png'),
         'TOOL5': pygame.image.load('gfx/tool_5.png'),
         'TOOL6': pygame.image.load('gfx/tool_6.png'),
         'TOOL7': pygame.image.load('gfx/tool_7.png'),
         'TOOL8': pygame.image.load('gfx/tool_8.png'),
         'TOOL9': pygame.image.load('gfx/tool_9.png'),
         }
         
music = pygame.mixer.Sound('snd/music.wav')
music.play(-1)

sfx = {'jump': pygame.mixer.Sound('snd/sfx-jump.wav'),
       'collect': pygame.mixer.Sound('snd/sfx-collect.wav'),
       'repair': pygame.mixer.Sound('snd/sfx-repair.wav'),
       'drop': pygame.mixer.Sound('snd/sfx-drop.wav'),
       }
         
         
#tiles['BUBBLE'].convert_alpha()
#tiles['BUBBLE'].set_alpha(50)
         
OBSTACLES = ['#', '-', '=']
CLIMBABLE = ['H']


TOOL_ORDER = list(range(NUM_TOOLS +1))
random.shuffle(TOOL_ORDER)
TOOL_ORDER.remove(0)

toolno = 0


playerSprites = [(pygame.image.load('gfx/player_left_1.png'), pygame.image.load('gfx/player_left_2.png')),
                 (pygame.image.load('gfx/player_right_1.png'), pygame.image.load('gfx/player_right_2.png')),
                 (pygame.image.load('gfx/player_up_1.png'), pygame.image.load('gfx/player_up_2.png')),
                 (pygame.image.load('gfx/player_down_1.png'), pygame.image.load('gfx/player_down_2.png')),
                 ]
                 
ratSprites = [pygame.image.load('gfx/rat_1.png'), pygame.image.load('gfx/rat_2.png')]

spiderSprites = [pygame.image.load('gfx/spider_1.png'), pygame.image.load('gfx/spider_2.png')]

debugSprite = pygame.image.load('gfx/debug.png')

    
def toggleFullscreen():
    global FULLSCREEN, window
    FULLSCREEN = not FULLSCREEN
    if FULLSCREEN:
        window = pygame.display.set_mode(pygame.display.list_modes()[0], pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode((WIN_W, WIN_H), 0)



LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3

levelBuffers = []



class GameObject():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self.xdir = 0
        self.ydir = 0
        self.facedir = LEFT
        
        self.speed = 2
        self.gravity = 2
        
        self.jump = False
        self.jumpBlocked = False

        self.width = TILE_W
        self.height = TILE_H
        
        self.tile = None
        
    def getSprite(self):
        return tiles[self.tile]
        
    def moveLeft(self):
        self.xdir = -1
        
    def moveRight(self):
        self.xdir = 1
        
    def moveUp(self):
        self.ydir = -1
        
    def moveDown(self):
        self.ydir = 1
        
    def doJump(self):
        if not self.jumpBlocked:# and not self.climb:
            self.ydir = -4
            self.jumpBlocked = True
            self.jump = True
            
            sfx['jump'].play()
        
    def stopLeft(self):
        if self.xdir < 0:
            self.xdir = 0
        
    def stopRight(self):
        if self.xdir > 0:
            self.xdir = 0
        
    def stopUp(self):
        if self.ydir < 0:
            self.ydir = 0
        
    def stopDown(self):
        if self.ydir > 0:
            self.ydir = 0
        
    def cancelJump(self):
        pass
        
    def update(self):
        pass

    def interact(self):
        pass

    def collides(self,game_object):
        if self.x < game_object.x + game_object.width and \
            self.x + self.width > game_object.x and \
            self.y < game_object.y + game_object.height and \
            self.y + self.height > game_object.y:

           debugList.append([self.x,self.y])
           debugList.append([game_object.x,game_object.y])

           return True
        return False        
        
class Player(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self,x, y)
        
        self.climb = False
        self.objects=[]

        self.remove_timer = 0
        self.max_objects = 7
    
    def interact(self):
        print("Trying to interact...")
        for collectible in collectibles:
            
            if isinstance(collectible, Collectible) and collectible.collides(self) and len(self.objects)<=self.max_objects:
                if (self.objects and self.objects[-1].item_type != collectible.item_type) or not self.objects:
                    self.objects.append(Collected(self.x+8,self.y+8,collectible.item_type))
                
                sfx['collect'].play()
                
            elif isinstance(collectible, RepairPoint) and collectible.collides(self):
                for collected in self.objects:
                    if collected.item_type == collectible.item_type :
                        print("increasing score")
                        global score
                        score += 1
                        print("removing item")
                        self.objects.remove(collected)
                        print("restart quest")
                        collectible.reinit()
                        
                        #global playtime
                        #playtime += 15 * FPS
                        
                        sfx['repair'].play()
                        return
                
        pass

    def remove_item(self,idx=-1):
        if len(self.objects)>0  and self.remove_timer == 0:
            o = self.objects.pop(idx)
            self.remove_timer = 25
            
            sfx['drop'].play()
            
            return o
            
        return None

    def collides_box(self,entity):
        for box in self.objects:
            if box.collides(entity) != False:
                return (True,self.objects.index(box))
        return (False,None)

    def update(self):
        if self.remove_timer >0:
            self.remove_timer-=1

        if self.xdir < 0:
            self.facedir = LEFT
        elif self.xdir > 0:
            self.facedir = RIGHT
            
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
        #debugList.append((x1 * TILE_W, y1 * TILE_H))
        #debugList.append((x2 * TILE_W, y1 * TILE_H))
        #debugList.append((x1 * TILE_W, y2 * TILE_H))
        #debugList.append((x2 * TILE_W, y2 * TILE_H))

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
        
        # vertical collision
        if self.climb:
            gravity = 0
        else:
            gravity = self.gravity
            
            
        #newxdir = self.xdir * self.speed
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

        #debugList.append((x1 * TILE_W, y1 * TILE_H))
        #debugList.append((x2 * TILE_W, y1 * TILE_H))
        #debugList.append((x1 * TILE_W, y2 * TILE_H))
        #debugList.append((x2 * TILE_W, y2 * TILE_H))
        
        if self.ydir + gravity < 0:
            if colltile1 in OBSTACLES and colltile2 in OBSTACLES:
                newydir = 0
            elif colltile1 in OBSTACLES and colltile2 not in OBSTACLES:
                newydir = 0
                newxdir = 1
            elif colltile1 not in OBSTACLES and colltile2 in OBSTACLES:
                newydir = 0
                newxdir = -1
        elif self.ydir + gravity > 0:
            self.jumpBlocked = True
        
            # check if player stands on top of ladder
            if colltile3 in CLIMBABLE or colltile4 in CLIMBABLE:
                if self.ydir == 0:
                    newydir = 0         # defy gravity
                    self.jumpBlocked = False
            else:
                if colltile3 in OBSTACLES and colltile4 in OBSTACLES:
                    newydir = 0
                    self.jumpBlocked = False
                elif colltile3 in OBSTACLES and colltile4 not in OBSTACLES:
                    newydir = 0
                    self.jumpBlocked = False
                elif colltile3 not in OBSTACLES and colltile4 in OBSTACLES:
                    newydir = 0
                    self.jumpBlocked = False

        self.y += newydir
        
        newx = self.x + newxdir
        
        # collision with screen bounds (left/right)
        if newx < 0:
            newx = 0
        elif newx > SCR_W - TILE_W:
            newx = SCR_W - TILE_W

        self.x = newx
        
        # climb
        if not self.jump:
            if colltile1 in CLIMBABLE or colltile2 in CLIMBABLE or colltile3 in CLIMBABLE or colltile4 in CLIMBABLE:
                if self.ydir != 0:
                    self.climb = True
                    
                    if self.ydir < 0:
                        self.facedir = UP
                    elif self.ydir > 0:
                        self.facedir = DOWN
            else:
                self.climb = False
            
        if not self.climb and not self.jump:
            if self.ydir < 0:
                self.ydir = 0
            
        # jump
        if self.jump:
            if self.ydir < 0:
                self.ydir += 0.25
            else:
                self.jump = False
            

class Spider(GameObject):

    def _find_nearest_ceil(self):
        for search_y in range(int(round(self.y/TILE_H)),0,-1):
                      
            if level[search_y][int(self.x/TILE_W)] in lu_wall_tiles:
                self.ceil = search_y
                return
        
    def getSprite(self):
        return spiderSprites[int(tick % 20 / 10)]


    def __init__(self,x,y):
        GameObject.__init__(self,x,y)
        self.dir = "down"
        self.tile = "S"

        self.wait_frames = 0

        self.speed = 1
        self.flip = False
        self.ceil = 0

        self.stole_chest = False

        self._find_nearest_ceil()

    def update(self):

        if player.collides(self) and not self.stole_chest:
            item =player.remove_item()
            self.dir = "up"

            
            if item is not None:
                global particles
                p = Particle(player.x, player.y - TILE_H, item.item_type)
                particles.append(p)


        else:
            result = player.collides_box(self)
            if result[0] and not self.stole_chest:
                self.dir = "up"
                item = player.remove_item(result[1])

                if item:
                    self.stolen_type = item.item_type
                    self.stole_chest = True
            

        

        if self.dir == "down":
            if level[int(round(self.y / TILE_H + self.speed))][int(self.x / TILE_W)] in lu_bg_tiles: 
                self.y+=self.speed
            else:
                self.dir = "up"
                
        elif self.dir == "up":
            debugList.append((self.x,self.y-self.speed))

            debugList.append((self.x,int((self.y-self.speed-0.5*TILE_H)/TILE_H)*TILE_H))
            if level[int(round((self.y-self.speed-0.5*TILE_H)/TILE_H))][int(self.x / TILE_W)] in lu_bg_tiles: 
                self.y-=self.speed * 0.5
            else:
                self.dir = "wait"
                self.wait_frames = 40
                
        elif self.dir ==  "wait":
            if self.wait_frames == 0 :
                self.dir= "down"
            else:
                self.wait_frames-=1
                self.stole_chest = False

        #print((self.x,self.y),(self.x,self.ceil*TILE_H))
        


class Rat(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self,x, y)
        self.xdir = -1
        self.speed = 1.5
        self.flip = False
        
    def getSprite(self):
        return ratSprites[int(tick % 10 / 5)]
    
    def update(self):
        if player.collides(self):
            o = player.remove_item()
            
            if o is not None:
                global particles
                p = Particle(player.x, player.y - TILE_H, o.item_type)
                particles.append(p)


        debugList.append((self.x,self.y))
        
        
        x_new = self.x+self.speed*self.xdir

        debugList.append(( int(round(x_new/TILE_W))*TILE_W,self.y))
        #check boundaries left and right
        if x_new >0 and x_new<SCR_W-TILE_W:
            
            

            debugList.append((int(round((x_new+(0.5*self.xdir))/TILE_W))*TILE_W,int(self.y/TILE_H)*TILE_H))

            #check the tile in the walking direction
            if level[int(round(self.y/TILE_H))][int((x_new+(0.5*self.xdir))/TILE_W)] not in ["#","-"] and level[int(self.y/TILE_H)+1][int((x_new+(0.5*self.xdir))/TILE_W)] not in lu_bg_tiles:

                self.x+=(self.speed*self.xdir)
            else:
                self.xdir*=-1
                self.flip= not self.flip
        else:
            self.xdir*=-1
            self.flip= not self.flip

        pass

class Collectible(GameObject):
    def __init__(self,x,y,item_type=None):
        GameObject.__init__(self,x,y)
        self.stack_size = 0
        self.item_type = item_type or "BOX"
        

class Collected(GameObject):
    def __init__(self,x,y,item_type=None):
        GameObject.__init__(self,x,y)

        self.item_type = item_type or "BOX"

        self.width = 16
        self.height = 16
        

class Particle(GameObject):
    def __init__(self,x,y,item_type=None):
        GameObject.__init__(self,x,y)

        self.item_type = item_type or "BOX"

        self.width = 16
        self.height = 16
        
        self.cnt = 0
        
        self.xdir = -1 if self.x > SCR_W / 2 else 1
        
    def update(self):
        self.x += self.xdir
        self.y += 1
        
        self.cnt += 1


class RepairPoint(GameObject):
    def __init__(self,x,y,item_type=None):
        GameObject.__init__(self,x,y)
        
        self.timer = 1
        self.item_type = None
        self.height = 32

    def update(self):
        self.timer -= 1
        
        if self.timer == 0:
            self.item_type = 'TOOL%i' % int(random.random() * NUM_TOOLS +1)

    def reinit(self):
        self.timer = int(random.random() * 20*FPS) + 2*FPS
        self.item_type = None

def get_entities(level):
    tmp_entities =[]
    tmp_objects = []
    
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
            elif char == "O":
                tmp_objects.append(Collectible(x*TILE_H,y*TILE_H))

                tmp_str =list(level[y])
                tmp_str[x]=" "
                level[y]="".join(tmp_str)
            elif char == "D":
                tmp_objects.append(RepairPoint((x+0.0)*TILE_W, (y-1.5)*TILE_H))
                
            x+=1
        
        y+=1
    
    return tmp_entities,tmp_objects
        

def setState(s):
    global state, statecnt
    state = s
    statecnt = 0


def count_tools():
    count = 0
    for c in collectibles:
        if not isinstance(c, RepairPoint):
            count += 1
    return count
    
def distribute_tools():
    toolno = 0
    for c in collectibles:
        if not isinstance(c, RepairPoint):
             c.item_type = 'TOOL%i' % TOOL_ORDER[toolno]
             toolno += 1

levels=[]
levelno = 0


def load_all_levels():
    global levels
    levels = []
    
    for root,folders,files in os.walk("./lvl"):
        for file in files:
            idx= file.find(".lvl")
            if idx != -1:
                print(file[:idx])
                level = load_level(os.path.join("./lvl",file))
                levels.append(level)
            
    #random.shuffle(levels)


def prerenderLevel():
    global level
    global levelBuffers
    
    levelBuffers = []
    
    for i in range(int(LEV_H * TILE_H / SCR_H) +1):
        levelBuffers.append(pygame.Surface((SCR_W, SCR_H)))

    for y in range(LEV_H):
        bufferno = int((y * TILE_H) / SCR_H)
        buffer = levelBuffers[bufferno]
    
        for x in range(LEV_W):
            tile = level[y][x]
            
            if tile in tiles:     
                buffer.blit(tiles[tile], (x * TILE_W, (y - bufferno * int(SCR_H / TILE_H)) * TILE_H))


def init():
    setState(STATE_GAME)
    
    load_all_levels()
    global level, LEV_W, LEV_H


    global levelno
    
    if haswon:
        levelno += 1
        if levelno == len(levels):
            levelno = 0
            # TODO game completed

    level = levels[levelno]

    LEV_W = len(level[0])
    LEV_H = len(level)
    
    global entities, collectibles, particles
    entities, collectibles = get_entities(level)
    particles = []
    
    global player
    for e in entities:
        if isinstance(e, Player):
            player = e
            entities.remove(e)
            break
    
    global debugList
    debugList = []

    global scrolly, scroll
    scrolly = 0
    scroll = False

    global score, playtime
    score = 0
    playtime = 90 * FPS
    
    global NUM_TOOLS
    NUM_TOOLS = count_tools()
    
    global TOOL_ORDER, toolno
    TOOL_ORDER = list(range(NUM_TOOLS +1))
    random.shuffle(TOOL_ORDER)
    TOOL_ORDER.remove(0)
    
    distribute_tools()

    toolno = 0
    
    prerenderLevel()


def controls():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            return False
        
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return False
                
            if e.key == pygame.K_a:
                player.doJump()
            if e.key == pygame.K_s:
                player.interact()

            if e.key == pygame.K_LEFT:
                player.moveLeft()
            if e.key == pygame.K_RIGHT:
                player.moveRight()
            if e.key == pygame.K_UP:
                player.moveUp()
            if e.key == pygame.K_DOWN:
                player.moveDown()
                
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
                
            if e.key == pygame.K_a:
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
                
                
        if e.type == pygame.JOYAXISMOTION:
            if e.axis == 0:
                if e.value < -JOY_DEADZONE:
                    player.moveLeft()
                elif e.value > JOY_DEADZONE:
                    player.moveRight()
                else:
                    if player.xdir < 0:
                        player.stopLeft()
                    if player.xdir > 0:
                        player.stopRight()
                        
            if e.axis == 1:
                if e.value < -JOY_DEADZONE:
                    player.moveUp()
                elif e.value > JOY_DEADZONE:
                    player.moveDown()
                else:
                    if player.ydir < 0:
                        player.stopUp()
                    if player.ydir > 0:
                        player.stopDown()
                        
        if e.type == pygame.JOYBUTTONDOWN:
            if e.button == 1:
                player.doJump()
            elif e.button == 0:
                player.interact()
            
        if e.type == pygame.JOYBUTTONUP:
            if e.button == 1:
                player.cancelJump()
                
    return True
    
def render():
    screen.fill((0, 0, 0))
    
    if state == STATE_GAMEOVER:
        if statecnt > 2 * FPS:
            font.centerText(screen, 'TIME IS UP', SCR_H / 2 / font.font_h, fgcolor=(255,255,255))
            return
                
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
    
    if scrolly > LEV_H * TILE_H -SCR_H :
        scroll = False
        scrolly =LEV_H * TILE_H -SCR_H

    screen.blit(levelBuffers[int(scrolly / SCR_H)], (0, -(scrolly % SCR_H)))
    screen.blit(levelBuffers[int(scrolly / SCR_H)+1], (0, -(scrolly % SCR_H) + SCR_H))
    
    for entity in entities:
        if entity.tile == "S":
            pygame.draw.line(screen,(255,255,255),(entity.x+7,entity.y- scrolly),(entity.x+7,(entity.ceil+1)*TILE_H- scrolly))
            if entity.stole_chest:
                print(entity.stolen_type)
                scaled_sprite = pygame.transform.scale(tiles[entity.stolen_type],(16,16))
                screen.blit(scaled_sprite,(entity.x  ,entity.y+TILE_H-scrolly -5))
        
        tile = pygame.transform.flip(entity.getSprite(), entity.flip, False)
        screen.blit(tile, (entity.x, entity.y - scrolly))


    for collectible in collectibles:
        #collectible.collides(player)
        
        if isinstance(collectible, RepairPoint):
            if int(tick % 40 / 20):
                continue
        else:
            screen.blit(tiles['BOX'], (collectible.x, collectible.y - scrolly))
                
        if collectible.item_type is not None:
            screen.blit(tiles[collectible.item_type], (collectible.x, collectible.y - scrolly))


    for particle in particles:
        scaled_sprite = pygame.transform.scale(tiles[particle.item_type],(particle.width,particle.height))
        screen.blit(scaled_sprite, (particle.x, particle.y - scrolly))


    anim_frame = int(tick % 20 / 10)
    for collected_num in range(len(player.objects)):
        player.objects[collected_num].x = player.x
        player.objects[collected_num].y = player.y - player.objects[collected_num].height*(collected_num+1)*0.75 -4


        scaled_sprite = pygame.transform.scale(tiles[player.objects[collected_num].item_type],(player.objects[collected_num].width,player.objects[collected_num].height))
        screen.blit(scaled_sprite,(player.objects[collected_num].x  ,player.objects[collected_num].y-scrolly+anim_frame))

    
    spr = playerSprites[player.facedir][anim_frame]
    screen.blit(spr, (player.x, player.y - scrolly))

    if DEBUG_MODE:
        global debugList
        for x, y in debugList:
            screen.blit(debugSprite, (x, y - scrolly))
        
    debugList = []
    
    font.drawText(screen, 'SCORE: %i' % score, 0, 0, fgcolor=(255,255,255))#, bgcolor=(0,0,0))
    font.drawText(screen, 'TIME: %02i' % (playtime / FPS), 30, 0, fgcolor=(255,255,255))


    if state == STATE_GAMEOVER:
        if int(tick % 20 / 10):
            font.centerText(screen, 'TIME IS UP', SCR_H / 2 / font.font_h, fgcolor=(255,255,255))


def update():

    if state == STATE_GAME:
        player.update()

        global playtime
        if scrolly > player.y - SCR_H:
            playtime -= 1
        
        if playtime == 0:
           setState(STATE_GAMEOVER)
            

    for entity in entities:
        entity.update()

    for collectible in collectibles:
        collectible.update()
        collectible.collides(player)
        
    removeParticles = []
    for particle in particles:
        particle.update()
        
        if particle.cnt > 24:
            removeParticles.append(particle)
            
    for particle in removeParticles:
        particles.remove(particle)
        
    
tick = 0
running = True

init()

while running:
    tick += 1
    
    render()
    
    pygame.transform.scale(screen, window.get_size(), window)
    pygame.display.flip()
    
    cont = controls()
    
    if not cont:
        running = False
        
    update()
    
    statecnt += 1

    if state == STATE_GAMEOVER:
        if statecnt == 3 * FPS:
            init()
            
    clock.tick(FPS)



