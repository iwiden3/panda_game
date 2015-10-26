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


#classes for our game objects
class Panda(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        self.rect.x = 0
        self.rect.y = 160
        self.jumping = False
        self.vely = -10

    def handle_keys(self, platform):
        key = pygame.key.get_pressed()
        dist = 5
        if key[K_SPACE]:
            self.jumping = True
        elif key[K_RIGHT]:
            if self.rect.x < platform.width - self.rect.width:            
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
                self.vely = -10
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

    def draw(self, surface, items):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        self.items_collision(items)

class Tile(object):
    def __init__(self, x, y, length, is_ground):
        self.x = x
        self.y = y
        self.length = length
        self.is_ground = is_ground
        self.rect = Rect(x, y, length, length)

    def draw(self, surface):
        ground_color = (50, 250, 50)
        sky_color = (135, 206, 250)      
        if self.is_ground:        
            pygame.draw.rect(surface, ground_color, (self.x, self.y, self.length, self.length))
        elif not self.is_ground:
            pygame.draw.rect(surface, sky_color, (self.x, self.y, self.length, self.length)) 
        
        
class Platform(object):
    def __init__(self):
        self.x = 0
        self.y = 240
        self.tile_length = 20
        self.width = 400
        self.height = 300
        self.rows = self.height/self.tile_length
        self.cols = self.width/self.tile_length
        tiles =[]
        for i in range(self.rows):
            row = []            
            for j in range(self.cols):
                tile = Tile(j*self.tile_length, i*self.tile_length, self.tile_length, False)                
                row.append(tile)
            tiles.append(row)
        for i in range(12, 15):
            for j in range(20):
                tiles[i][j].is_ground = True
        for i in range(12, 14):
            for j in range(10, 15):
                tiles[i][j].is_ground = False
        
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
                       
    def draw(self, surface):
        tiles = self.tiles
        for i in range(len(tiles)):
            for j in range(len(tiles[i])):        
                tiles[i][j].draw(surface)

def main():
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((400, 300), 0 , 32)
    pygame.display.set_caption('Ilyssa Panda Game!')
    pygame.key.set_repeat(500, 30)
    panda = Panda()
    platform = Platform()
    coinImg = 'data/coin.png'
    
    items = pygame.sprite.Group()
    coin = Item(100, 218, {'coin':1}, coinImg)
    items.add(coin)
    pygame.display.flip()
    clock = pygame.time.Clock()
    pygame.time.set_timer(10, 60)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            panda.handle_keys(platform)

        platform.draw(DISPLAYSURF)        
        panda.draw(DISPLAYSURF, items)
        items.draw(DISPLAYSURF)
        pygame.display.flip()

if __name__ == '__main__': main()
