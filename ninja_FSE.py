#Jack Jiang -ICS3U_FSE

from pygame import *
from os import listdir
from random import *
from math import *
from tkinter import *
import csv, click, sys


init()
root = Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()-50
screen = display.set_mode((width,height))
root.withdraw()
font.init()
mixer.init()

display.set_caption("Ninja storm V.2")
display.set_icon(image.load("icon/icon.jpg"))


#load images
bg = transform.scale(image.load("background/back5.jpg").convert(),(width*1.5,height))
my_menu = transform.scale(image.load("menu_.jpg").convert_alpha(),(width,height))

#level
current_level = 1
ROWS = 20
COL = 150
TILE_SIZE = 36
TILE_TYPE = 10
SPEED = 6
GRAVITY = 0.65
GROUND = height-25
blocks = []
for i in range(4):
    if i != 0:
        blocks.append(transform.scale(image.load(f"brick/bricks00{i+1}.png").convert_alpha(),(TILE_SIZE, TILE_SIZE)))
    else:
        blocks.append(transform.scale(image.load(f"brick/bricks00{i+1}.png").convert_alpha(),(TILE_SIZE * 1.5, TILE_SIZE//2)))

        
    
directories = listdir("collectible")
for x in range(len(directories)):
    blocks.append(transform.scale(image.load(f"collectible/{directories[x]}/p0.png").convert_alpha(),(TILE_SIZE, TILE_SIZE)))



#load different type of bullets
weapons = {
            "fire": transform.scale(image.load("weapons/w_png/p0.png").convert_alpha(),(50,25)),
            "water": transform.scale(image.load("weapons/w_png/p3.png").convert_alpha(),(40,15)),
            "kunai": transform.scale(image.load("weapons/w_png/p1.png").convert_alpha(),(50,20)),
            "star": transform.scale(image.load("weapons/w_png/p2.png").convert_alpha(),(25,25)),
            "waterDragon": transform.scale(image.load("weapons/w_png/p4.png").convert_alpha(),(45,15)),
            "explode": transform.scale(image.load("weapons/w_png/p5.png").convert_alpha(),(50,18)),
            "frog": transform.scale(image.load("weapons/w_png/p6.png").convert_alpha(),(45,45))

           }

#profiles
kakashi_p = transform.scale(image.load("kakashi_p.jpg").convert_alpha(),(45,45))
minato_p = transform.scale(image.load("minato_p.jpg").convert_alpha(),(45,45))
jiraiya_p = transform.scale(image.load("jiraiya_p.jpg").convert_alpha(),(45,45))
kisame_p = transform.scale(image.load("boss.jpg").convert_alpha(),(45,45))

explosion_effect = [transform.scale(image.load("explosion/p"+str(i)+".png").convert_alpha(),(35,35)) for i in range(5) ]

RED = (255,0,0)
GREY =(127,127,127)
BLACK =(0,0,0)
GREEN =(0,255,0)
WHITE = (255,255,255)
BORDER = (220,220,220)


bulletList = []


#matrix for loading world data
worldData = [[ -1 for _ in range(COL) ] for x in range(ROWS)]

#load in the world data in csv file
with open(f"level{current_level}_data.csv", newline = "") as csvfile:
    reader = csv.reader(csvfile, delimiter = ",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            worldData[x][y] = int(tile)


#default character
all_types = ["jiraiya", "kakashi", "minato"]
random_char = choice(range(3))
default = all_types[random_char]
damage = 13

#FPS
FPS = 60
myClock = time.Clock()


#player action variables
moving_left = False
moving_right = False



#skill cooldown
kunaiCoolDown=45


#scrolling variables
SCROLL_LIMIT = 200
screen_scroll = 0   #the individual scroll value of player's opposite movement
bg_scroll = 0 #accumulative value that keeps track of how much the screen has been scrolled


#font
font = font.SysFont("Futura", 26)


#menu
main_menu = True

items = {
    "coin":transform.scale(image.load("collectible/coin/p0.png").convert_alpha(),(TILE_SIZE,TILE_SIZE)),
    "flag":transform.scale(image.load("collectible/flag/p0.png").convert_alpha(),(TILE_SIZE,TILE_SIZE)),
    "headband": transform.scale(image.load("collectible/boss/p0.png").convert_alpha(),(TILE_SIZE,TILE_SIZE)),
    "med":transform.scale(image.load("collectible/medKit/p0.png").convert_alpha(),(TILE_SIZE,TILE_SIZE)),
     }

money = 0

#loading musics and sound effects
mixer.music.load("Naruto.mp3")
mixer.music.set_volume(0.02)
mixer.music.play(-1)
shoot_effect = mixer.Sound("musics/kunai_fx.wav")
jump_effect = mixer.Sound("musics/jump_sound.wav")
explosion_fx = mixer.Sound("musics/explosion_fx.wav")
coin_fx = mixer.Sound("musics/coin.wav")
game_over = mixer.Sound("musics/game_over.wav")
shoot_effect.set_volume(0.01)
jump_effect.set_volume(0.02)
explosion_fx.set_volume(0.01)
coin_fx.set_volume(0.03)
game_over.set_volume(0.05)
death_bgm_played = False
    
def drawText(text, font, content_col, x, y, size):
    image = font.render(text, True, content_col)
    screen.blit(transform.scale(image,(image.get_width()*size, image.get_height()*size)),(x,y))
    
    
def background():
    screen.fill(BLACK)
    width = bg.get_width()
    for j in range(1):
        screen.blit(bg, (j*width - bg_scroll,0))


def restart_level():
    enemy_group.empty()
    bullet_group.empty()
    item_group.empty()
    plat_group.empty()
    scroll_group.empty()
    explode_group.empty()

    #empty world tile list
    world = [[ -1 for _ in range(COL) ] for x in range(ROWS)]

    return world

def help_instruct():
    drawText("Player controls:", font, BLACK, 40,40, 2.5)
    drawText("- Control character's movement by pressing: ", font, BLACK, 50,120, 1.5)
    drawText("- A and D key for moving left and moving right correspondingly", font, BLACK, 50,200, 1.5)
    drawText("- Space bar for jumping", font, BLACK, 50,275, 1.5)
    drawText("- F key for throwing explosive scroll with a maximum amount of 10(refillable by  collecting certain amount of coins)", font, BLACK, 50,355, 1.35)
    drawText("- Shoot kunai by left clicking the mouse", font, BLACK, 50,435, 1.5)
    drawText("- Shoot fire ball by right clicking the mouse", font, BLACK, 50,510, 1.5)
    drawText("Game objective:", font, RED, 40,555, 2.5)
    drawText("Kill all opponents to activate the mysterious Ninja headband for the level's final boss.", font, RED, 55,615, 1.5)
    drawText("Reminder: 10 coins will be automatically exchanged for an additional explosion scroll", font, RED, 55,653, 1.3)
    drawText("Press the ESCAPE KEY to EXIT the current menu", font, (0,0,255), 1040,40, 0.8)

    
class World():
    def __init__(self):
        self.dirts = [] #obstacle list
        self.movable = []

    def data_process(self, data):
        self.level_width = len(data[1])
        #iterate through every value from the data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile > -1:
                    img = blocks[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x* TILE_SIZE 
                    img_rect.y = y* TILE_SIZE
                    data = (img, img_rect)  #dirt tuple that stores the rect&img
                    if tile > 0 and tile < 4:
                        self.dirts.append(data)  #dirts
                    elif tile == 0:
                        self.movable.append(data)
                    elif tile == 8:
                        test = Collectible("flag", x* TILE_SIZE, y* TILE_SIZE)
                        item_group.add(test)
                    elif tile == 6:
                        enemy = Ninja(x * TILE_SIZE, y * TILE_SIZE, 2, 3, "black")
                        enemy_group.add(enemy)
                    elif tile == 7:
                        enemy = Ninja(x * TILE_SIZE, y * TILE_SIZE, 1.5, 3, "white")
                        enemy_group.add(enemy)
                    elif tile == 9:
                        itemBox = Collectible("med", x* TILE_SIZE, y* TILE_SIZE)
                        item_group.add(itemBox)
                    elif tile == 4:
                        boss_pass = Collectible("headband", x* TILE_SIZE, y* TILE_SIZE)
                        item_group.add(boss_pass)                        
                    elif tile == 5:
                        coin = Collectible("coin", x* TILE_SIZE, y* TILE_SIZE)
                        item_group.add(coin)

    def draw(self):
        for tile in self.dirts:
            tile[1][0] += screen_scroll
            screen.blit(tile[0],tile[1])
      
                        


#characters
class Ninja(sprite.Sprite):
    def __init__ (self, x, y, scale, velocity, char_type):
        #inheritance the sprite class
        super().__init__()

        
        self.alive = True
        self.health = 100
        self.max_health = 100
        self.type = char_type
        self.speed = velocity
        self.direction = 1
        self.flip = False
        self.jumping = False
        self.inAir = True
        self.vy = 0
        self.edge = False

        
        img = image.load(f"{self.type}/idle/p1.png").convert_alpha()
        self.image = transform.scale(img, (img.get_width()*scale, img.get_height()*scale))    
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.width = self.width*0.65
        self.rect.topright = (x,y)
        
        


        #player folder
        char_categories = ["idle","run","fight","jump","fireball","throw","seal","summon",
                         "r_run","r_collsion","kick5","kick9","death"]


        kakashi = listdir("kakashi")

        char2_categories=["idle","run","walk","rasen","yin","summon","frog", "death"]

        black_categories = ["idle","run","fight","death"]

        boss = ["idle","run","fight","dead"]

        white = ["idle", "fight", "death"]
        
        #Initial timer
        self.timer = time.get_ticks()

        #cooldown
        self.shootCooldown = 50
        
        #animations
        self.currentAction = 0
        self.inner = 0
        self.animation = []   
        if self.type == "minato":
            for category in char_categories:
               temp_list=[]
               len_folder=len(listdir(f"{self.type}\\{category}"))
               for i in range(len_folder):
                   if category != "run" and category != "jump" and category != "death":
                       temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*scale, img.get_height()*scale)))
                   elif category == "jump":
                       temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*scale *1.5, img.get_height()*scale*1.1)))
                   elif category == "death":
                       temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*4, img.get_height()*1.6)))
                   else:
                       temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*1.7, img.get_height()*1.5)))
               self.animation.append(temp_list)

        elif self.type == "kakashi":
            for category in kakashi:
               temp_list=[]
               len_folder=len(listdir(f"{self.type}\\{category}"))
               for i in range(len_folder):
                   if category != "summon":
                       temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*scale, img.get_height()*scale)))
                       
                   else:
                       temp_list.append(transform.scale(image.load(f"kakashi\\summon\\p{i}.png").convert_alpha(),(img.get_width()*scale, img.get_height()*scale*1.15)))
               self.animation.append(temp_list)


        elif self.type == "black":
             for category in black_categories:
               temp_list=[]
               len_folder=len(listdir(f"{self.type}\\{category}"))
               for i in range(len_folder):
                   temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*scale, img.get_height()*scale)))
               self.animation.append(temp_list)


        elif self.type == "jiraiya":
            for category in char2_categories:
               temp_list=[]
               len_folder=len(listdir(f"{self.type}\\{category}"))
               for i in range(len_folder):
                   if category != "death":
                       temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*scale, img.get_height()*scale)))
                   else:
                       temp_list.append(transform.scale(image.load(f"{self.type}\\death\\p0.png").convert_alpha(),(225, 125)))
               self.animation.append(temp_list)

        elif  self.type == "white":
             for category in white:
               temp_list=[]
               len_folder=len(listdir(f"{self.type}\\{category}"))
               for i in range(len_folder):
                   temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*scale, img.get_height()*scale)))
               self.animation.append(temp_list)


        else:
            for category in boss:
               temp_list=[]
               len_folder=len(listdir(f"{self.type}\\{category}"))
               for i in range(len_folder):
                   if category != "death":
                       temp_list.append(transform.scale(image.load(f"{self.type}\\{category}\\p{i}.png").convert_alpha(),(img.get_width()*scale, img.get_height()*scale)))
                   else:
                       temp_list.append(transform.scale(image.load(f"{self.type}\\death\\p0.png").convert_alpha(),(225, 125)))
               self.animation.append(temp_list)
               
        #Computer player specific variables
        self.counter = 0
        self.idle = False
        self.idle_counter = 50
        self.sight = Rect(0, 0, 250, 15)

        #boss variables
        self.bossidle = False
        self.bossidlecount = 0
        self.bossTimer = 35


        
        
    def draw(self):
         screen.blit(transform.flip(self.animation[self.currentAction][self.inner],self.flip, False),(self.rect.x - 15, self.rect.y))


    def move(self, move_left, move_right):
        #reset movement variables (prediction check for collsions)
        relative_x = 0
        dx = 0
        dy = 0
        
        
        #process the keyboard interactions for the player
        #horizontal movements
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
            
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #Jumping
        if self.jumping and self.inAir == False:
            self.vy = -16
            self.jumping = False
            self.inAir = True


        #apply gravity and vertical velocity
        self.vy += GRAVITY
        if self.vy > 10:
            self.vy = 10
        dy +=self.vy

        for tile in world.dirts:
            #collision inspection in the x-driection
            if tile[1].colliderect(self.rect.x +dx, self.rect.y, self.width, self.height):
                dx = 0
            #collision inspection in the y-direction
            if tile[1].colliderect(self.rect.x, self.rect.y +dy, self.width, self.height):
                #check if below the ground
                if self.vy < 0:
                    self.vy = 0
                    dy = tile[1].bottom - self.rect.top

                #check if above the ground
                elif self.vy >= 0:
                    self.vy = 0
                    dy = tile[1].top - self.rect.bottom
                    self.inAir = False

                    
        for platform in plat_group:
            #collision with moving platform in the x-direction
            if platform.rect.colliderect(self.rect.x +dx, self.rect.y, self.width, self.height):
                dx = 0

            #collision in the y-direction
            if platform.rect.colliderect(self.rect.x, self.rect.y +dy, self.width, self.height):
                #check if below the platform
                if abs((self.rect.top + dy) - platform.rect.bottom) < 13:
                    self.vy = 0
                    dy = platform.rect.bottom - self.rect.top

                #check if above the platform
                elif abs((self.rect.bottom + dy) - platform.rect.top) < 13:
                    self.rect.bottom = platform.rect.top 
                    dy = 0 
                    self.inAir = False

                #move sideways with the platform
                    self.rect.x += platform.move_direction + screen_scroll
                
            
 
    
        if self.rect.bottom + dy > GROUND:
            dy = GROUND - self.rect.bottom
            self.inAir = False

        if self.rect.top + dy < 0:
            self.vt = 0
            dy = 0 - self.rect.top
            self.inAir = False

        if self.type in all_types or self.type == "kisame":
            if self.rect.right + dx > width or self.rect.left + dx< 0:
                dx = 0
                self.edge = True
            else:
                self.edge = False

        #update rectangle pos
        self.rect.x += dx
        self.rect.y += dy


        #update scroll based on user input
        if self.type in all_types:
            if (self.rect.left < SCROLL_LIMIT  and self.rect.left != (width - SCROLL_LIMIT)and bg_scroll > abs(dx) and bg_scroll > 0) or \
               (self.rect.right > (width - SCROLL_LIMIT)  and bg_scroll < 622):
                #keep player stationary
                self.rect.x -= dx   
                relative_x = -dx
        return relative_x
                

    def actions(self,new_action):
        #check if the new animation is diffent then the current animation
        if new_action != self.currentAction:
            #update the new animation
            self.currentAction = new_action
            self.inner = 0
            self.timer = time.get_ticks()
            

    def cooldown_animation(self):
        COOLDOWN_idle = 200
        COOLDOWN_else = 75

        if self.currentAction == 0:
            if time.get_ticks()-self.timer > COOLDOWN_idle:
                self.timer = time.get_ticks()
                self.inner +=1
            
            if self.inner >= len(self.animation[self.currentAction]):
                self.inner = 0

        else:
            if time.get_ticks()-self.timer > COOLDOWN_else:
                self.timer = time.get_ticks()
                self.inner +=1
            
            if self.inner >= len(self.animation[self.currentAction]):
                self.inner = 0
        self.image = self.animation[self.currentAction][self.inner]


    def shoot(self):
        if self.shootCooldown == 50:
           if self.type == "jiraiya":
               bullet = Weapon(self.rect.centerx+self.rect.size[0]*1.1*self.direction, self.rect.centery-25, self.direction, "fire", "player")

               
           elif self.type =="minato":
               bullet = Weapon(self.rect.centerx+self.rect.size[0]*1.1*self.direction, self.rect.centery-35, self.direction, "water", "player")

           elif self.type == "kakashi":
               bullet = Weapon(self.rect.centerx+self.rect.size[0]*self.direction, self.rect.centery-15, self.direction, "waterDragon", "player")

           else:
               bullet = Weapon(self.rect.centerx+self.rect.size[0]*0.9*self.direction, self.rect.centery-35, self.direction, "star", "enemy")

           bullet_group.add(bullet)
           self.shootCooldown = 0
           

    def update(self):
        self.cooldown_animation()
        self.check_alive()

        if self.shootCooldown < 50:
            self.shootCooldown += 1
            

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            if self.type == "kakashi":
                self.actions(0)
            else:
                self.actions(-1)
            
        return self.alive


    def AI(self):
        if player.alive and self.alive:
            if not self.idle and randint(1, 300) == 50:
                self.idle = True
                self.idle_counter = 0
                self.actions(0)#idling
                
            #check for shooting trigger
            if self.sight.colliderect(player.rect):
                self.actions(0) #facing to the player while stop running
                self.shoot()
                
            else:
                if not self.idle:
                    # 1: moving to the right
                    #-1: moving to the left
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.actions(1)#patrolling
                    self.counter += 1

                    #update enemy's vision while moving
                    self.sight.center = (self.rect.centerx + 125*self.direction , self.rect.centery - 10)
                    if self.counter > TILE_SIZE:
                        self.direction *= -1
                        self.counter *= -1
                        
                else:
                    self.idle_counter += 1
                    if self.idle_counter >= 50:
                        self.idle = False

        #scroll
        self.rect.x += screen_scroll


    def bossAI(self):

        self.rect.x += screen_scroll
        if self.alive and player.alive:
            #timer for damage
            if self.bossTimer<35 :
                self.bossTimer+=1
                
            #randomize idling motion
            if randint(1,150) == 20 and self.bossidle == False:
                self.bossidle=True
                self.bossidlecount=15
                
            #check collision
            if self.rect.colliderect(player.rect):
                if self.bossTimer == 35:
                    self.actions(2)
                    player.health -= 15
                    self.bossTimer = 0

            else:
                #basic logic check
                if not self.bossidle:
                    if self.direction==1:
                        boss_moving_right = True
                    else:
                        boss_moving_right = False
                    boss_moving_left = not boss_moving_right
                    self.move(boss_moving_left,boss_moving_right)
                    self.actions(1)
                    self.cooldown_animation()


                    #Boss's running area
                    if self.edge:
                        self.direction *= -1
                        

                #the counter for how long the idling state is going to last
                elif self.bossidle:
                    self.bossidlecount-=1
                    self.actions(0)
                    if self.bossidlecount==0:
                        self.bossidle=False
                        
        #when killed player
        elif self.alive and not player.alive:
            self.actions(0)
            



                        

class Moveplat(sprite.Sprite):
    def __init__(self, platList):
        super().__init__()
        #variables for movable platforms
        self.move_direction = 1
        self.move_count = 0
        self.list = platList
        self.image = blocks[0]
        self.rect = self.list[0][1]
        
        
    def update(self):
        self.rect.x += screen_scroll
        for tile in self.list:
             tile[1].x += self.move_direction
             self.move_count += 1
             if abs(self.move_count) > 50:
                 self.move_direction *= -1
                 self.move_count *= -1

        

    def draw(self):
        screen.blit(self.image,self.rect)  
                 
        



class Weapon(sprite.Sprite):
    def __init__(self, x, y, direction, weapon_index, char_type):
        super().__init__()
        self.speed = 10
        self.direction = direction
        #spriteGroup.draw()-->Must have an varible called image
        self.image = weapons[weapon_index]  
        self.rect = self.image.get_rect()   
        self.rect.center = (x,y)
        self.char_type = char_type


        
    def update(self, instance):
        new_list = []
        self.rect.x += (self.direction * self.speed) + screen_scroll
        
        #move the position of the bullet
        self.image = transform.flip(self.image,instance.flip, False)
       
       #check if the bullet has gone offscreen
        if self.rect.x > width or self.rect.x < 0 :
            self.kill()

       #checking for collision with characters 
        if sprite.spritecollide(player, bullet_group, False) and player.alive:
            self.kill()
            player.health -= 3

        for enemy in enemy_group:
            if sprite.spritecollide(enemy, bullet_group, False) and enemy.alive and self.char_type == "player":
                self.kill()
                enemy.health -= damage
                
        if activated:        
            if sprite.spritecollide(boss, bullet_group, False) and boss.alive and self.char_type == "player":
                self.kill()
                boss.health -= damage*1.3

        #check for collision with the level
        new_list.insert(0, world.movable)
        new_list.insert(-1, world.dirts)
        
        for i in new_list:
            for tile in i:
                if tile[1].colliderect(self.rect):
                    self.kill()
            



class Collectible(sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = items[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (TILE_SIZE//2 + x, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #check if the player has picked the item
        #ONLY check collision against the player
        global damage, activated, money
        counter = 0
        self.rect.x += screen_scroll
        
        if sprite.collide_rect(self, player):
            #check the type of the item
            if self.item_type == "med" and player.health < player.max_health:
                player.health += 20
                if player.health > player.max_health:
                    player.health = player.max_health
                self.kill()

                
            elif self.item_type == "flag" and damage <= 25:
                damage += 3
                self.kill()

            elif self.item_type =="coin":
                money += 5
                coin_fx.play()
                self.kill()


            elif self.item_type == "headband":
                for e in enemy_group:
                    if not e.alive:
                        counter +=1
                if counter == len(enemy_group):
                    self.kill()
                    activated = True

            
                
#Ninja weapon (All direction available)
class Bullet():
    def __init__(self,start_X,start_Y,weaponIndex, enemyRect):
        self.SPEED = 20
        self.startX = start_X #starting x pos
        self.startY = start_Y #starting y pos
        self.index = weaponIndex 
        self.angle = 0  #the angle 
        self.dX = 0     #the change in horizontal direction
        self.dY = 0     #the change in vertical direction
        self.pic = weapons[self.index]  #image with indicated index
        self.rect = self.pic.get_rect()
        self.rect = Rect(self.rect.x +160, self.rect.y +160, 45,45)
        self.rect.topleft= (self.startX,self.startY) 
        self.enemyRect = enemyRect
        self.cur_type = None
        self.hit = False
        self.hitted_enemy = None
        damage = 20
        
        
    def shootBullet(self):
     #calculate the useful data such as the horizontal component of my bullet regards to the cursor and the character
       global bulletList
       self.dist = hypot(mx-self.startX, my-self.startY)    #hypotnuse
       self.angle = atan2(my-self.startY,mx-self.startX)  #angle
       self.dX = cos(self.angle)*self.SPEED  #run
       self.dY = sin(self.angle)*self.SPEED  #rise
       bulletList.append([self.startX, self.startY, self.dX, self.dY, self.angle])
  

    def move(self):
        self.rect.x += screen_scroll
        for i in bulletList[:]:
            i[0]+=i[2] #horizontal component
            i[1]+=i[3] #vertical component
            self.rect[0]+=i[2] #rect's horizontal
            self.rect[1]+=i[3] #rect's vertical
            if i[0] > width or i[0] < 0 or i[1] > height - 50 or i[1] < -10:  #check off-screen
                bulletList.remove(i)


         
        
    def collideBullet(self):
        new_list = []
        movable_rect = world.movable[0][1]
        new_list.append(movable_rect)
        for i in range(len(world.dirts)):
            new_list.append( world.dirts[i][1])
        
        self.hit = False
        for b in bulletList:
            rotpic = transform.rotate(self.pic,-degrees(b[4]))   
            screen.blit(rotpic,(int(b[0]),int(b[1])))
            for e in self.enemyRect:
                if self.rect.colliderect(e.rect) and e.alive:    #check collision between bullet and enemies
                    self.hit = True
                    self.hitted_enemy = e
                    try:
                        bulletList.remove(b)

                    except ValueError:
                        pass
        

        for b in bulletList:
            for tile in new_list:
                if tile.colliderect(self.rect):
                    try:
                        bulletList.remove(b)
                    except Exception:
                        pass

        if activated and boss.alive:
            for b in bulletList:
                if self.rect.colliderect(boss.rect):
                    self.hit = True
                    self.hitted_enemy = boss
                    try:
                        bulletList.remove(b)
                    except Exception:
                        pass


    def damage(self):
          if self.hit:
              self.hitted_enemy.health -= damage

          
              

                       
class Healthbar():
    def __init__(self, x, y, health, max_health, char_type):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.char_type = char_type

    def draw(self, health):
        #update with new health
        self.health = health

        if self.char_type == "enemy":
            draw.rect(screen, BLACK, (self.x - 3, self.y - 3, 106, 9),1)
            draw.rect(screen, RED, (self.x, self.y, 100, 3))
            draw.rect(screen, GREEN,(self.x, self.y, 100 * (self.health/self.max_health), 3))

        else:
            draw.rect(screen, BORDER, (self.x - 3, self.y - 3, 256, 26 ))
            draw.rect(screen, RED, (self.x, self.y, 250, 20))
            #calculate the ratio of the current health
            draw.rect(screen, GREEN,(self.x, self.y, 250 * (self.health/self.max_health), 20))
        
        
                
class Explosive(sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 8
        self.direction = direction
        self.timer = 0
        self.velocity_y = -8
        self.image = items["flag"]
        self.rect = self.image.get_rect()   
        self.rect.center = (x,y)
        self.explosion_radius = TILE_SIZE * 1.5
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
    def update(self):
        new_list = []
        dx = self.direction * self.speed
        self.velocity_y += GRAVITY
        dy = self.velocity_y

        #check collision with the sides of the screen
        if self.rect.right + dx > width or self.rect.left + dx < 0 :
            self.direction *= -1
            dx = self.direction * self.speed

        #check collision with the floor
        if self.rect.bottom + dy > GROUND:
            self.speed = 0
            dy = GROUND - self.rect.bottom

            
        #check for collision with the level
        new_list.insert(0, world.movable)
        new_list.insert(-1, world.dirts)

        for i in new_list:
            for block in i:
                if block[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    self.direction *= -1
                    dx = self.speed * self.direction

                if block[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    self.speed = 0
                    
                    #check for throwing up the way
                    if self.velocity_y < 0:
                        self.velocity_y = 0
                        dy = block[1].bottom - self.rect.top

                    #check for falling
                    elif self.velocity_y > -1:
                        self.velocity_y = 0
                        dy = block[1].top - self.rect.bottom
                        

        
        #update position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy


        #fuels
        self.timer += 1
        if self.timer >= 50:
            self.kill()
            explosion = Explosion(self.rect.x + 20, self.rect.y)
            explode_group.add(explosion)
            
            #Apply damage to everyone who is nearby
            if abs(self.rect.centerx - player.rect.centerx) <= self.explosion_radius \
               and abs(self.rect.centery - player.rect.centery) <= self.explosion_radius:
                player.health -= 22
                
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) <= self.explosion_radius \
               and abs(self.rect.centery - enemy.rect.centery) <= self.explosion_radius:
                    enemy.health -= 33

            if activated:        
                if abs(self.rect.centerx - boss.rect.centerx) <= self.explosion_radius \
                   and abs(self.rect.centery - boss.rect.centery) <= self.explosion_radius:
                    boss.health -= 25





class Explosion(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.speed = 10
        self.timer = 100
        self.velocity_y = -8
        self.image_lis = explosion_effect
        self.ind = 0
        self.image = self.image_lis[self.ind]
        self.rect = self.image.get_rect()   
        self.rect.center = (x,y)
        self.count = 0

    def update(self):
        FRAME_SPEED = 3
        self.rect.x += screen_scroll
        explosion_fx.play()
        
        #update explosion animation
        self.count += 1
        if self.count >= FRAME_SPEED:
            self.ind += 1
            #check whether or not the animation is complete then delete the sprite
            if self.ind >= len(explosion_effect):
                self.kill()
            else:
                self.image = self.image_lis[self.ind]
            self.counter = 0
            


            
#buttons
buttons={
    "start_btn": image.load("buttons/start_btn.png").convert_alpha(),
    "exit_btn": image.load("buttons/exit_btn.png").convert_alpha(),
    "setting_btn": transform.scale(image.load("buttons/setting.png").convert_alpha(),(50,50)),
    "restart_btn": transform.scale(image.load("buttons/restart_btn.png").convert_alpha(),(400,100)),
    "back_btn": transform.scale(image.load("buttons/back_btn.png").convert_alpha(),(250,80)),
    "help_btn": transform.scale(image.load("buttons/help_btn.png").convert_alpha(),(250,80))
    }

start = click.Button(width//2-100,480, buttons["start_btn"], 0.8)
Exit = click.Button(width//2-85,570, buttons["exit_btn"], 0.8)
setting = click.Button(width-55,5 , buttons["setting_btn"] ,1)
restart = click.Button(width//2-100,height//2, buttons["restart_btn"], 0.5)
back = click.Button(width//2-170, height//2+70, buttons["back_btn"], 1)
helps = click.Button(width//2-170, height//2- 150, buttons["help_btn"], 1)
help_instruction = image.load("buttons/help_ins.png")
help_img = image.load("buttons/help_img.png").convert_alpha()
help_img = transform.scale(help_img,(help_img.get_width()*0.2, help_img.get_height()*0.2))
next_btn = transform.scale(image.load("buttons/next_btn.jpg").convert_alpha(),(100,50))
passed = click.Button(width//2 - next_btn.get_width()//2, 0, next_btn,1)

#pygame sprite groups
bullet_group = sprite.Group()
item_group = sprite.Group()
enemy_group = sprite.Group()
plat_group = sprite.Group()
scroll_group = sprite.Group()
explode_group = sprite.Group()
        

        
#character instances

if default != "kakashi":
    player = Ninja(200, 615, 1.5, SPEED, default)
    
else:
    player = Ninja(150, 615, 1.7, SPEED, default)

health_bar = Healthbar(70, 15, player.health, player.health, "player")



#ninja kunai
myBullet = Bullet(player.rect.x + 25, player.rect.y + 45 ,"kunai", enemy_group)
world = World()
world.data_process(worldData)
move_plat = world.movable
platforms = Moveplat(move_plat)
plat_group.add(platforms)


#boss
activated = False
boss = Ninja(1300 , 515, 1.7, 4, "kisame")
button_clicked = False
help_menu = False
shooting = False
running = True
explosive_scroll = False
thrown = False
projectile_amount = 10

while running:
    clicked = False
    #keyboard and mouse inputs
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        if evt.type==MOUSEBUTTONDOWN:
            if evt.button == 1:
                clicked = True
                if clicked and not main_menu and player.alive:
                    shoot_effect.play()
            if evt.button == 3 and not explosive_scroll:
                shooting = True


        if evt.type==MOUSEBUTTONUP:
            if evt.button == 1:
                clicked = False
            if evt.button == 3:
                shooting = False
        
        

        if evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                if help_menu:
                    button_clicked = True
                    help_menu = False
                elif button_clicked:
                    button_clicked = False
                else:
                    if main_menu and not button_clicked and not help_menu:
                        running = False
                    main_menu = True
                        
            if evt.key == K_a and player.alive and boss.alive:
                moving_left = True
            if evt.key == K_d and player.alive and boss.alive:
                moving_right = True
            if evt.key == K_SPACE and player.alive:
                player.jumping = True
                jump_effect.play()
            if evt.key == K_f and player.alive and not shooting and projectile_amount >0:
                explosive_scroll = True
            if evt.key == K_RETURN:
                main_menu = False
            

        if evt.type == KEYUP:
            if evt.key == K_a:
                moving_left = False
            if evt.key == K_d:
                moving_right = False
            if evt.key == K_f:
                explosive_scroll = False
                thrown = False
                projectile_amount -= 1
                if projectile_amount < 0:
                    projectile_amount = 0
            
                
                       
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()


    if main_menu:
        #main menu
        if not button_clicked:
            screen.blit(my_menu, (0,0))
            draw.rect(screen,WHITE, (width - 55,5, buttons["setting_btn"].get_width(), buttons["setting_btn"].get_height()))
            draw.rect(screen,BLACK, (width - 55,5, buttons["setting_btn"].get_width(), buttons["setting_btn"].get_height()),2)
            if start.drawButton(screen):
                main_menu = False
            if Exit.drawButton(screen):
                running = False
            if setting.drawButton(screen):
                button_clicked = True
        else:
            screen.fill(BORDER)
            if helps.drawButton(screen):
                help_menu = True

            elif back.drawButton(screen):
                button_clicked = False
                main_menu = True
                    
            if help_menu:
                screen.fill(BORDER)
                help_instruct()
                screen.blit(help_img,(width - help_img.get_width(),height - help_img.get_height()))
      
        display.update()


    else:
        #game menu
        background()

        #draw obstacles
        world.draw()
        drawText(f"Fireball current damage: {damage}", font, WHITE, 15, 50, 1)
        drawText(f"Kunai temporary cooldown: {kunaiCoolDown}", font, WHITE, 15, 70, 1)
        screen.blit(transform.scale(items["flag"],(25,25)),(10,85))
        drawText(f":{projectile_amount}", font, WHITE, 43, 90,1)
        screen.blit(transform.scale(items["coin"],(25,25)),(10,115))
        drawText(f":{money}", font, WHITE, 43, 115,1)
        if money == 20:
            projectile_amount += 1
            money = 0
        
        #draw characters
        if default == "minato":
            screen.blit(minato_p,(0,0))
            draw.rect(screen, WHITE, (0,0,45,45),3)
        elif default == "kakashi":
            screen.blit(kakashi_p, (0,0))
            draw.rect(screen, WHITE, (0,0,45,45),3)
        else:
            screen.blit(jiraiya_p, (0,0))
            draw.rect(screen, WHITE, (0,0,45,45),3)
            
        player.draw()
        screen_scroll = player.move(moving_left, moving_right)
        bg_scroll -= screen_scroll
        player.update()
        health_bar.draw(player.health)


        if activated:
            boss.draw()
            boss.update()
            boss.bossAI()
            screen.blit(kisame_p,(width - kisame_p.get_width(),0))
            draw.rect(screen, BLACK, (width - kisame_p.get_width(),0,45,45),3)
            if boss.health >= 40:
                 drawText("Current health: "+ str(round(boss.health,0)), font, GREEN, width - kisame_p.get_width()-170 , 5, 1)
            else:
                 drawText(f"Current health: "+ str(round(boss.health,0)), font, RED, width - kisame_p.get_width() -170 , 5, 1)

        #when player has defeated the boss
        if not boss.alive:
            screen_scroll = 0
            if passed.drawButton(screen):
                #enter into the next level
                current_level += 1
                worldData = restart_level()
                with open(f"level{current_level}_data.csv", newline = "") as csvfile:
                    reader = csv.reader(csvfile, delimiter = ",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            worldData[x][y] = int(tile)
                bg_scroll = 0
                projectile_amount = 10
                world = World()
                world.data_process(worldData)
                move_plat = world.movable
                platforms = Moveplat(move_plat)
                plat_group.add(platforms)
                boss.alive = True
                activated = False
                player.health = 100
                death_bgm_played = False

                
                if default != "kakashi":
                    player = Ninja(200, 615, 1.5, SPEED, default)

                else:
                    player = Ninja(150, 615, 1.7, SPEED, default)

        
        for e in enemy_group:
            e.draw()
            e.update()
            e.AI()
      

        for enemy in enemy_group:
            health = Healthbar(enemy.rect.x - enemy.rect[2]//2 , enemy.rect.y - 20 , enemy.health, enemy.max_health, "enemy")
            health.draw(enemy.health)

        
        #draw and update pygame sprite groups
        bullet_group.update(player)
        bullet_group.draw(screen)
        item_group.update()
        item_group.draw(screen)
        plat_group.update()
        plat_group.draw(screen)
        scroll_group.update()
        scroll_group.draw(screen)
        explode_group.update()
        explode_group.draw(screen)


      
        #------------------------------------------------------------
        #update player actions depends on the default character
        if player.alive:
 
                
            myBullet.move()
            myBullet.collideBullet()
            myBullet.damage()


            if kunaiCoolDown < 55:
                kunaiCoolDown += 1
            


            if default != "kakashi":

                if shooting:
                    player.actions(4)
                    player.shoot()

                elif explosive_scroll and not thrown:
                    scroll_obj = Explosive(player.rect.centerx + player.rect.size[0]*0.55*player.direction, player.rect.top, player.direction)
                    scroll_group.add(scroll_obj)
                    thrown = True
                    
                    
                
                elif moving_left or moving_right :
                    player.actions(1)

                    
                elif player.inAir and default == "minato":
                    player.actions(3)

                elif 5 < kunaiCoolDown < 30:
                    player.actions(5)

                elif clicked and kunaiCoolDown > 25:
                    if kunaiCoolDown == 55:
                        if default == 'jiraiya':
                            myBullet = Bullet(player.rect.x + 25, player.rect.y + 30 ,"explode", enemy_group)
                        else:
                            myBullet = Bullet(player.rect.x + 25, player.rect.y + 30 ,"kunai", enemy_group)
                        myBullet.shootBullet()
                        kunaiCoolDown = 0
                        

                else:
                    player.actions(0)


            else:

                if moving_left or moving_right:
                    player.actions(4)
                    
                    
                elif player.inAir:
                    player.actions(3)

                else:
                    player.actions(2)

                if shooting:
                    player.actions(5)
                    player.shoot()
                    
                elif explosive_scroll and not thrown:
                    scroll_obj = Explosive(player.rect.centerx + player.rect.size[0]*0.55 * player.direction, player.rect.top, player.direction)
                    scroll_group.add(scroll_obj)
                    thrown = True

                elif clicked and kunaiCoolDown > 25:
                    if kunaiCoolDown == 55:
                        myBullet = Bullet(player.rect.x + 25, player.rect.y + 45 ,"kunai", enemy_group)
                        myBullet.shootBullet()
                        kunaiCoolDown = 0
            
                        
        else:
            #restart will be avaliable once player died
            screen_scroll = 0
            if death_bgm_played == False:
                game_over.play()
                death_bgm_played = True
            if restart.drawButton(screen):
                worldData = restart_level()
                with open(f"level{current_level}_data.csv", newline = "") as csvfile:
                    reader = csv.reader(csvfile, delimiter = ",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            worldData[x][y] = int(tile)
                bg_scroll = 0
                projectile_amount = 10
                world = World()
                world.data_process(worldData)
                move_plat = world.movable
                platforms = Moveplat(move_plat)
                plat_group.add(platforms)
                player.alive = True
                activated = False
                player.health = 100
                death_bgm_played = False

                
                if default != "kakashi":
                    player = Ninja(200, 615, 1.5, SPEED, default)

                else:
                    player = Ninja(150, 615, 1.7, SPEED, default)

        myClock.tick(FPS)
        display.flip()

            
quit()
sys.exit()

