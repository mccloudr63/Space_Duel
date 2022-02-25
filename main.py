import pygame
import os
import random

pygame.font.init() #initialize font
pygame.mixer.init() #initialize sound 

WIDTH, HEIGHT = 1200, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("First Game!")

#Timing Values
FPS = 60
VEL = 3
BULLET_VEL = 10
POWERUP_VEL = 2
FLASHING_TEXT_INTERVAL = 5
POWERUP_SPAWN_RATE = 300
# POWERUP_SPAWN_RATE = 10
EXPLOSION_LIFE = 50

#COLORS
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255, 255, 0)
GREEN = (0,255,0)
BLUE = (0,0,255)
INDIGO = (20,10,40)
ORANGE = (255, 165, 0)

#Dimensions
SHIP_WIDTH, SHIP_HEIGHT = 50, 45
POWERUP_WIDTH, POWERUP_HEIGHT = 32,32
SHIELD_WIDTH, SHIELD_HEIGHT = SHIP_WIDTH, SHIP_HEIGHT
EXPLOSION_SCALE = 150

#SPRITE RECTS
YELLOW_RECT = pygame.Rect(300, 400, SHIP_WIDTH, SHIP_HEIGHT)
RED_RECT = pygame.Rect(900, 400, SHIP_WIDTH, SHIP_HEIGHT)

#PLAYERS SPRITES
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets','spaceship_yellow.png'))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT)), 90)
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets','spaceship_red.png'))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT)), 270)

#OTHER IMAGE ASSETS
BG_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('Assets','stars_space_dark.jpg')), (WIDTH,HEIGHT))

MULTI_SHOT = pygame.transform.scale(pygame.image.load(os.path.join('Assets','green_times_2.png')),(POWERUP_WIDTH,POWERUP_HEIGHT))
QUICK_SHOT = pygame.transform.scale(pygame.image.load(os.path.join('Assets','quick_shot.png')),(POWERUP_WIDTH,POWERUP_HEIGHT))
EXPLOSIVE_MINE = pygame.transform.scale(pygame.image.load(os.path.join('Assets','explosive_mine.png')),(POWERUP_WIDTH,POWERUP_HEIGHT))
HYPERDRIVE = pygame.transform.scale(pygame.image.load(os.path.join('Assets','hyperdrive.png')),(POWERUP_WIDTH,POWERUP_HEIGHT))
SHIELD = pygame.transform.scale(pygame.image.load(os.path.join('Assets','shield.png')),(POWERUP_WIDTH,POWERUP_HEIGHT))
SHIELD_WALL = pygame.transform.scale(pygame.image.load(os.path.join('Assets','shield_wall.png')),(SHIELD_WIDTH,SHIELD_HEIGHT))

EXPLOSION_1 = pygame.transform.scale(pygame.image.load(os.path.join('Assets','explosion_1.png')),(EXPLOSION_SCALE,EXPLOSION_SCALE))
EXPLOSION_2 = pygame.transform.scale(pygame.image.load(os.path.join('Assets','explosion_2.png')),(EXPLOSION_SCALE,EXPLOSION_SCALE))
EXPLOSION_3 = pygame.transform.scale(pygame.image.load(os.path.join('Assets','explosion_3.png')),(EXPLOSION_SCALE,EXPLOSION_SCALE))
EXPLOSION_4 = pygame.transform.scale(pygame.image.load(os.path.join('Assets','explosion_4.png')),(EXPLOSION_SCALE,EXPLOSION_SCALE))
EXPLOSION_5 = pygame.transform.scale(pygame.image.load(os.path.join('Assets','explosion_5.png')),(EXPLOSION_SCALE,EXPLOSION_SCALE))
EXPLOSION_6 = pygame.transform.scale(pygame.image.load(os.path.join('Assets','explosion_6.png')),(EXPLOSION_SCALE,EXPLOSION_SCALE))

#AUDIO
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Audio', 'Grenade+1.mp3'))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Audio', 'Gun+Silencer.mp3'))
SHIELD_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Audio', 'shield_hit.wav'))
SHIELD_PICKUP_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Audio', 'shield_pickup.mp3'))
RAPID_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Audio', 'rapid_fire.wav'))
MULTI_SHOT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Audio', 'multi_shot.wav'))
HYPERDRIVE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Audio', 'hyperdrive.wav'))
EXPLOSION_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Audio', 'bomb_explosion.wav'))

#Boundries
BORDER_WIDTH = 10
BORDER = pygame.Rect(WIDTH//2-BORDER_WIDTH//2,0,BORDER_WIDTH,HEIGHT)

#TEXT
HEALTH_FONT = pygame.font.SysFont('Ariel', 60)
WINNER_FONT = pygame.font.SysFont('Ariel', 80)
TEXT_PADDING = 15

class Player(pygame.sprite.Sprite):
    def __init__(self, player_surface: pygame.Surface, hp=3, bullet_color=GREEN):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = player_surface
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = hp
        self.health_text = HEALTH_FONT.render("Health: " + str(self.hp), 1, WHITE)
        self.speed = VEL
        self.hyperdrive = False
        self.bullets = []
        self.bullet_width = 10
        self.bullet_height = 4
        self.bullet_color = bullet_color
        self.bullet_multiplier = 1
        self.max_bullets = self.bullet_multiplier * 5
        self.shield = False
        self.rapid_fire = False
        self.rail_shot = False
        self.font_flash = False
        self.flash_frame_count = 0
        self.bomb_hit_list = []

    def take_damage(self):
        if self.shield:
            self.shield = False
            SHIELD_HIT_SOUND.play()
        else:
            BULLET_HIT_SOUND.play()
            self.hp -= 1
            if self.hp < 0: #Insure HP doesn't drop to negatives for display
                self.hp = 0

    def render_flash_effect(self):
        font_color = ORANGE
        if self.hp > 1:
            font_color = WHITE
        elif self.hp <= 0:
            font_color = RED
        elif self.hp == 1 and self.font_flash:
            font_color = RED
        self.flash_frame_count += 1
        if self.flash_frame_count >= FLASHING_TEXT_INTERVAL:
            self.toggle_font_flash()
            self.flash_frame_count = 0
        self.health_text = HEALTH_FONT.render("Health: " + str(self.hp), 1, font_color)

    def toggle_font_flash(self):
        if self.font_flash:
            self.font_flash = False
        else:
            self.font_flash = True

    def hit_by_bomb(self, explosion):
        if explosion in self.bomb_hit_list:
            pass
        else:
            self.take_damage()
            self.bomb_hit_list.append(explosion)

    def shoot(self,ship_center_x,ship_center_y):
        if len(self.bullets) < self.max_bullets:
            BULLET_FIRE_SOUND.play()
            if self.bullet_multiplier == 1:
                bullet = pygame.Rect(ship_center_x,ship_center_y,self.bullet_width,self.bullet_height)
                self.bullets.append(bullet)
            elif self.bullet_multiplier == 2:
                bullet = pygame.Rect(ship_center_x,ship_center_y+SHIP_HEIGHT//2,self.bullet_width,self.bullet_height)
                self.bullets.append(bullet)
                bullet = pygame.Rect(ship_center_x,ship_center_y-SHIP_HEIGHT//2,self.bullet_width,self.bullet_height)
                self.bullets.append(bullet)
            elif self.bullet_multiplier == 3:
                bullet = pygame.Rect(ship_center_x,ship_center_y,self.bullet_width,self.bullet_height)
                self.bullets.append(bullet)
                bullet = pygame.Rect(ship_center_x,ship_center_y+SHIP_HEIGHT//2,self.bullet_width,self.bullet_height)
                self.bullets.append(bullet)
                bullet = pygame.Rect(ship_center_x,ship_center_y-SHIP_HEIGHT//2,self.bullet_width,self.bullet_height)
                self.bullets.append(bullet)

    def reset_shot(self):
        self.bullet_color = GREEN
        self.bullet_multiplier = 1
        self.max_bullets = self.bullet_multiplier * 5
        self.rapid_fire = False
        self.wide_shot = False

    def change_bullet_color(self, rgb):
        self.bullet_color = rgb

    def add_shot(self):
        if self.bullet_multiplier < 3:
            self.bullet_multiplier += 1
            if self.rapid_fire:
                self.max_bullets = self.bullet_multiplier * 15
            else:
                self.max_bullets = self.bullet_multiplier * 5

    def add_shield(self):
        self.shield = True

    def remove_shield(self):
        self.shield = False

    def rapid_fire_on(self):
        self.rapid_fire = True
        self.max_bullets = self.bullet_multiplier * 15
    
    def rapid_fire_off(self):
        self.rapid_fire = False
        self.max_bullets = self.bullet_multiplier * 5        

    def toggle_rapid_fire(self):
        if self.rapid_fire:
            self.rapid_fire_off()
        else:
            self.rapid_fire_on()

    def rail_shot_on(self):
        self.rail_shot = True
    
    def rail_shot_off(self):
        self.rail_shot = False

    def toggle_rail_shot(self):
        if self.rail_shot:
            self.rail_shot_off()
        else:
            self.rail_shot_on()

    def hyperdrive_on(self):
        self.hyperdrive = True
        self.speed = VEL*2

    def hyperdrive_off(self):
        self.hyperdrive = False
        self.speed = VEL

    def toggle_hyperdrive(self):
        if self.hyperdrive:
            self.hyperdrive_off()
        else:
            self.hyperdrive_on()

    def powerup(self,powerup_img):
        if powerup_img == MULTI_SHOT:
            MULTI_SHOT_SOUND.play()
            self.add_shot()
        elif powerup_img == QUICK_SHOT:
            RAPID_FIRE_SOUND.play()
            self.rapid_fire_on()
        elif powerup_img == HYPERDRIVE:
            HYPERDRIVE_SOUND.play()
            self.hyperdrive_on()
        elif powerup_img == SHIELD:
            SHIELD_PICKUP_SOUND.play()
            self.add_shield()
            
class Explosion(pygame.sprite.Sprite):
    def __init__(self, position_x, position_y):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = EXPLOSION_1
        self.rect = pygame.Rect(position_x-EXPLOSION_SCALE//2,position_y-EXPLOSION_SCALE//2,EXPLOSION_SCALE,EXPLOSION_SCALE)
        self.mask = pygame.mask.from_surface(self.image)
        self.position_x = position_x
        self.position_y = position_y
        self.lifetime = 0
        self.scale = 1

    def calculate_image(self):
        frames = [
            EXPLOSION_1,
            EXPLOSION_2, 
            EXPLOSION_3, 
            EXPLOSION_4,
            EXPLOSION_5, 
            EXPLOSION_6 
        ]
        frame_index = self.lifetime % 6
        growth_rate = 6
        self.scale = 1
        if self.lifetime % growth_rate == 1 or self.lifetime % growth_rate == 4:
            self.scale = 1.5
        elif self.lifetime % growth_rate == 2 or self.lifetime % growth_rate == 3:
            self.scale = 2
        self.image = pygame.transform.scale(frames[frame_index],(EXPLOSION_SCALE*self.scale,EXPLOSION_SCALE*self.scale))
        self.rect = pygame.Rect(self.position_x-EXPLOSION_SCALE*self.scale//2,self.position_y-EXPLOSION_SCALE*self.scale//2,EXPLOSION_SCALE,EXPLOSION_SCALE)
        self.mask = pygame.mask.from_surface(self.image)
        return self.image
    
class Space_Game(object):
    def __init__(self):
        self.explosions = pygame.sprite.Group()
        self.game_setup()
        self.main()

    def game_setup(self) -> tuple[Player, Player, pygame.Rect, pygame.Rect, list]: 
        '''Sets both players and their images to their starting values and clears player window of other objects'''
        self.yellow_player = Player(YELLOW_SPACESHIP,bullet_color=YELLOW)
        self.red_player = Player(RED_SPACESHIP,bullet_color=RED)
        self.yellow_player.rect = pygame.Rect(300, 400, SHIP_WIDTH, SHIP_HEIGHT)
        self.red_player.rect = pygame.Rect(900, 400, SHIP_WIDTH, SHIP_HEIGHT)
        self.powerups = [] #Contains powerups formatted as tuple (Surface,list[position_x, position_y])
        # self.explosions = [] #Contains list of explosion sprites
        self.explosions.empty()
        self.asteriods = []

    def handle_yellow_movement(self, keys_pressed):
        if keys_pressed[pygame.K_a]: # LEFT
            self.yellow_player.rect.x -= self.yellow_player.speed
            if self.yellow_player.rect.x < 0:
                self.yellow_player.rect.x = 0
        if keys_pressed[pygame.K_d]: # RIGHT
            self.yellow_player.rect.x += self.yellow_player.speed
            if self.yellow_player.rect.x > BORDER.x - self.yellow_player.rect.height:
                self.yellow_player.rect.x = BORDER.x - self.yellow_player.rect.height
        if keys_pressed[pygame.K_w]: # UP
            self.yellow_player.rect.y -= self.yellow_player.speed
            if self.yellow_player.rect.y < 0:
                self.yellow_player.rect.y = 0
        if keys_pressed[pygame.K_s]: # DOWN
            self.yellow_player.rect.y += self.yellow_player.speed
            if self.yellow_player.rect.y > HEIGHT - self.yellow_player.rect.width:
                self.yellow_player.rect.y = HEIGHT - self.yellow_player.rect.width

    def handle_red_movement(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]: # LEFT
            self.red_player.rect.x -= self.red_player.speed
            if self.red_player.rect.x < BORDER.x + BORDER.width:
                self.red_player.rect.x = BORDER.x + BORDER.width
        if keys_pressed[pygame.K_RIGHT]: # RIGHT
            self.red_player.rect.x += self.red_player.speed
            if self.red_player.rect.x > WIDTH - self.red_player.rect.height:
                self.red_player.rect.x = WIDTH - self.red_player.rect.height
        if keys_pressed[pygame.K_UP]: # UP
            self.red_player.rect.y -= self.red_player.speed
            if self.red_player.rect.y < 0:
                self.red_player.rect.y = 0
        if keys_pressed[pygame.K_DOWN]: # DOWN
            self.red_player.rect.y += self.red_player.speed
            if self.red_player.rect.y > HEIGHT - self.red_player.rect.width:
                self.red_player.rect.y = HEIGHT - self.red_player.rect.width

    def handle_collisions(self):
        #HANDLE BULLET COLLISIONS
        for bullet in self.yellow_player.bullets:
            bullet.x += BULLET_VEL
            if self.red_player.rect.colliderect(bullet):
                self.yellow_player.bullets.remove(bullet)
                self.red_player.take_damage()
            elif bullet.x > WIDTH:
                self.yellow_player.bullets.remove(bullet)
        for bullet in self.red_player.bullets:
            bullet.x -= BULLET_VEL
            if self.yellow_player.rect.colliderect(bullet):
                self.red_player.bullets.remove(bullet)
                self.yellow_player.take_damage()                
            elif bullet.x < 0 - bullet.width:
                self.red_player.bullets.remove(bullet)

        #HANDLE POWERUP COLLISIONS
        for powerup in self.powerups:
            powerup_img,position = powerup
            position[1] += POWERUP_VEL
            powerup_rect = pygame.Rect(position[0],position[1],POWERUP_WIDTH,POWERUP_HEIGHT)
            if self.yellow_player.rect.colliderect(powerup_rect):
                self.powerups.remove(powerup)
                if powerup_img == EXPLOSIVE_MINE:
                    explosion = Explosion(position[0]+POWERUP_WIDTH//2,position[1]+POWERUP_HEIGHT//2)
                    self.explosions.add(explosion)
                    EXPLOSION_SOUND.play()
                else:
                    self.yellow_player.powerup(powerup_img)
            elif self.red_player.rect.colliderect(powerup_rect):
                self.powerups.remove(powerup)
                if powerup_img == EXPLOSIVE_MINE:
                    explosion = Explosion(position[0]+POWERUP_WIDTH//2,position[1]+POWERUP_HEIGHT//2)
                    self.explosions.add(explosion)
                    EXPLOSION_SOUND.play()
                else:
                    self.red_player.powerup(powerup_img)
            elif position[1] > HEIGHT:
                self.powerups.remove(powerup)
            else:
                for bullet in self.yellow_player.bullets:
                    if powerup_rect.colliderect(bullet):
                        if powerup in self.powerups:
                            self.powerups.remove(powerup)
                            self.yellow_player.bullets.remove(bullet)
                            if powerup_img == EXPLOSIVE_MINE:
                                explosion = Explosion(position[0]+POWERUP_WIDTH//2,position[1]+POWERUP_HEIGHT//2)
                                self.explosions.add(explosion)
                                EXPLOSION_SOUND.play()
                            else:
                                self.yellow_player.powerup(powerup_img) 
                for bullet in self.red_player.bullets:
                    if powerup_rect.colliderect(bullet):
                        if powerup in self.powerups:
                            self.powerups.remove(powerup)
                            self.red_player.bullets.remove(bullet)
                            if powerup_img == EXPLOSIVE_MINE:
                                explosion = Explosion(position[0]+POWERUP_WIDTH//2,position[1]+POWERUP_HEIGHT//2)
                                self.explosions.add(explosion)
                                EXPLOSION_SOUND.play()
                            else:
                                self.red_player.powerup(powerup_img)

        # #HANDLE EXPLOSION COLLISIONS
        for explosion in self.explosions:
            if pygame.sprite.spritecollide(self.yellow_player,self.explosions,False,pygame.sprite.collide_mask):
                self.yellow_player.hit_by_bomb(explosion)
            if pygame.sprite.spritecollide(self.red_player,self.explosions,False,pygame.sprite.collide_mask):
                self.red_player.hit_by_bomb(explosion)

    def draw_window(self):
        WIN.blit(BG_IMAGE, (0,0))
        pygame.draw.rect(WIN, INDIGO, BORDER)

        for powerup in self.powerups:
            powerup_img,position = powerup
            WIN.blit(powerup_img,position)

        #Draw bullets
        for bullet in self.yellow_player.bullets:
            pygame.draw.rect(WIN, self.yellow_player.bullet_color, bullet)
        for bullet in self.red_player.bullets:
            pygame.draw.rect(WIN, self.red_player.bullet_color, bullet)

        #Draw Explosions
        for explosion in self.explosions:
            if explosion.lifetime >= EXPLOSION_LIFE:
                self.explosions.remove(explosion)
            else:
                explosion_image = explosion.calculate_image()
                x = explosion.position_x-(EXPLOSION_SCALE*explosion.scale)//2
                y = explosion.position_y-(EXPLOSION_SCALE*explosion.scale)//2
                WIN.blit(explosion_image,(x,y))
                explosion.lifetime += 1

        #Draw player ships
        if self.yellow_player.hp > 0:
            WIN.blit(YELLOW_SPACESHIP, (self.yellow_player.rect.x,self.yellow_player.rect.y))
            if self.yellow_player.shield:
                shield_x = self.yellow_player.rect.x+self.yellow_player.rect.height
                shield_y = self.yellow_player.rect.y+(self.yellow_player.rect.width-SHIELD_WALL.get_height())//2
                WIN.blit(SHIELD_WALL,(shield_x,shield_y))
        if self.red_player.hp > 0:
            WIN.blit(RED_SPACESHIP, (self.red_player.rect.x,self.red_player.rect.y))
            if self.red_player.shield:
                shield_x = self.red_player.rect.x-self.red_player.rect.height
                shield_y = self.red_player.rect.y+(self.red_player.rect.width-SHIELD_WALL.get_height())//2
                WIN.blit(pygame.transform.rotate(SHIELD_WALL,180),(shield_x,shield_y)) #Must rotate image 180 degrees for player facing left

        #Draw Health text
        self.yellow_player.render_flash_effect()
        self.red_player.render_flash_effect()    
        WIN.blit(self.yellow_player.health_text, (WIDTH//4 - self.yellow_player.health_text.get_width()//2,TEXT_PADDING))
        WIN.blit(self.red_player.health_text, (int(WIDTH*.75) - self.red_player.health_text.get_width()//2,TEXT_PADDING))

        pygame.display.update()

    def draw_winner(self,text):
        winner = WINNER_FONT.render(text, 1, WHITE)
        WIN.blit(winner, (WIDTH//2-winner.get_width()//2, HEIGHT//2-winner.get_height()//2))
        pygame.display.update()
        pygame.time.delay(3000) #3 SECOND DELAY

    def main(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL: #Fire yellow
                        self.yellow_player.shoot(self.yellow_player.rect.x+self.yellow_player.rect.height//2, self.yellow_player.rect.y + self.yellow_player.rect.width//2)                    

                    if event.key == pygame.K_RCTRL: #Fire red
                        self.red_player.shoot(self.red_player.rect.x+self.red_player.rect.height//2, self.red_player.rect.y + self.red_player.rect.width//2)                    

            keys_pressed = pygame.key.get_pressed()
            self.handle_yellow_movement(keys_pressed)
            self.handle_red_movement(keys_pressed)
            
            #Spawn random powerup
            if random.randrange(0,POWERUP_SPAWN_RATE) == 0:
                self.powerups.append(spawn_powerup())
            self.handle_collisions()

            self.draw_window()

            winner_text = ''
            if self.yellow_player.hp <= 0:
                winner_text = 'Red Wins!'
            if self.red_player.hp <= 0:
                winner_text = 'Yellow Wins!'
            if winner_text != '':
                self.draw_winner(winner_text)
                self.game_setup()

def spawn_powerup() -> tuple[pygame.Surface, list]:
    powerup_list = [
        MULTI_SHOT,
        QUICK_SHOT,
        EXPLOSIVE_MINE,
        HYPERDRIVE,
        SHIELD
    ]
    position_x = random.randrange(WIDTH//5,int(WIDTH*.80)) #Set spawn area to the middle 3/5ths of the window
    postition = [position_x,0]
    powerup_index = random.randrange(0,len(powerup_list))
    powerup_img = powerup_list[powerup_index] #Get random powerup from list
    return (powerup_img,postition)
  
if __name__ == '__main__':
    game = Space_Game()
    game.main()