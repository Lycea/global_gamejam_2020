import pygame


SCR_W = 320
SCR_H = 176

WIN_W = 1920
WIN_H = 1080

TILE_W = 16
TILE_H = 16

FULLSCREEN = False

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
         '####################',
         ]

LEV_W = len(level[0])
LEV_H = len(level)


tiles = {'#': pygame.image.load('gfx/wall.png'),
         }


spr_guy = pygame.image.load('gfx/guy.png')


    
def toggleFullscreen():
    global FULLSCREEN, window
    FULLSCREEN = not FULLSCREEN
    window = pygame.display.set_mode((WIN_W, WIN_H), pygame.FULLSCREEN if FULLSCREEN else 0)


class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self.xdir = 0
        self.ydir = 0
        
        self.speed = 2
        self.gravity = 2
        
        self.jumpBlocked = False
        
    def moveLeft(self):
        self.xdir = -1
        
    def moveRight(self):
        self.xdir = 1
        
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
        self.ydir = 0
        
    def update(self):
        newx = self.x
        newy = self.y
        
        newx += self.xdir * self.speed
        newy += (self.ydir + self.gravity) * self.speed
        
        if self.ydir < 0:
            self.ydir += 0.125
            
        # collision
        collx = int((newx - TILE_W / 2) / TILE_W)
        colly = int((newy +TILE_H-1) / TILE_H)
        
        if level[colly][collx] == ' ':
            self.y = newy
        else:
            self.jumpBlocked = False

        self.x = newx


player = Player(8 * TILE_W, 9 * TILE_H)

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

    for y in range(LEV_H):
        for x in range(LEV_W):
            tile = level[y][x]
            
            if tile in tiles:
                screen.blit(tiles[tile], (x * TILE_W, y * TILE_H))
    
    screen.blit(spr_guy, (player.x, player.y))
    
def update():
    player.update()
    


running = True

init()

while running:
    render()
    
    pygame.transform.scale(screen, (WIN_W, WIN_H), window)
    pygame.display.flip()
    
    cont = controls()
    
    if not cont:
        running = False
        
    update()
    
    clock.tick(60)



