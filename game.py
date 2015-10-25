import pygame, sys, os
from pygame.locals import *

#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def on_ground(panda, platform):
    panda_rect = panda.curr_rect
    tiles = platform.tiles
    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            if panda_rect.colliderect(tiles[i][j].rect) and tiles[i][j].is_ground:
                return True
    return False
    

#classes for our game objects
class Panda(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        self.x = 0
        self.y = 160
        self.curr_rect = self.rect
        self.jumping = False
        self.vely = -10
        self.max_jump = 200
        self.go_down = False
        self.falling = False
    def handle_keys(self,platform):
        key = pygame.key.get_pressed()
        dist = 5
        on_ground(self,platform)
        if key[K_SPACE]:
            self.jumping = True
            self.max_jump = 100
        elif key[K_RIGHT]:
            if self.x < 390:            
                recta = Rect(self.x + dist, self.y, self.rect.width, self.rect.height)  
                if self.is_valid_move(platform,recta):
                    self.x += dist
        elif key[K_LEFT]:
            if self.x > 0:
                recta = Rect(self.x - dist, self.y, self.rect.width, self.rect.height)
                if self.is_valid_move(platform, recta):
                    self.x -= dist
        #elif not any(key):
        if not on_ground(self, platform) and not self.jumping:
            self.jumping = True
            self.vely = 0
        if self.jumping:
            self.y += self.vely
            self.vely += 1
            if on_ground(self,platform):
                self.jumping = False
                self.vely = -10
        self.curr_rect = Rect(self.x,self.y,self.rect.width,self.rect.height)
    
    def is_valid_move(self, platform, recta):
        walls = platform.walls     
        for w in walls:
            if recta.colliderect(w.rect):
                return False
        return True

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

class Tile(object):
    def __init__(self, x, y, height, is_ground):
        self.x = x
        self.y = y
        self.height = height
        self.is_ground = is_ground
        self.rect = Rect(x, y, height, height)

    def draw(self, surface):
        ground_color = ( 50, 250, 50)
        sky_color = (135, 206, 250)      
        if self.is_ground:        
            pygame.draw.rect(surface, ground_color, (self.x, self.y, self.height, self.height))
        elif not self.is_ground:
            pygame.draw.rect(surface, sky_color, (self.x, self.y, self.height, self.height)) 
        
        
class Platform(object):
    def __init__(self):
        self.ground_color = ( 0, 255, 0)
        self.sky_color = (135, 206, 256)
        self.x = 0
        self.y = 240
        self.width = 400
        self.height = 20
        self.rows = 400/20
        tiles =[]
        for i in range(15):
            row = []            
            for j in range(20):
                tile = Tile(j*20, i*20, 20, False)                
                row.append(tile)
            tiles.append(row)
        for i in range(12,15):
            for j in range(20):
                tiles[i][j].is_ground = True
        for i in range(12,14):
            for j in range(10,15):
                tiles[i][j].is_ground = False
        
        self.tiles = tiles
        self.walls = self.get_walls()
        #print [(w.x, w.y) for w in self.walls]
    
    def get_walls(self):
        tiles = self.tiles
        walls = set()
        for i in range(len(tiles)):
            for j in range(len(tiles[i])):
                if tiles[i][j].is_ground:
                    if  j>0:
                        if not tiles[i][j-1].is_ground:
                            walls.add(tiles[i][j])
                    if j < len(tiles[i])-1:
                        if not tiles[i][j+1].is_ground:
                            walls.add(tiles[i][j])
        return walls
                    
   
    def draw(self, surface):
        tiles = self.tiles
        for i in range(len(tiles)):
            for j in range(len(tiles[i])):        
                tiles[i][j].draw(surface)

def main():
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((400, 300),0 , 32)
    pygame.display.set_caption('Ilyssa Panda Game!')
    pygame.key.set_repeat(500,30)
    panda = Panda()
    platform = Platform()

    background = pygame.Surface(DISPLAYSURF.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    
    DISPLAYSURF.blit(background, (0, 0))
    pygame.display.flip()
    clock = pygame.time.Clock()
    pygame.time.set_timer(10,60)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            panda.handle_keys(platform)
        DISPLAYSURF.blit(background, (0, 0))
        platform.draw(DISPLAYSURF)        
        panda.draw(DISPLAYSURF)
        pygame.display.flip()

if __name__ == '__main__': main()
