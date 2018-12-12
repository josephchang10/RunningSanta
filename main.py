# Setup ------------------------------------------------------ #
import pygame, sys, os, math, random, time
from pygame.locals import *

# Setup pygame/window ---------------------------------------- #
pygame.init()
clock = pygame.time.Clock()

W, H = 800, 437
DEFAULT_SPEED = 60

win = pygame.display.set_mode((W,H), FULLSCREEN)
pygame.display.set_caption('Running Santa')

def load_bg():
    global bg, bgX, bgX2
    bg = pygame.image.load(os.path.join('images','bg' + str(random.randint(1,4)) + '.jpg')).convert()
    bgX = 0
    bgX2 = bg.get_width()

load_bg()

snow_list = []

for i in range(80):
    x = random.randrange(0, W)
    y = random.randrange(0, H)
    z = random.randrange(1, 4) # size
    snow_list.append([x, y, z])

# Audio ------------------------------------------------------ #

pygame.mixer.pre_init(44100, -64, 2, 2048)

def load_snd(name):
    return pygame.mixer.Sound('data/sound/' + name + '.wav')

def stop_snd(name):
    return pygame.mixer.Sound.stop('data/sound/' + name + '.wav')

pygame.mixer.init(44100,-16,2,2048)
pygame.mixer.set_num_channels(32)

pygame.mixer.music.load('data/music/main.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)

grass_s = load_snd('grass')
jump_s = load_snd('jump')
hurt_s = load_snd('hurt')
running_s = load_snd('running')

# Classes ---------------------------------------------------- #
class player(object):
    # Animations ----------------------------------------------- #
    run = [pygame.image.load(os.path.join('images', 'Run (' + str(x) + ').png')) for x in range(1,12)]
    jump = [pygame.image.load(os.path.join('images', 'Jump (' + str(x) + ').png')) for x in range(1,17)]
    slide = [pygame.image.load(os.path.join('images', 'Slide (' + str(x) + ').png')) for x in range(1,12)]
    fall = [pygame.image.load(os.path.join('images', 'Dead (' + str(x) + ').png')) for x in range(1,18)]
    jumpList = [1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-1,-1,-1,-1,-1,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-3,-3,-3,-3,-3,-3,-3,-3,-3,-3,-3,-3,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4]
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.jumping = False
        self.sliding = False
        self.falling = False
        self.slideCount = 0
        self.jumpCount = 0
        self.runCount = 0

    def draw(self, win):
        global pause

        if self.falling:
            win.blit(self.fall[pause//(math.ceil((fallSpeed * 2)/16))], (self.x, self.y))
            pygame.mixer.music.stop()   
        elif self.jumping:
            self.y -= self.jumpList[self.jumpCount] * 1.3
            win.blit(self.jump[self.jumpCount//7], (self.x,self.y))
            self.jumpCount += 1
            if self.jumpCount > 105:
                self.jumpCount = 0
                self.jumping = False
                self.runCount = 0
            self.hitbox = (self.x+30,self.y,self.width-24,self.height-10)
        elif self.sliding:
            if self.slideCount < 20:
                self.hitbox = (self.x+ 4,self.y,self.width-24,self.height-10)
            elif self.slideCount > 20 and self.slideCount < 80:
                self.hitbox = (self.x+15,self.y+22,self.width-8,self.height-35)
            if self.slideCount >= 110:
                self.slideCount = 0
                self.runCount = 0
                self.sliding = False
                self.hitbox = (self.x+ 4,self.y,self.width-24,self.height-10)
            win.blit(self.slide[self.slideCount//11], (self.x,self.y))
            self.slideCount += 1
        else:
            if self.runCount > 60:
                self.runCount = 0
            win.blit(self.run[self.runCount//6], (self.x,self.y))
            self.runCount += 1
            self.hitbox = (self.x+30,self.y,self.width-24,self.height-13)
 
        # pygame.draw.rect(win, (255,0,0),self.hitbox, 2)

class saw(object):
    rotate = [pygame.image.load(os.path.join('images', 'SAW0.PNG')),pygame.image.load(os.path.join('images', 'SAW1.PNG')),pygame.image.load(os.path.join('images', 'SAW2.PNG')),pygame.image.load(os.path.join('images', 'SAW3.PNG'))]
    def __init__(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotateCount = 0
        self.vel = 1.4

    def draw(self,win):
        self.hitbox = (self.x + 25, self.y + 5, self.width - 50, self.height - 5)
#        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        if self.rotateCount >= 8:
            self.rotateCount = 0
        win.blit(pygame.transform.scale(self.rotate[self.rotateCount//2], (64,64)), (self.x,self.y))
        self.rotateCount += 1

    def collide(self, rect):
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] + rect[3] > self.hitbox[1]:
                return True
        return False


class spike(saw):
    img = pygame.image.load(os.path.join('images', 'spike.png'))
    def draw(self,win):
        self.hitbox = (self.x + 30, self.y, 25,315)
        # pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(self.img, (self.x,self.y))

    def collide(self, rect):
        r1 = pygame.Rect(self.hitbox[0],self.hitbox[1],self.hitbox[2],self.hitbox[3])
        r2 = pygame.Rect(rect[0],rect[1],rect[2],rect[3])
        return r1.colliderect(r2)

def updateFile(): 
    f = open('scores.txt','r')
    file = f.readlines()
    last = int(file[0])

    if last < int(score):
        f.close()
        file = open('scores.txt', 'w')
        file.write(str(int(score)))
        file.close()

        return score
               
    return last

def endScreen():
    global pause, score, speed, obstacles
    pause = 0
    speed = DEFAULT_SPEED
    obstacles = []
                   
    run = True
    while run:
        pygame.mixer.music.play()
        pygame.time.delay(100)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
                else:
                    run = False
                    runner.falling = False
                    runner.sliding = False
                    load_bg()
               
        win.blit(bg, (0,0))
        largeFont = pygame.font.SysFont('comicsans', 80)
        hintFont =  pygame.font.SysFont('comicsans', 40)
        lastScore = largeFont.render('Longest Distance: ' + str(int(updateFile()))+'m',1,(255,255,255))
        currentScore = largeFont.render('Distance: '+ str(int(score))+'m',1,(255,255,255))
        
        hint = hintFont.render('PRESS ANY KEY TO CONTINUE',1,(255,255,255))
        win.blit(lastScore, (W/2 - lastScore.get_width()/2,100))
        win.blit(currentScore, (W/2 - currentScore.get_width()/2, 160))
        win.blit(hint,(W/2 - hint.get_width()/2, 280))
        pygame.display.update()
    score = 0


def redrawWindow():
    
    win.blit(bg, (bgX, 0))
    win.blit(bg, (bgX2,0))

    runner.draw(win)
    for obstacle in obstacles:
        obstacle.draw(win)

    largeFont = pygame.font.SysFont('comicsans', 30)
    text = largeFont.render('Distance: ' + str(int(score))+'m', 1, (255,255,255))
    win.blit(text, (600, 10))

    for i in range(len(snow_list)):
        # Draw the snow flake
        pygame.draw.circle(win, (255, 255, 255), (snow_list[i][0],snow_list[i][1]), snow_list[i][2])
 
        # Move the snow flake down one pixel
        snow_list[i][1] += 1
 
        # If the snow flake has moved off the bottom of the screen
        if snow_list[i][1] > 400:
            # Reset it just above the top
            y = random.randrange(-50, -10)
            snow_list[i][1] = y
            # Give it a new x position
            x = random.randrange(0, W)
            snow_list[i][0] = x

    pygame.display.update()

pygame.time.set_timer(USEREVENT+1, 500)
pygame.time.set_timer(USEREVENT+2, 3000)
pygame.time.set_timer(USEREVENT+3, 450)
speed = DEFAULT_SPEED

score = 0

run = True
runner = player(200, 290, 64, 94)

obstacles = []
pause = 0
fallSpeed = 0
ms = 0

while run:
    
    if pause > 0:
        pause += 1
        if pause > fallSpeed * 2:
            endScreen()
    
    for obstacle in obstacles:
        if obstacle.collide(runner.hitbox):
            hurt_s.play(0)
            pygame.mixer.music.stop()
            runner.falling = True
            
            if pause == 0:
                pause = 1
                fallSpeed = speed
        if obstacle.x < -64:
            obstacles.pop(obstacles.index(obstacle))
        else:
            obstacle.x -= 1.4
    
    bgX -= 1.4
    bgX2 -= 1.4

    if bgX < bg.get_width() * -1:
        bgX = bg.get_width()
    if bgX2 < bg.get_width() * -1:
        bgX2 = bg.get_width() 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False

        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
            
        if event.type == USEREVENT+1:
            speed += 1
            score += (speed-DEFAULT_SPEED)*0.03
            
        if event.type == USEREVENT+2:
            r = random.randrange(0,2)
            if r == 0:
                obstacles.append(saw(810, 300, 64, 64))
            elif r == 1:
                obstacles.append(spike(810, -10, 48, 310))
                
        if event.type == USEREVENT+3 and runner.falling == False and runner.jumping ==False and runner.sliding  == False :
            running_s.play(loops=0)
                
    if runner.falling == False:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            jump_s.play(loops=0,fade_ms=500)
            if not(runner.jumping):
                runner.jumping = True
                
        if keys[pygame.K_DOWN]:
            if not(runner.sliding):
                runner.sliding = True
                if runner.jumping ==False:
                    grass_s.play(2)

    clock.tick(speed)
    redrawWindow()




