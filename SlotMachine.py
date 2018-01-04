import os
import pygame
from pygame.locals import *
import random
import time
from numpy.random import choice
import numpy as np
#only if using raspberry pi
#import smbus
#import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#For RPI version 1, use "bus = smbus.SMBus(0)"
#Sbus = smbus.SMBus(1)

# This is the address we setup in the Arduino Program
#address = 0x08

pygame.init()
pygame.mouse.set_visible(False)

SIZE = WIDTH, HEIGHT = 1000, 760
BACKGROUND_COLOR = pygame.Color('black')
FPS = 80

spriteImageWidth = 325
spriteImageHeight = 263
imagePadding = 12 #padding between reel images

screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
time = pygame.time

#load font, prepare values
font = pygame.font.Font(None, 80)
text = 'Fonty'
size = font.size(text)

fg = 250, 250, 250 #font color
fgGreen = 0, 250, 0 #green font color
fgRed = 250, 0, 0 #red font color
bg = 5, 5, 5
   
scores_sys_font = pygame.font.Font("slot_fonts/Something Strange.ttf", 40)
scoreFinal_sys_font = pygame.font.Font("slot_fonts/Something Strange.ttf", 50)
cost_sys_font = pygame.font.SysFont("Arial", 50)
play_sys_font = pygame.font.Font("slot_fonts/Seaside.ttf", 50)
cashOut_sys_font = pygame.font.Font("slot_fonts/FFF_Tusj.ttf", 40)
bank_sys_font = pygame.font.Font("slot_fonts/StripesCaps.ttf", 55)
c_sys_font = pygame.font.SysFont("Arial", 90)
d_sys_font = pygame.font.SysFont("Arial", 25)
e_sys_font = pygame.font.SysFont("Arial", 20)

#table for probablities for selecting final reel image
#weighted towards hex and demons
#each reel gets a different probability
PROBABILTY1=[0.05,0.2,0.07,0.24,0.21,0.12,0.01,0.01,0.01,0.06,0.02]
PROBABILTY2=[0.01,0.35,0.01,0.21,0.19,0.11,0.01,0.01,0.01,0.06,0.03]
PROBABILTY3=[0.11,0.2,0.15,0.19,0.1,0.03,0.07,0.04,0.03,0.06,0.02]

#set normal probability to start
PROBABILTY = PROBABILTY1
#number of images loaded from image folder
IMAGES_N = 11

if IMAGES_N <> len(PROBABILTY):
   print"number of images and probability array length do not match!"
          
background_image = pygame.image.load("slot_background_images/devils_delight_wallpaper_1000_760_v2.png").convert()
background_image_blank = pygame.image.load("slot_background_images/devils_delight_wallpaper_1000_760_v2_blank.png").convert()

#icon for app window
icon = pygame.image.load('slot_misc_images/icon.png')
pygame.display.set_icon(icon)
pygame.display.set_caption("Devil's Bargain")

pygame.mixer.init()

#create background music for the game
pygame.mixer.music.load("slot_sounds/bgSlotMusic.ogg")
#pygame.mixer.music.load("slot_sounds/gravewalk.ogg")
#loop the sound file continuously starting at 0.0
pygame.mixer.music.play(-1,0.0)
pygame.mixer.music.set_volume(0.2) #between 0-1

#create array to hold soundsif you want to go this way
# sounds = []
#create the variables and assign them the sounds
# spinSound = pygame.mixer.Sound("Sounds/slotSpinSound.ogg")
# winSound = pygame.mixer.Sound("Sounds/slotWinSound.ogg")
#add them to the sounds array
# sounds.append(spinSound)
# sounds.append(winSound)

#unique sound for each reel
reelSpin1 = pygame.mixer.Sound('slot_sounds/reel_fast.ogg')
reelSpin2 = pygame.mixer.Sound('slot_sounds/reel_fast2.ogg')
reelSpin3 = pygame.mixer.Sound('slot_sounds/reel_fast.ogg')

#unique sound for each image
reelImageSounds = []
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/dice.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/hex.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/growl.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/devil_laugh.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/witch_laugh.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/reaper_laugh.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/crow1.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/crow2.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/crow3.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/moo.ogg'))
reelImageSounds.append(pygame.mixer.Sound('slot_sounds/thunder.ogg'))

#sounds for various outcomes (win, lose)
win1_sound = pygame.mixer.Sound('slot_sounds/win1.ogg')
win2_sound = pygame.mixer.Sound('slot_sounds/win2.ogg')
win3_sound = pygame.mixer.Sound('slot_sounds/win3.ogg')
win4_sound = pygame.mixer.Sound('slot_sounds/win_moo.ogg')
lose_sound = pygame.mixer.Sound('slot_sounds/error.ogg')
noPoints_sound = pygame.mixer.Sound('slot_sounds/sigh.ogg')
lever_sound = pygame.mixer.Sound('slot_sounds/slot_lever.ogg')

# name_decoder- array of image names based on index position in 'images' array
name_decoder = ["Dice", "Hex", "666", "Demon", "Devil Girl",
                    "Satan", "Tomestone Q", "Tomestone K", "Tomestone A", "Evil Cow", "God Cow"]
catagory_decoder = ["Satanic", "Satanic", "Satanic", "Demon", "Demon", "Demon", "Grave", "Grave", "Grave",
                     "Special", "xSpecial"]

reelImages = []

#set up event clock(s)
pygame.time.set_timer(USEREVENT+1, 50)

#I2C read and write
##def writeNumber(value):
##    bus.write_byte(address, value) #number of coins to pay out
##    return -1
##
##def readNumber():
##    number = bus.read_byte(address) #number of coins added
##    return number
   
def timerFunc(index):
       index_old = index
       index = index+1
       #print"index incremented to "+repr(index)+" in timerFunc"
       return index
      
def load_images(path):
    """
    Loads all images in directory. The directory must only contain images.
    Args: path: The relative or absolute path to the directory to load images from.
    Returns: List of images.
    """
    images = []
    images_names = []
    
    for file_name in os.listdir(path):
        image_name = file_name
        images_names.append(image_name)
    images_names = sorted(images_names) #use sort to insure linux file sys behaves
    print(images_names) #check for proper order

    for file_name in images_names:
        image = pygame.image.load(path + os.sep + file_name).convert()
        images.append(image)
    return images

def create_reels(imageArr):
    #create each reel from shuffled image array to look random
    #random.shuffle(imageArr)
    reel1 = AnimatedSprite(position=(imagePadding, 10), images=imageArr)
    #random.shuffle(imageArr)
    reel2 = AnimatedSprite(position=((spriteImageWidth)+imagePadding, 10), images=imageArr)
    #random.shuffle(imageArr)
    reel3 = AnimatedSprite(position=((spriteImageWidth*2)+imagePadding, 10), images=imageArr)

    # Create sprite groups and add reels to them.
    all_spinning_sprites = pygame.sprite.Group(reel1, reel2, reel3)
    only_2_3_spinning_sprites = pygame.sprite.Group(reel2, reel3)
    only_3_spinning_sprites = pygame.sprite.Group(reel3)
    return all_spinning_sprites,only_2_3_spinning_sprites,only_3_spinning_sprites

def choose_final_images(n, probability):
    #choose final reel image
    #use probabilities to choose 3 random images
    imageIndexs = np.random.choice(n, 3, p=probability)
    return imageIndexs

def check_input():
    for event in pygame.event.get():
     if event.type == pygame.KEYDOWN:
         if event.key == pygame.K_DOWN:
            print"In check_input fxn, Key hit: down detected, QUIT"
            pygame.quit()
            sys.exit()
    return index

def draw_player_data(bank):
   textSurf = bank_sys_font.render(" Bank "+(repr(bank))+" ", 1, fg, bg)
   textRect = textSurf.get_rect()
   textRect.center = (WIDTH/8, HEIGHT-55)
   screen.blit(textSurf, textRect)

def score_update(current, total, bonusNum, bonusName, bonusCat, specialCat, xspecialCat, bet):

   print"length of bonusNum: "+repr(len(bonusNum))
   print"bonusName: "+bonusName
   print"bonusCat: "+bonusCat
   print"bet: "+repr(bet)
   nameScore = bonusNum[0]
   catScore = bonusNum[1]
   specialScore = bonusNum[2]
   xspecialScore = bonusNum[3]
   text_y = spriteImageHeight + imagePadding #start text here
   text_height = 50 #increment y by this
   
   subscore_cat = scores_sys_font.render("Bet: "+repr(bet), 1, fg)
   screen.blit(subscore_cat, (5, text_y))
   pygame.display.update()
   pygame.time.wait(100)
   text_y = text_y + text_height

   subscoreName = scores_sys_font.render("Bonus: "+repr(nameScore)+" "+bonusName+" ", 1, fg)
   screen.blit(subscoreName, (5, text_y))
   pygame.display.update()
   if bonusName > 0:
      win1_sound.play()
   pygame.time.wait(200)
   text_y = text_y + text_height

   subscore_cat = scores_sys_font.render("Bet Multiplier: X"+repr(bet), 1, fg)
   screen.blit(subscore_cat, (5, text_y))
   pygame.display.update()
   if catScore > 0:
      win1_sound.play()
   pygame.time.wait(400)
   text_y = text_y + text_height
   
   subscore_total = scores_sys_font.render("**Sub Total: "+repr(bet*nameScore)+"**", 1, fg)
   screen.blit(subscore_total, (5, text_y))
   pygame.display.update()
   if catScore*nameScore > 0:
      win1_sound.play()
   else:
      lose_sound.play()
   pygame.time.wait(600)
   text_y = text_y + text_height + 10

   if specialScore > 0:
      subscore_special = scores_sys_font.render("Add Special: "+repr(specialScore)+" "+specialCat+" ", 1, fg)
      screen.blit(subscore_special, (5, text_y))
      pygame.display.update()
      text_y = text_y + text_height
      win2_sound.play()
      pygame.time.wait(500)
   else:
      text_y = text_y + 10
   
   if xspecialScore <> 0:
      subscore_xspecial = scores_sys_font.render("Wrath of God: "+repr(xspecialScore)+" "+xspecialCat+" ", 1, fg)
      screen.blit(subscore_xspecial, (5, text_y))
      pygame.display.update()
      win4_sound.play()
      text_y = text_y + text_height + 4
      pygame.time.wait(500)
   else:
      text_y = text_y + 10 
   
   pygame.draw.lines(screen, fg, False, [(5, text_y), (500,text_y)], 3)
   pygame.time.wait(500)
   #text_y = text_y + text_height
   
   ren1 = scoreFinal_sys_font.render("Current Score: "+repr(current), 1, fg)
   screen.blit(ren1, (5, text_y))
   pygame.display.update()
   if current > 0:
      win3_sound.play()
   else:
      noPoints_sound.play()
   pygame.time.wait(1500)

   #redraw backround to clear previous text   
   screen.blit(background_image, [0, 0])
   draw_player_data(total)
   pygame.display.update()

def pay_update(cost, total):
   total = total - cost

   pygame.display.update()
   pygame.time.wait(1500)

   #redraw backround to clear previous text
   screen.blit(background_image, [0, 0])
   draw_player_data(total)
   pygame.display.update()
   return total

#process keyboard input to set bet
# bet - the current bet
# key - the keyboard key pressed
#returns - the new bet
def procBet(bet,key):
    betStr = str(bet) #get the bet string
                
    #try because chr will fail if character is > 255, but we dont care about them anyways
    try:
        #if the key is a backspace
        if key == K_BACKSPACE:
            betStr = betStr[0:-1] #remove the last digit
        
        #if key is a digit
        elif (chr(key).isdigit()):
            betStr += chr(key)  #add it to the bet string
        
        #if user entered an invalid bet (nothing)
        if(not betStr):
            return 0 #new bet of 0
    
    #if there was any problem, return the original bet
    except Exception:
        return bet
    
    #convert and return the new bet
    return int(betStr)
   
def pull_handle(images, spinning_3_sprites,spinning_2_sprites,spinning_1_sprites, final_reel1, final_reel2, final_reel3):

    reel1_static = False
    reel2_static = False
    reel3_static = False

    spins = 0
    running = True
    
    while running:
        # Amount of seconds between each loop.
        #dt = clock.tick(FPS) / 1000
        dt = clock.get_rawtime()

        for event in pygame.event.get():
           if event.type == USEREVENT+1:
              spins = timerFunc(spins) #calling the function whenever we get timer event.
              #print"Event index(spins): " + repr(spins)
        
        if spins >= 40:
           spin1 = False
        else:
           spin1 = True

        if spins >= 75:
           spin2 = False
        else:
           spin2 = True

        if spins >= 120:
           spin3 = False
        else:
           spin3 = True

        if spin1 & spin2 & spin3:
           #print"all true!"
           spinning_3_sprites.update(spins,USEREVENT+1)
           spinning_3_sprites.draw(screen)
           reelSpin1.play()
           reelSpin2.play()
           reelSpin3.play()
           if not reel1_static:
              #print"play effect: "+repr(final_reel1)
              reel1_static = True
        elif spin2 & spin3:
           #print"2 and 3 true!"
           if not reel2_static:
              #print"play effect: "+repr(final_reel2)
              reelSpin1.stop()
              reelImageSounds[final_reel1].play()
              reel2_static = True
           spinning_2_sprites.update(spins,USEREVENT+1)
           spinning_2_sprites.draw(screen)
           screen.blit(images[final_reel1], (imagePadding,10))
           
        elif spin3:
           #print"only 3 true!"
           if not reel3_static:
              #print"play effect: "+repr(final_reel3)
              reelSpin2.stop()
              reelImageSounds[final_reel1].stop()
              reelImageSounds[final_reel2].play()
              reel3_static = True
           spinning_1_sprites.update(spins,USEREVENT+1)
           spinning_1_sprites.draw(screen)
           screen.blit(images[final_reel1], (imagePadding,10))
           screen.blit(images[final_reel2], (spriteImageWidth+imagePadding,10))
           
        else:
           print"Game over!"
           reelSpin3.stop()
           reelImageSounds[final_reel2].stop()
           reelImageSounds[final_reel3].play()
           screen.blit(images[final_reel1], (imagePadding,10))
           screen.blit(images[final_reel2], (spriteImageWidth+imagePadding,10))
           screen.blit(images[final_reel3], ((spriteImageWidth*2)+imagePadding,10))        
           running = False
           
        #all_sprites.update(dt,USEREVENT+1)  # Calls the 'update' method on all sprites in the list.
        #print"pygame.time.get_ticks: " + repr(time.get_ticks())
        #all_sprites.draw(screen)
        #screen.fill(BACKGROUND_COLOR)
        pygame.display.update()
        pygame.event.pump()

def redraw_static_reels(images, final_reel1, final_reel2, final_reel3):
    screen.blit(images[final_reel1], (imagePadding,10))
    screen.blit(images[final_reel2], (spriteImageWidth+imagePadding,10))
    screen.blit(images[final_reel3], ((spriteImageWidth*2)+imagePadding,10))
    pygame.display.update()

def run_game(bank, cost, reelImages,currentbet):

       #create the 3 reels and animate to spin 1, 2, or 3
       spinning_3_sprites,spinning_2_sprites,spinning_1_sprites = create_reels(reelImages)
       #choose final reel image
       imageIndexs = choose_final_images(IMAGES_N, PROBABILTY1)
       final_reel1 = imageIndexs[0]
       print"final_reel1: "+repr(final_reel1)
       imageIndexs = choose_final_images(IMAGES_N, PROBABILTY2)
       final_reel2 = imageIndexs[0]
       print"final_reel2: "+repr(final_reel2)
       imageIndexs = choose_final_images(IMAGES_N, PROBABILTY3)
       final_reel3 = imageIndexs[0]
       print"final_reel3: "+repr(final_reel3)
       imageIndexs = [final_reel1,final_reel2,final_reel3]
       print"imageIndexs: "+repr(imageIndexs)
       print"********************"
       print"choose these reelImages["+repr(imageIndexs[0])+"], ["+repr(imageIndexs[1])+"], ["+repr(imageIndexs[2])+"]"

       final_name1 = name_decoder[imageIndexs[0]]
       final_name2 = name_decoder[imageIndexs[1]]
       final_name3 = name_decoder[imageIndexs[2]]
              
       final_cat1 = catagory_decoder[imageIndexs[0]]
       final_cat2 = catagory_decoder[imageIndexs[1]]
       final_cat3 = catagory_decoder[imageIndexs[2]]

       #Make numpy arrays so we can do advanced searching/matching
       final_reels = np.array([final_reel1,final_reel2,final_reel3])
       final_names = np.array([final_name1,final_name2,final_name3])
       final_cats =  np.array([final_cat1,final_cat2,final_cat3])

       #bank = bank - cost #charge cost_pull for a spin!

       bank = pay_update(cost, bank)
       draw_player_data(bank)
       
       pull_handle(reelImages, spinning_3_sprites,spinning_2_sprites,spinning_1_sprites, final_reel1, final_reel2, final_reel3)

       # pause after reels have all stopped
       pygame.time.wait(1000)

       #display and calculate score
       scoreName = 0 #reset score for individual images
       bonusName = ""
       bonusCat = ""
       specialCat = ""
       xspecialCat = ""
       score_special = 0
       score_xspecial = 0

       #set to 'True' if matches 3 or 2
       setGodMatch = False
       setEvilMatch = False
       setHexMatch = False
       
       for name in name_decoder:
          #print"name: "+repr(name)
          #print"np.count_nonzero: "+repr(np.count_nonzero(final_names == name))
          if np.count_nonzero(final_names == name) == 3:
             if name == "God Cow":
                score_xspecial = -30
                xspecialCat = "Triple Cow God!"
                lose_sound.play()
                setGodMatch = True
             elif name == "Evil Cow":
                score_special = 6
                specialCat = "Triple Evil Cow!"
                win3_sound.play()
                setEvilMatch = True
             elif name == "Satan":
                scoreName = 50
                bonusName = "Triple Satan!"
                win3_sound.play()
             elif name == "Devil Girl":
                scoreName = 20
                bonusName = "Triple Devil Girl!"
                win3_sound.play()
             elif name == "Demon":
                scoreName = 10
                bonusName = "Triple Demon!"
                win3_sound.play()
             elif name == "Hex":
                scoreName = 4
                bonusName = "Triple Hex!"
                win1_sound.play()
                win2_sound.play()
                setHexMatch = True
             else:
                print"no match for 3 scoreName "+name
                
          elif np.count_nonzero(final_names == name) == 2:
             #print"np.count_2(final_names == "+name+" == "+repr(np.count_nonzero(final_names == name))
             if name == "God Cow":
                score_xspecial = -20
                xspecialCat = "Double Cow God!"
                lose_sound.play()
                setGodMatch = True
             elif name == "Evil Cow":
                score_special = 4
                specialCat = "Double Evil Cow!"
                win2_sound.play()
                setEvilMatch = True
             elif name == "Hex":
                scoreName = 2
                bonusName = 'Double Hex!'
                win2_sound.play()
                setHexMatch = True
             else:
                print"no match for 2 scoreName "+name

          #print"first loop looking for triplets done, scoreName: "+repr(scoreName)+", bonusName: "+bonusName

       for name in name_decoder:
          #print"np.count_1(final_names == "+name+" == "+repr(np.count_nonzero(final_names == name))
          if np.count_nonzero(final_names == name) == 1:
             print"looking for match for 1 scoreName == "+name
             if name == "God Cow":
                print"Match for scoreName "+name
                if setGodMatch == False:
                   score_xspecial = -10
                   xspecialCat = "Single Cow God!"
                   lose_sound.play()
             elif name == "Evil Cow":
                if setEvilMatch == False:
                   score_special = 2
                   specialCat = "Single Evil Cow!"
                   win1_sound.play()
                   print"Match for scoreName "+name
             elif name == "Hex":
                if setHexMatch == False:
                   scoreName = 1
                   bonusName = "Single Hex!"
                   win1_sound.play()
                   print"Match for scoreName "+name
             elif np.count_nonzero(final_names == "Demon") == 1:
                if np.count_nonzero(final_names == "Devil Girl") == 1:
                   if np.count_nonzero(final_names == "Satan") == 1:
                      scoreName = 4
                      bonusName = "All Demons!"
                      win2_sound.play()
                      print"Match for scoreName "+name
 
       scoreCat  = 1
       
       finalScore = (scoreName * scoreCat*currentbet) + score_special + score_xspecial
       
       if finalScore == 0:
          lose_sound.play()

       print"reelImages["+repr(final_reel1)+"], ["+repr(final_reel2)+"], ["+repr(final_reel3)+"]"
       print"["+final_name1+"], ["+final_name2+"], ["+final_name3+"]"
       print"["+final_cat1+"], ["+final_cat2+"], ["+final_cat3+"]"
       print"bonusName: "+repr(bonusName)
       print"scoreName: "+repr(scoreName)
       print"scoreCat: "+repr(scoreCat)
       print"score_special: "+repr(score_special)
       print"score_xspecial: "+repr(score_xspecial)

       bank = bank+finalScore
       
       print"Current Total Score: "+repr(finalScore)
       print"Cummalative Total: "+repr(bank)
       print"**************************************"
       
       bonusNums = []

       bonusNums = [scoreName, scoreCat, score_special, score_xspecial]

       score_update(finalScore, bank, bonusNums, bonusName, bonusCat, specialCat, xspecialCat, currentbet)

       redraw_static_reels(reelImages, final_reel1, final_reel2, final_reel3)

       #redraw backround to clear previous text
       screen.blit(background_image, [0, 0])
       pygame.display.update()
       redraw_static_reels(reelImages, final_reel1, final_reel2, final_reel3)

       draw_player_data(bank) #update the running data like total bank

       return bank

class AnimatedSprite(pygame.sprite.Sprite):

    def __init__(self, position, images):
        """
        Animated sprite object.
        Args:
            position: x, y coordinate on the screen to place the AnimatedSprite.
            images: Images to use in the animation.
        """
        super(AnimatedSprite, self).__init__()

        size = (spriteImageWidth, spriteImageHeight)  # This should match the size of the images.

        self.rect = pygame.Rect(position, size)
        self.images = images
        #pick a random starting image
        self_index_start = random.randint(0, IMAGES_N-1)
        #Sprint"self.index: " + repr(self_index_start)
        self.index = self_index_start
        self.image = images[self.index]  # 'image' is the current image of the animation.

        self.animation_time = 0.1
        self.current_time = 0

        self.animation_frames = IMAGES_N
        self.current_frame = 0
        print "Sprit initiated!"
        

    def update_event_dependent(self, counter):
        """
        Updates the image of Sprite by event timer.
        Args:
            events occur periodically by timer.
        """
        #print"event count: " + repr(counter)

        self.index = (self.index + 1) % len(self.images)
        self.image = self.images[self.index]
            
    def update(self, counter, USEREVENT):
        self.update_event_dependent(counter)

def button_press(pin):
      print(str(pin) + ' button pressed')
      time.wait(200)
  
        
def main():

   #reset scores
   print"reset scores...."
   finalScore = 0 #current reels
   bank = 1 #total bank, start with 0
   cost_pull = 1 #cost per pull (1-4)
   minBet = 1 #minimum bet allowed to play
   repullMultiplier = 0.25 #mult bank if repull before cashout
   running = True
   #load the reel images
   #Make sure to provide the relative or full path to the images directory.
   reelImages = load_images(path='slot_images_lg')
   #draw intro screen
   
##   textSurf = b_sys_font.render("Soul Cost 1", 1, fg)
##   textRect = textSurf.get_rect()
##   textRect.center = ((WIDTH/2),(HEIGHT/5))
##   screen.blit(textSurf, textRect)
##
##   screen.blit(background_image, [0, 0])
##   pygame.display.update()
##   textSurf = b_sys_font.render("Press Down Arrow To Spin", 1, fg)
##   textRect = textSurf.get_rect()
##   textRect.center = ((WIDTH/2),(HEIGHT/3))
##   screen.blit(textSurf, textRect)

   pygame.display.update()
   mybet = 0 # amt bet
   firstSpin = True #change to false after first spin
   
   while (running):
##only if using raspberry pi
       #only if using raspberry pi
##       input_state = GPIO.input(22)
##       if input_state == False:
##          button_press(22)
##          print"Key hit: quit"
##          try:
##             writeNumber(int(bank)) #payout money
##          except:
##             print"IO write error"
##          print"Payout: "+repr(bank)
##          #running = False
##          #pygame.quit()
##          bank = 0
##       input_state = GPIO.input(27)
##       if input_state == False:
##          button_press(27)
##          print"bank: "+repr(bank)
##          print"Key hit: 'green button', so spin again!"
##          #win1_sound.play()
##          lever_sound.play()
##          if bank <= 0:
##             print"Soul Bank empty, Add More Money!"
##
##          firstSpin = False
##          screen.blit(background_image, [0, 0])
##          pygame.display.update()
##
##          mybet = 0
##          if bank <= 4 :
##              if bank >= 1:
##                  mybet = bank #for now, bet it all!
##                  cost_pull = mybet
##              else:
##                 cost_pull = 1
##                 mybet = 1
##          elif bank > 4:
##             mybet = 4
##             cost_pull = mybet
##             
##          if bank <= 0:
##            print"Add more money!"
##            #fill background
##            screen.fill(BACKGROUND_COLOR)
##            textSurf = c_sys_font.render("Add More Money!", 1, fg)
##            textRect = textSurf.get_rect()
##            textRect.center = ((WIDTH/2),(HEIGHT/3))
##            screen.blit(textSurf, textRect)
##            pygame.display.update()
##            bank = 0 #reset score in case it is negative
##            pygame.time.wait(1000)
##            #pygame.quit()
##          else:
##            bank = run_game(bank, cost_pull,reelImages,mybet)
##            screen.blit(background_image, [0, 0])
##            draw_player_data(bank)
##             
##          if bank < minBet:
##            print"GAME OVER!"
##            #fill background
##            screen.fill(BACKGROUND_COLOR)
##            textSurf = c_sys_font.render("GAME OVER!", 1, fg)
##            textRect = textSurf.get_rect()
##            textRect.center = ((WIDTH/2),(HEIGHT/3))
##            screen.blit(textSurf, textRect)
##            pygame.display.update()
##            bank = 0 #reset score in case it is negative
##            pygame.time.wait(1000)
##            #pygame.quit()

       screen.blit(background_image_blank, [0, 0])

       textSurf = cost_sys_font.render("Cost to Play: 1-4 Quarters", 1, fg)
       textRect = textSurf.get_rect()
       textRect.center = ((WIDTH/2),(HEIGHT/6))
       screen.blit(textSurf, textRect)
       
       textSurf = play_sys_font.render("Press 'GREEN Button' To PLAY", 1, fgGreen)
       textRect = textSurf.get_rect()
       textRect.center = ((WIDTH/2),(HEIGHT/3.5))
       screen.blit(textSurf, textRect)

       textSurf = cashOut_sys_font.render("Press 'RED Button' To CASH OUT", 1, fgRed)
       textRect = textSurf.get_rect()
       textRect.center = ((WIDTH/2),(HEIGHT/2.5))
       screen.blit(textSurf, textRect)
       
       draw_player_data(bank) #update the running data like total bank

       bribe = 0
       adjBribe = 0
       
##only if using raspberry pi
##       try:
##        coinIn = readNumber()
##        if coinIn != 0 & coinIn != 13:
##           print "Arduino: Quarters added: ", coinIn
##           print # skip a line        print "
##           bank = bank + coinIn
##           win1_sound.play()
##           coinIn = 0
##       except:
##           print"IO read error"

       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               print"You QUIT"
               pygame.quit()
               sys.exit()
           elif event.type == pygame.KEYUP:
               if event.key == pygame.K_UP:
                   print"Key hit: 'up key', so program quit"
                   running = False
                   pygame.quit()
           elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_DOWN:
                   print"Key hit: 'down key', so spin again!"
                   if bank <= 0:
                      bank = 1
                   firstSpin = False
                   screen.blit(background_image, [0, 0])
                   pygame.display.update()
                   bank = run_game(bank, cost_pull,reelImages,mybet)
                   screen.blit(background_image, [0, 0])
                   draw_player_data(bank)
                   if bank < cost_pull:
                      print"GAME OVER!"
                      #fill background
                      screen.fill(BACKGROUND_COLOR)
                      textSurf = c_sys_font.render("GAME OVER!", 1, fg)
                      textRect = textSurf.get_rect()
                      textRect.center = ((WIDTH/2),(HEIGHT/3))
                      screen.blit(textSurf, textRect)
                      pygame.display.update()
                      bank = 0 #reset score in case it is negative
                      pygame.time.wait(1000)
                      #pygame.quit()
                      
                      

       pygame.display.update()

if __name__ == '__main__':
    main()
