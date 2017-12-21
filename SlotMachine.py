import os
import pygame
from pygame.locals import *
import random
from numpy.random import choice
import numpy as np

pygame.init()

SIZE = WIDTH, HEIGHT = 640, 480
BACKGROUND_COLOR = pygame.Color('black')
FPS = 80

screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
time = pygame.time

#load font, prepare values
font = pygame.font.Font(None, 80)
text = 'Fonty'
size = font.size(text)

fg = 250, 250, 250 #font color
bg = 5, 5, 5
   
a_sys_font = pygame.font.SysFont("Arial", 30)
b_sys_font = pygame.font.SysFont("Arial", 40)
c_sys_font = pygame.font.SysFont("Arial", 60)
d_sys_font = pygame.font.SysFont("Arial", 25)
e_sys_font = pygame.font.SysFont("Arial", 10)

#table for probablities for selecting final reel image
#weighted towards hex and demons
#each reel gets a different probability
PROBABILTY1=[0.05,0.31,0.07,0.14,0.17,0.16,0.01,0.01,0.01,0.06,0.01]
PROBABILTY2=[0.01,0.2,0.01,0.21,0.2,0.21,0.01,0.01,0.01,0.06,0.07]
PROBABILTY3=[0.21,0.05,0.21,0.09,0.05,0.02,0.11,0.02,0.06,0.06,0.12]

#set normal probability to start
PROBABILTY = PROBABILTY1
#number of images loaded from image folder
IMAGES_N = 11

if IMAGES_N <> len(PROBABILTY):
   print"number of images and probability array length do not match!"
          
background_image = pygame.image.load("slot_background_images/devils_delight_wallpaper_640_480.png").convert()
background_image_blank = pygame.image.load("slot_background_images/devils_delight_wallpaper_640_480_blank.png").convert()

#icon for app window
icon = pygame.image.load('slot_misc_images/icon.png')
pygame.display.set_icon(icon)
pygame.display.set_caption("Devil's Bargain")

pygame.mixer.init()

#create background music for the game
pygame.mixer.music.load("slot_sounds/gravewalk.ogg")
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

#set up event clock(s)
pygame.time.set_timer(USEREVENT+1, 50)



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
    reel1 = AnimatedSprite(position=(15, 10), images=imageArr)
    #random.shuffle(imageArr)
    reel2 = AnimatedSprite(position=(225, 10), images=imageArr)
    #random.shuffle(imageArr)
    reel3 = AnimatedSprite(position=(435, 10), images=imageArr)

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

def populate_names_cats():
    # name_decoder- array of image names based on index position in 'images' array
    name = ["Dice", "Hex", "666", "Demon", "Devil Girl",
                    "Satan", "Tomestone Q", "Tomestone K", "Tomestone A", "Evil Cow", "God Cow"]
    catagory = ["Satanic", "Satanic", "Satanic", "Demon", "Demon", "Demon", "Grave", "Grave", "Grave",
                     "Special", "xSpecial"]
    #print"len(name_decoder): "+repr(len(name_decoder))
    return (name, catagory)

def check_input():
    for event in pygame.event.get():
     if event.type == pygame.KEYDOWN:
         if event.key == pygame.K_DOWN:
            print"In check_input fxn, Key hit: down detected, QUIT"
            pygame.quit()
            sys.exit()
    return index

def draw_player_data(bank):
   textSurf = a_sys_font.render("Player Soul Bank: $"+("{:.2f}".format(bank)), 1, fg)
   textRect = textSurf.get_rect()
   textRect.center = (10, HEIGHT-40)
   screen.blit(textSurf, textRect)

def score_update(current, total, bonusNum, bonusName, bonusCat, specialCat, xspecialCat):

   print"length of bonusNum: "+repr(len(bonusNum))
   print"bonusName: "+bonusName
   print"bonusCat: "+bonusCat
   nameScore = bonusNum[0]
   catScore = bonusNum[1]
   specialScore = bonusNum[2]
   xspecialScore = bonusNum[3]
   text_y = 180 #start text here
   text_height = 40 #increment y by this
   
   subscoreName = a_sys_font.render("Bonus: $"+repr(nameScore)+" "+bonusName+" ", 1, fg)
   screen.blit(subscoreName, (5, text_y))
   pygame.display.update()
   if bonusName > 0:
      win1_sound.play()
   pygame.time.wait(500)
   text_y = text_y + text_height

   subscore_cat = a_sys_font.render("Multiplier: X"+repr(catScore), 1, fg)
   screen.blit(subscore_cat, (5, text_y))
   pygame.display.update()
   if catScore > 0:
      win1_sound.play()
   pygame.time.wait(500)
   text_y = text_y + text_height
   
   subscore_total = a_sys_font.render("**Sub Total: $"+repr(catScore*nameScore)+"**", 1, fg)
   screen.blit(subscore_total, (5, text_y))
   pygame.display.update()
   if catScore*nameScore > 0:
      win1_sound.play()
   else:
      lose_sound.play()
   pygame.time.wait(800)
   text_y = text_y + text_height + 5

   if specialScore > 0:
      subscore_special = a_sys_font.render("Add Special: $"+repr(specialScore)+" "+specialCat+" ", 1, fg)
      screen.blit(subscore_special, (5, text_y))
      pygame.display.update()
      text_y = text_y + text_height
      win2_sound.play()
      pygame.time.wait(500)
   else:
      text_y = text_y
   
   if xspecialScore <> 0:
      subscore_xspecial = a_sys_font.render("Wrath of God: $"+repr(xspecialScore)+" "+xspecialCat+" ", 1, fg)
      screen.blit(subscore_xspecial, (5, text_y))
      pygame.display.update()
      win4_sound.play()
      text_y = text_y + text_height + 4
      pygame.time.wait(500)
   else:
      text_y = text_y + 4 
   
   pygame.draw.lines(screen, fg, False, [(5, text_y), (300,text_y)], 3)
   pygame.time.wait(500)
   #text_y = text_y + text_height
   
   ren1 = a_sys_font.render("Current Score: $"+repr(current), 1, fg)
   screen.blit(ren1, (5, text_y))
   pygame.display.update()
   if current > 0:
      win3_sound.play()
   else:
      noPoints_sound.play()
   pygame.time.wait(1200)

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
           screen.blit(images[final_reel1], (15,10))
           
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
           screen.blit(images[final_reel1], (15,10))
           screen.blit(images[final_reel2], (225,10))
           
        else:
           print"Game over!"
           reelSpin3.stop()
           reelImageSounds[final_reel2].stop()
           reelImageSounds[final_reel3].play()
           screen.blit(images[final_reel1], (15,10))
           screen.blit(images[final_reel2], (225,10))
           screen.blit(images[final_reel3], (435,10))        
           running = False
           
        #all_sprites.update(dt,USEREVENT+1)  # Calls the 'update' method on all sprites in the list.
        #print"pygame.time.get_ticks: " + repr(time.get_ticks())
        #all_sprites.draw(screen)
        #screen.fill(BACKGROUND_COLOR)
        pygame.display.update()
        pygame.event.pump()

def redraw_static_reels(images, final_reel1, final_reel2, final_reel3):
    screen.blit(images[final_reel1], (15,10))
    screen.blit(images[final_reel2], (225,10))
    screen.blit(images[final_reel3], (435,10))
    pygame.display.update()

def run_game(bank, cost):

       #load the reel images
       #Make sure to provide the relative or full path to the images directory.
       reelImages = load_images(path='slot_images')

       #polulate the names of each image and the catagory into name_decoder, catagory_decoder arrays
       name_decoder, catagory_decoder = populate_names_cats()

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

       # puase after reels have all stopped
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
       
       finalScore = (scoreName * scoreCat) + score_special + score_xspecial
       
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

       score_update(finalScore, bank, bonusNums, bonusName, bonusCat, specialCat, xspecialCat)

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

        size = (185, 150)  # This should match the size of the images.

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

        
def main():

   #reset scores
   print"reset scores...."
   finalScore = 0.00 #current reels
   bank = 1.00 #total bank, start with 0
   cost_pull = 1.00 #cost per pull
   repullMultiplier = 0.25 #mult bank if repull before cashout
   running = True
   #draw intro screen
   
##   textSurf = b_sys_font.render("Soul Cost $1", 1, fg)
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

   firstSpin = True #change to false after first spin
   
   while (running):

       screen.blit(background_image_blank, [0, 0])

       textSurf = b_sys_font.render("Soul Cost $1", 1, fg)
       textRect = textSurf.get_rect()
       textRect.center = ((WIDTH/2),(HEIGHT/6))
       screen.blit(textSurf, textRect)
       
       textSurf = b_sys_font.render("Press Down Arrow To Sell Soul", 1, fg)
       textRect = textSurf.get_rect()
       textRect.center = ((WIDTH/2),(HEIGHT/2.5))
       screen.blit(textSurf, textRect)

       draw_player_data(bank) #update the running data like total bank

       #pygame.display.update()

       bribe = 0
       
       if firstSpin == False:
          if bank > 2:
             bribe = bank*repullMultiplier
             if bribe > 2:
                adjBribe = 2
                textSurf = e_sys_font.render("* Up to $2 Maximum", 1, fg, bg)
                textRect = textSurf.get_rect()
                textRect.center = ((WIDTH/2),(HEIGHT/(3)))
                screen.blit(textSurf, textRect)
             else:
                adjBribe = bribe
             textSurf = d_sys_font.render("Devil's Bargain*: Soul Bank"
                                          +" X "
                                          +"{:.2f}".format(repullMultiplier)
                                          +" = $"
                                          +"{:.2f}".format(adjBribe)
                                          +" bribe to spin again", 1, fg, bg)
             textRect = textSurf.get_rect()
             textRect.center = ((WIDTH/2),(HEIGHT/(4)))
             screen.blit(textSurf, textRect)
      
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
                  # double bank for repeat pull!
                   if bank > 1:
                      if bribe > 2:
                         adjBribe = 2
                         textSurf = d_sys_font.render("* Up to $2 Maximum", 1, fg, bg)
                         textRect = textSurf.get_rect()
                         textRect.center = ((WIDTH/2),(HEIGHT/(3)))
                         screen.blit(textSurf, textRect)
                   else:
                      adjBribe = bribe
                   bank = bank + adjBribe
                   firstSpin = False
                   screen.blit(background_image, [0, 0])
                   pygame.display.update()
                   bank = run_game(bank, cost_pull)
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
                      pygame.time.wait(5000)
                      #pygame.quit()
                      
                      

       pygame.display.update()

if __name__ == '__main__':
    main()
