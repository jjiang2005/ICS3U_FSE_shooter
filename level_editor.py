#level editor
from pygame import*
from tkinter import*
from os import listdir
import click,csv


init()
root = Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()-50
screen = display.set_mode((width,height))
root.withdraw()

display.set_caption("level editor")

ROWS = 20
COL = 150
TILE_SIZE = 36


current_level = 0
current_tile = 0
blocks = []
for i in range(4):
    blocks.append(transform.scale(image.load(f"brick/bricks00{i+1}.png").convert_alpha(),(TILE_SIZE, TILE_SIZE)))
    
directories = listdir("collectible")
for x in range(len(directories)):
    blocks.append(transform.scale(image.load(f"collectible/{directories[x]}/p0.png").convert_alpha(),(TILE_SIZE, TILE_SIZE)))


bg_img = transform.scale(image.load("background/back5.jpg").convert(),(width*1.5,height))

#define game variables
scroll_right = False
scroll_left = False
scroll = 0
scroll_speed = 1

#button images
buttons = {
            "save_button": transform.scale(image.load("buttons/save.png").convert_alpha(),(75,35)),
            "load_button": transform.scale(image.load("buttons/load.png").convert_alpha(),(75,35))
           }

save_btn = click.Button(width - 190 , 25, buttons["save_button"], 1)
load_btn = click.Button(width - 100, 25, buttons["load_button"], 1)


#colors
RED = (255,0,0)
GREY =(127,127,127)
BLACK =(0,0,0)
GREEN =(0,255,0)
WHITE = (255,255,255)
BORDER = (220,220,220)
CYAN = (0, 188, 227)
GREY = (125,125,125)

FPS = 60
clock = time.Clock()

font = font.SysFont("Futura", 30)

#A matrix that stores the data of the map
worldData = [[ -1 for _ in range(COL) ] for x in range(ROWS)]



#draw background
def bg():
    screen.fill(BLACK)
    img_width = bg_img.get_width()
    for i in range(1):
        screen.blit(bg_img, ((i*img_width)-scroll,0))

def grid():
    #vertical lines
    for c in range(COL + 1):
        draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0),(c * TILE_SIZE - scroll, height))
    for r in range(ROWS + 1):
        draw.line(screen, WHITE, (0, r * TILE_SIZE), (width, r * TILE_SIZE))


def text(content, font, text_col, x, y):
    img = font.render(content, True, text_col)
    screen.blit(img, (x,y))
    
    
#function for drawing the world tiles
def drawWorld():
    for y, row in enumerate(worldData):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(blocks[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))

#create buttons
#make a button list
bt_list = []
button_col = 0
button_row = 0
for i in range(len(blocks)):
    button_tile = click.Button(width - 250 + (75 * button_col) + 60, 75 * button_row + 100, blocks[i], 1)
    bt_list.append(button_tile)
    button_col += 1
    if button_col == 3:
        button_col = 0
        button_row += 1

        
running = True
while running:
    
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        if evt.type == KEYDOWN:
            if evt.key == K_LEFT:
                scroll_left = True
            if evt.key == K_RIGHT:
                scroll_right = True
            if evt.key == K_RSHIFT:
                scroll_speed = 5
            if evt.key == K_UP:
                current_level += 1
            if evt.key == K_DOWN and current_level > 0:
                current_level -= 1
                
        if evt.type == KEYUP:
            if evt.key == K_LEFT:
                scroll_left = False
            if evt.key == K_RIGHT:
                scroll_right = False
            if evt.key == K_ESCAPE:
                running = False
            if evt.key == K_RSHIFT:
                scroll_speed = 1

    #get mouse position
    mx, my = mouse.get_pos()
    x = (mx + scroll)//TILE_SIZE
    y = my // TILE_SIZE

    #check that the coordinates are within the map
    if mx < width - 215 and my < height -320 or my > height -320:
        #update the tile index
        if mouse.get_pressed()[0] == 1 and worldData[y][x] != current_tile:
            worldData[y][x] = current_tile
        if mouse.get_pressed()[2] == 1:
            worldData[y][x] = -1

    
        
    bg()
    grid()
    drawWorld()
    
    #scrolling
    if scroll_left and scroll > 0:
        scroll -= 3*scroll_speed
    if scroll_right and scroll < 675:
        scroll += 3*scroll_speed

    #tile panel
    draw.rect(screen, GREY, (width - 215, 0, 215, height - 320))

    button_counter = 0
    for button_counter, i in enumerate (bt_list):
        if i.drawButton(screen):
           current_tile = button_counter
           
        
    #highlight the selected tile
    draw.rect(screen, RED, bt_list[current_tile].outlineRect,2)    

    #save&load data
    if save_btn.drawButton(screen):
        #save data using context manager
        with open(f"level{current_level}_data.csv", "w", newline = "") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter = ",")
            for r in worldData:
                csv_writer.writerow(r)
                
    if load_btn.drawButton(screen):
        #load in level data
        try:
            scroll = 0
            with open(f"level{current_level}_data.csv", "r", newline = "") as csvfile:
                csv_reader = csv.reader(csvfile, delimiter = ",")
                for x, r in enumerate (csv_reader):
                    for y, tile in enumerate(r):
                        worldData[x][y] = int(tile)
                        
        except Exception as e:
            pass

        
    text(f"Level-{current_level}", font, WHITE, width - 100, 325)
    
    clock.tick(FPS)
    display.update()
quit()

