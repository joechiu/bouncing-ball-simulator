import pygame
from pygame.locals import *
import os, sys, time
from random import randint, uniform
from i import Info

time.clock = time.time

pygame.mixer.pre_init(44100, -16, 1, 512)
width, height = 800, 600
bgcolor = Color("black")
clock = pygame.time.Clock()   
B = []
rate = 1/10
# frame per second, best tuned: 1000 x rate
fps = 1000 * rate 
# gravity
G = 9.8
nn = 1

def init(f):
    global screen, font, info
    f()
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    font = pygame.font.SysFont("Courier", 16)
    info = Info(screen, font, Color('yellow'))
    pygame.mixer.set_num_channels(108)

def reload(f):
    def inner(m):
        f(m)
        B.append(Ball("tennis", 100.0, 200.0, uniform(2,10), 0.0, 32, "tennis2", 40 ))
        B.append(Ball("soccer", 050.0, 100.0, uniform(2,10), 0.0, 48, "soccer5", 100 ))
        B.append(Ball("basket", 000.0, 000.0, uniform(2,10), 0.0, 64, "basket3", 160))
    return inner

@reload
def rp(msg): print("%d. %s" % (nn, msg))

def blitRotate(surf, image, pos, originPos, angle):

    # calcaulate the axis aligned bounding box of the rotated image
    w, h       = image.get_size()
    box        = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box    = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box    = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

    # calculate the translation of the pivot 
    pivot        = pygame.math.Vector2(originPos[0], -originPos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move   = pivot_rotate - pivot

    # calculate the upper left origin of the rotated image
    origin = (pos[0] - originPos[0] + min_box[0] - pivot_move[0], pos[1] - originPos[1] - max_box[1] + pivot_move[1])

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)

    # rotate and blit the image
    surf.blit(rotated_image, origin)

    # draw rectangle around the image
    # pygame.draw.rect (surf, (255, 255, 0), (*origin, *rotated_image.get_size()),2)

class Ball:
    def __init__(self, name, x, y, vx, vy, r, s, wt):
        self.name = name
        self.img = pygame.image.load('./img/' + name + '.png')
        self.w, self.h = self.img.get_size()
        self.x = x
        self.y = y
        self.vx = vx  # x velocity
        self.vy = vy  # y velocity
        self.angle = 0
        
        # gravity coefficient for game, 0.2 ~ 0.98 
        self.g = G * rate * 1.8
        # the weight of the ball (eg. gram), 30g for the tennis ball
        # cfe y ~ .96, acts like the friction / elasticity with the weight
        # bouncing infinitely if elasticity changed to 1
        self.cfe = float(1000/(wt + 1000))
        # ball direction and spin effect
        self.d = vx
        self.stop = False
        self.r = r
        self.v = 1
        self.s = pygame.mixer.Sound('./mp3/'+s+'.wav')
        self.c = pygame.mixer.find_channel()
        self.c.queue(self.s)
        self.s.set_volume(self.v)
        print("Ball: %s, SpeedX: %.2f, wt: %.2f, r: %d, g: %.2f, cfe: %f" % (name,vx,wt,r,G,self.cfe))
        
    # sound effect: update and play
    def boing(b, p=True):
        if not b.s: return
        if p:
            b.s.set_volume(b.v)
        else:
            b.s.stop()
        b.c.play(b.s)
        
    def jump(b):
        # the time and timing had been simulated/rated to be 1, 
        b.vy -= b.g  
        b.y -= b.vy * 1/2
        b.x += b.vx
        
        if b.y + b.r > height:
            b.vy = b.vy * -1 * b.cfe
            b.y = float(height) - b.r
            b.vx *= b.cfe
            b.d *= b.cfe
            b.v *= b.cfe
            b.boing()
            
        if b.x + b.r > width:
            b.d *= -1
            b.vx = b.vx * -1
            b.x = float(width) - b.r
            b.boing()
            
        if b.x < b.r:
            b.d *= -1
            b.vx = b.vx * -1
            b.x = b.r
            b.boing()
            
        # stopper points
        if abs(b.vx)<0.4: b.boing(False)
        if abs(b.vx)<0.001**3: b.stop = True

def bb(b):
    ret = True
    for i in range(0, len(b)):
        ret = ret and b[i].stop
    return ret
            
@init
def start(): print("here initialize the screen")

rp("first reload and instantiate the ball objects")
running = True

while running:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                os.startfile(__file__)
                sys.exit()                
            if event.key == pygame.K_SPACE:
                nn += 1
                rp("after reload and instantiate the ball objects")
        if event.type == pygame.QUIT: # If user clicked close
            sys.exit()
    
    screen.fill(bgcolor)
    info.display()
    
    # redrawing balls
    for i in range(0, len(B)):
        pos = (B[i].x, B[i].y)
        blitRotate(screen, B[i].img, pos, (B[i].w/2, B[i].h/2), B[i].angle)
        B[i].angle -= 1 * B[i].d
    
    pygame.display.flip()
    
    if bb(B):
        time.sleep(6)
        pygame.quit()
        break
    else:
        for i in range(0, len(B)):
            B[i].jump()
        
    # fps: 100 is as same as time.sleep(0.01)    
    clock.tick(fps)
    
print("-- FIN --")
