import pygame, sys, os, random
from pygame.locals import *
from levels import *

WIN_WIDTH = 400
WIN_HEIGHT = 300
HALF_WIDTH = int(WIN_WIDTH/2)
HALF_HEIGHT = int(WIN_HEIGHT/2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

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
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def on_ground(panda_rect, platform):
    tiles = platform.tiles
    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            if panda_rect.colliderect(tiles[i][j].rect) and tiles[i][j].is_ground:
                return True
    return False

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, image, sound=None):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(image, (20, 20))
        self.rect = self.image.get_rect().inflate(-20, -20)      
        self.rect.x = x
        self.rect.y = y
        self.item_type = item_type
        self.load_sound(sound)

    def load_sound(self, sound):
        if sound != None:
            self.sound = pygame.mixer.Sound(sound)
        else:
            self.sound = None
    
    def play_sound(self):
        if self.sound != None:
            self.sound.play()

    def pick_up(self):
        self.play_sound()
        return self.item_type

    def draw2(self, surface, camera):
        surface.blit(self.image, camera.apply(self))


#classes for our game objects
class Panda(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        self.rect.x = 0
        self.rect.y = 240
        self.jumping = False
        self.vely = -15

    def handle_keys(self, platform):
        key = pygame.key.get_pressed()
        dist = 5
        if key[K_SPACE]:
            self.jumping = True
        elif key[K_RIGHT]:
            if self.rect.x < 800 - self.rect.width:            
                r = Rect(self.rect.x + dist, self.rect.y, self.rect.width, self.rect.height)  
                if self.is_valid_move(platform, r):
                    self.rect.x += dist
        elif key[K_LEFT]:
            if self.rect.x > 0:
                r = Rect(self.rect.x - dist, self.rect.y, self.rect.width, self.rect.height)
                if self.is_valid_move(platform, r):
                    self.rect.x -= dist
        if not on_ground(self.rect, platform) and not self.jumping:
            self.jumping = True
            self.vely = 0
        if self.jumping:
            if on_ground(Rect(self.rect.x, self.rect.y + self.vely, self.rect.width, self.rect.height) , platform):
                self.jumping = False
                self.vely = -15
            else:
                self.rect.y += self.vely            
                self.vely += 1
    
    def is_valid_move(self, platform, rect_panda):
        walls = platform.walls     
        for w in walls:
            if rect_panda.colliderect(w.rect):
                return False
        return True
    
    def items_collision(self, items):
        collision_list = pygame.sprite.spritecollide(self, items, True)
        for collision in collision_list:
            item = collision.pick_up()

    def draw(self, surface, camera, items):
        surface.blit(self.image, camera.apply(self))
        self.items_collision(items)

class Tile(object):
    def __init__(self, x, y, length, is_ground):
        self.length = length
        self.is_ground = is_ground
        self.rect = Rect(x, y, length, length)

    def draw(self, surface, rect):
        ground_color = (50, 250, 50)
        sky_color = (135, 206, 250)      
        if self.is_ground:        
            pygame.draw.rect(surface, ground_color, rect)
        elif not self.is_ground:
            pygame.draw.rect(surface, sky_color, rect) 
        
class Platform(object):
    def __init__(self):
        self.tile_length = 20
        tiles =[]
        for i in range(len(level1)):
            row = []            
            for j in range(len(level1[i])):
                 if level1[i][j] == "1":
                    tile = Tile(j*self.tile_length, i*self.tile_length, self.tile_length, True)
                 else:
                    tile = Tile(j*self.tile_length, i*self.tile_length, self.tile_length, False)            
                 row.append(tile)
            tiles.append(row)         
        self.tiles = tiles
        self.walls = self.get_walls()
    
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
                       
    def draw(self, surface, camera):
        tiles = self.tiles
        for i in range(len(tiles)):
            for j in range(len(tiles[i])):
                tiles[i][j].draw(surface,camera.apply(tiles[i][j]))

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l + HALF_WIDTH, -t+HALF_HEIGHT, w, h
    l = min(0, l)
    l = max(-(w-WIN_WIDTH), l)
    t = max(-(h-WIN_HEIGHT), t)
    t = min(0, t)
    return Rect(l, t, w, h)

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.rect = Rect(0,0, width, height)

    def apply(self, target):
        return target.rect.move(self.rect.topleft)
    
    def update(self, target):
        self.rect = self.camera_func(self.rect, target.rect) 

def get_coins(platform):
    coinImg = 'data/coin.png'
    items = pygame.sprite.Group()
    for i in range(10):
        #x = random.randint(0,platform.width)
        x = 100
        y = random.randint(400,450)
        coin = Item(x, y, {'coin':1}, coinImg)
        items.add(coin)
    return items

def main():
    global cameraX, cameraY
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode(DISPLAY, 0 , 32)
    pygame.display.set_caption('Ilyssa Panda Game!')
    pygame.key.set_repeat(500, 30)
    panda = Panda()
    platform = Platform()
    items = get_coins(platform)
    pygame.display.flip()
    clock = pygame.time.Clock()
    pygame.time.set_timer(10, 60)
    total_level_width = len(level1[0])*20
    total_level_height = len(level1)*20
    camera = Camera(complex_camera, total_level_width, total_level_height)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            panda.handle_keys(platform)
        camera.update(panda)
        platform.draw(DISPLAYSURF, camera)        
        panda.draw(DISPLAYSURF, camera, items)
        for item in items:        
            item.draw2(DISPLAYSURF, camera)
        pygame.display.flip()

if __name__ == '__main__': main()
