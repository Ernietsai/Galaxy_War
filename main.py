#載入模組
import asyncio
import pygame
pygame.init()
import os
import random
import time
import math
import copy
import sys
#from cwc import windows

#方便編輯，可有可無
import pygame.display, pygame.mixer, pygame.sprite, pygame.time, pygame.image, pygame.transform, pygame.font
import pygame.joystick, pygame.event, pygame.constants, pygame.display, pygame.draw, pygame.key
import os.path

async def main():
    #顏色設定
    white=(255,255,255)
    black=(0,0,0)
    red=(255,0,0)
    green=(0,255,0)
    blue=(0,0,255)
    orange=(255,165,0)
    yello=(255,255,0)
    SKIBLUE=(0,191,255)
    purple=(160,32,240)
    pink=(255,20,147)


    #設定長、寬
    is_fullscreen = True  #是否全螢幕
    info = pygame.display.Info()  #顯示器尺寸
    if is_fullscreen:
        width = info.current_w  #500
        height = info.current_h  #600
    else:
        width = 500
        height = 600
        

    #初始化
    FPS = 60
    SHOW_DIED_TIME = 5
    FULL_BLOOD = 100
    running     = 1
    GAME_STATE_MEAN = {0:'主選單', 1:'遊戲中', 2:'暫停', 3:'已經死了', 4:'廣告'}
    MENU_STATE, PLAYING_STATE, PAUSING_STATE, DIED_STATE, AD_STATE = 0, 1, 2, 3, 4
    game_state = PLAYING_STATE  #PLAYING_STATE #MENU_STATE
    old_game_state = game_state
    can_change_old_game_state = False
    is_quit    = False
    is_pause   = 0
    pause_time = 0
    wordX = width/2   #-200
    wordY = 10   #200
    voice = 0.4
    score = 100  #0
    blood = 100
    show_blood   = blood
    has_voice    = True
    enemy1_count = enemy2_count = enemy3_count = missile1_count = 0
    most_enemy1  = 5
    most_enemy2  = 3
    most_enemy3  = 3
    most_missile1 = 3
    star_speed   = 2  #星星速度
    start_pause_time = 0
    spaceship_characteristic = 2  #飛船特性
    player_before_site = []
    wav_background_music = pygame.mixer.Sound(os.path.join('music',"Laser-bursts-sound-effect2.wav"))
    channel = pygame.mixer.Channel(0)
    is_pausing_background_music = 0  # {0:False, 1:True}  #背景音樂正在暫停
    have_ad = False
    #need_sign_in = False
    #backgroundx = 0

    #if need_sign_in:
    #    import 輸入密碼

    #初始化pygame
    #print(pygame.constants.FULLSCREEN)
    screen = pygame.display.set_mode((width,height), flags = pygame.constants.RESIZABLE if is_fullscreen else 0)
    clock = pygame.time.Clock()
    pygame.display.set_caption('Galaxy War')
    pygame.display.set_icon(pygame.image.load(os.path.join('picture', '遊戲圖示(小).png')).convert())
    pygame.mixer.init()

    #廣告前使用函式
    def start_ad(surf):  #廣告
        global ad_img_size, ad_img
        surf.fill(black)
        ad_sound = pygame.mixer.Sound(os.path.join('music',"Trap Beat(廣告音樂).wav"))
        ad_sound.play()
        ad_img_size = (int(459*7/10), int(320*7/10))
        ad_img = pygame.transform.scale(pygame.image.load(os.path.join('picture', "廣告2.png")).convert(), ad_img_size)
        ad_img.set_colorkey(black)
        surf.blit(ad_img, (width/2 - ad_img_size[0]/2, height/2 - ad_img_size[1]/2))
        pygame.display.update()


    def stop_ad(surf):
        global start_ad_time
        alpha_background = copy.copy(background)
        ad_x = width/2 - ad_img_size[0]/2
        ad_y = height/2 - ad_img_size[1]/2
        while not(time.time() - start_ad_time >= 6.68) :  #6.68是廣告音樂的長度
            clock.tick(FPS)
            for event in pygame.event.get():#暫停時離開
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        for i in range(0, 255, 3):
            clock.tick(FPS)
            for event in pygame.event.get():#暫停時離開
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            stars.update()
            surf.fill(black)
            #print(alpha_background)#, background.convert_alpha(255-i))
            alpha_background.set_alpha(i)
            surf.blit(alpha_background, (0, 0))
            surf.blit(ad_img, (width/2 - ad_img_size[0]/2, height/2 - ad_img_size[1]/2))
            stars.draw(screen)
            pygame.display.update()
        del start_ad_time


    #廣告前使用類別
    class Star(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = random.uniform(2, 3.5)
            self.image = pygame.Surface((self.size, self.size))
            self.rect = self.image.get_rect()
            pygame.draw.circle(self.image, white, self.rect.center, self.size)
            self.rect.bottom = random.randint(-height*2, 0)#(-height, height)
            self.rect.centerx = random.randint(1, width-1)
        
        def update(self):
            self.rect.centery += star_speed
            if self.rect.top > height:
                self.size = random.uniform(2, 3.5)
                self.image = pygame.Surface((self.size, self.size))
                self.rect = self.image.get_rect()
                pygame.draw.circle(self.image, white, self.rect.center, self.size)
                self.rect.bottom = random.randint(-height, 0)
                self.rect.centerx = random.randint(1, width-1)
            elif self.rect.bottom < 0:
                self.size = random.uniform(2, 3.5)
                self.image = pygame.Surface((self.size, self.size))
                self.rect = self.image.get_rect()
                pygame.draw.circle(self.image, white, self.rect.center, self.size)
                self.rect.top = height
                self.rect.centerx = random.randint(1, width-1)

    #製作星星
    stars = pygame.sprite.Group()
    for i in range(80*2):
        star = Star()
        stars.add(star)


    #廣告
    if have_ad:
        start_ad(screen)
        start_ad_time = time.time()

    #載入背景音樂
    all_background_music_switching_method = {1:'循環播放全部', 2:'隨機播放', 3:'重複播放同一首'}  #所有背景音樂播放模式
    background_music_switching_method = 1  #背景音樂播放模式


    #try:
    all_background_music = []
    '''
        pygame.mixer.Sound(os.path.join('H:\\', "_Alan Walker - Force    Indian-Programmer's.mp3"))  #測試有沒有插記憶卡
        all_background_music = {  #記憶卡裡的音樂
            0:os.path.join('H:\\', "_Alan Walker - Force    Indian-Programmer's.mp3"),
            1:os.path.join('H:\\', "MULICS.wav"),
            2:os.path.join('H:\\',"Wii Music - Gaming Background Music (HD) - Copy.wav"),
            3:os.path.join('H:\\',"Mario-theme-song.mp3"),
            4:os.path.join('H:\\',"Menu Music amazingQ's.mp3"),
            5:os.path.join('H:\\',"TheFatRat - Windfall [Tasty Release].mp3  amazingQ's.wav"),
            6:os.path.join('H:\\',"Treenan Lucasliu9595's.mp3"),
            7:os.path.join('H:\\',"Song  -Zeric-'s.mp3"),
            8:os.path.join('H:\\',"Outro  JC_ProGold's.mp3"),
            9:os.path.join('H:\\',"Among Us Theme Song (Moondai Remix) kemie's.wav"),
            10:os.path.join('H:\\',"Electro-Light - Symbolism kemie's.wav"),
            11:os.path.join('H:\\',"Sunshine kemie's.mp3"),
            12:os.path.join('H:\\',"Tryhard  kemie's.mp3"),
            13:os.path.join('H:\\',"Hello   (KHPe14133,s).wav"),
            14:os.path.join('H:\\',"Nebula   (KHPe14133's).wav"),
            15:os.path.join('H:\\',"Syn Cole - Feel Good [NCS Release]   (KHPe14133,s).wav"),
            16:os.path.join('H:\\',"Unlimited   (KHPe14133,s).mp3")
            }
        '''
    if os.access('H:\\', os.F_OK):
        #file_index = 0
        for file in os.listdir('H:\\'):
            #print(file)
            if os.path.isfile('H:\\' + file):
                #print('x:'+file)
                all_background_music.append('H:\\' + file)
                #file_index += 1
        #del file_index
        print('記憶卡讀取成功')  #記憶卡讀取成功提示
    else:
        print('沒插記憶卡')
        all_background_music = [  #遊戲背景音樂
            os.path.join('music',"Treenan Lucasliu9595's.mp3"),  #0
            os.path.join('music',"Song  -Zeric-'s.mp3"),  #1
            os.path.join('music',"_Alan Walker - Force    Indian-Programmer's.mp3"),  #2
            os.path.join('music',"Among Us Theme Song (Moondai Remix) kemie's.wav")   #3
            ]
    '''
    except: 
        print('沒插記憶卡')
        all_background_music = [  #遊戲背景音樂
        os.path.join('music',"Treenan Lucasliu9595's.mp3"),  #0
        os.path.join('music',"Song  -Zeric-'s.mp3"),  #1
        os.path.join('music',"_Alan Walker - Force    Indian-Programmer's.mp3"),  #2
        os.path.join('music',"Among Us Theme Song (Moondai Remix) kemie's.wav")   #3
        ]
    print(all_background_music)
    '''
    background_music = 9  #random.randint(0,len(all_background_music)-1)  #隨機選一首背景音樂播


    #載入音效
    shoot_sound       = pygame.mixer.Sound(os.path.join('music',"Laser-bursts-sound-effect2.wav"))
    expl_sound        = pygame.mixer.Sound(os.path.join('music',"Bomb-explosion-sound-effect.mp3"))
    enemy_shoot_sound = pygame.mixer.Sound(os.path.join('music',"Shot-navy-artillery-weapons-military-exercise.wav"))

    #設定音量
    pygame.mixer.music.set_volume(voice)
    channel.set_volume(voice)
    shoot_sound.set_volume(voice)
    expl_sound.set_volume(voice)
    enemy_shoot_sound.set_volume(voice * 0.5)

    #載入圖片
    died_expl_size = 180
    background     = pygame.image.load(os.path.join('picture',"空宇宙.png")).convert()
    background     = pygame.transform.scale(background,(width,height))
    menu_background     = pygame.image.load(os.path.join('picture',"遊戲圖示(大).png")).convert()
    menu_background     = pygame.transform.scale(menu_background,(width,height))
    title_picture    = pygame.image.load(os.path.join('picture', "Galaxy war 標題2.png")).convert()
    player_picture   = pygame.image.load(os.path.join('picture', "飛船.png")).convert()
    enemy1_picture   = pygame.image.load(os.path.join('picture', "奇怪飛船.png")).convert()
    enemy2_picture   = pygame.image.load(os.path.join('picture', "敵人2.png")).convert()
    enemy3_picture   = pygame.image.load(os.path.join('picture', "U翼運輸機.png")).convert()
    missile1_picture = pygame.image.load(os.path.join('picture', "飛彈1.png")).convert()
    all_expl = {}
    all_expl['lg']   = []
    all_expl['sm']   = []
    all_expl['died'] = []
    died_expl_img = pygame.image.load(os.path.join('picture',"E0000.png")).convert()
    died_expl_img.set_colorkey(black)
    all_expl['died'].append(pygame.transform.scale(died_expl_img, (died_expl_size, died_expl_size)))
    for i in range(1, 10):
        expl_img = pygame.image.load(os.path.join('picture',f"Effect{i}.png")).convert()
        died_expl_img = pygame.image.load(os.path.join('picture',f"E000{i}.png")).convert()
        expl_img.set_colorkey(black)
        died_expl_img.set_colorkey(black)
        all_expl['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
        all_expl['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
        all_expl['died'].append(pygame.transform.scale(died_expl_img, (died_expl_size, died_expl_size)))
    died_expl = False
    del died_expl_size
    #print(all_expl)

        
    #設定函式
    font_name1=pygame.font.match_font('arial')
    font_name2=pygame.font.SysFont('微軟正黑體',100)
    all_font_name=[font_name1,font_name2]
    #print(all_font_name)

    def draw_text(surf,text,size,color,x,y):
        '''畫出文字'''
        font=pygame.font.Font(all_font_name[0],size)
        text_surface=font.render(text,True,color)
        text_rect=text_surface.get_rect()
        text_rect.centerx=x
        text_rect.top=y
        surf.blit(text_surface,text_rect)


    def draw_blood(surf, blood, x, y, color):
        '''畫出血量'''
        BAR_LENTH = 100
        BAR_height = 10
        blood_rect = pygame.Rect(x, y, BAR_LENTH*(blood/FULL_BLOOD), BAR_height)
        full_rect = pygame.Rect(x, y, BAR_LENTH, BAR_height)
        pygame.draw.rect(surf, color, blood_rect)
        pygame.draw.rect(surf, white, full_rect, 2)


    def choice_background_music(method):
        global background_music
        if  method == '循環播放全部':
            background_music = (background_music + 1) % len(all_background_music)
        elif method == '隨機播放':
            background_music = random.randint(0, len(all_background_music)-1)
        print('現在音樂:' + str(background_music))


    def play_background_music(music):  #, run_time = 1):
        global wav_background_music
        wav_background_music = pygame.mixer.Sound(all_background_music[music % len(all_background_music)])
        channel.play(wav_background_music)
        '''
        if run_time <= 1:
            try:
                pygame.mixer.music.load(all_background_music[music % len(all_background_music)])
                pygame.mixer.music.play(0)
            #except pygame.error as e:
            #    if e == 'Unknown WAVE data format':
            #        wav_background_music = pygame.mixer.Sound(all_background_music[music % len(all_background_music)])
            #        wav_background_music.play()
            except Exception as e:
                try:
                    int(e)
                except:
                    pass
                else:
                    print(f'all_background_music:{all_background_music}')
                try:
                    print(f'F:{os.access(all_background_music[music % len(all_background_music)], os.F_OK)}',
                        f'R:{os.access(all_background_music[music % len(all_background_music)], os.R_OK)}',
                        f'W:{os.access(all_background_music[music % len(all_background_music)], os.W_OK)}',
                        f'X:{os.access(all_background_music[music % len(all_background_music)], os.X_OK)}')
                except Exception as e2:
                    print(e2)
                print(e)
                print('已拔出記憶卡')
                print('現在音樂:', str(music))
                all_background_music = {  #遊戲背景音樂
                0:os.path.join('music',"Treenan Lucasliu9595's.mp3"),
                1:os.path.join('music',"Song  -Zeric-'s.mp3"),
                2:os.path.join('music',"_Alan Walker - Force    Indian-Programmer's.mp3"),
                3:os.path.join('music',"Among Us Theme Song (Moondai Remix) kemie's.wav")
                }
                choice_background_music(all_background_music_switching_method[background_music_switching_method])
                play_background_music(music, run_time + 1)
            
            except pygame.error as e:
                print(e)
                print('已拔出記憶卡')
                print('現在音樂:', str(music))
                all_background_music = {  #遊戲背景音樂
                0:os.path.join('music',"Treenan Lucasliu9595's.mp3"),
                1:os.path.join('music',"Song  -Zeric-'s.mp3"),
                2:os.path.join('music',"_Alan Walker - Force    Indian-Programmer's.mp3"),
                3:os.path.join('music',"Among Us Theme Song (Moondai Remix) kemie's.wav")
                }
                choice_background_music(all_background_music_switching_method[background_music_switching_method])
                play_background_music(music, run_time + 1)
            

        else:
            pygame.mixer.music.load(all_background_music[music % len(all_background_music)])
            pygame.mixer.music.play(0)
        '''


    def check_is_playing_music():
        global all_background_music, background_music, wav_background_music
        if len(all_background_music) != 4 and (not os.access('H:\\', os.F_OK)):  #拔出記憶卡
            wav_background_music.stop()
            print('已拔出記憶卡')
            print('現在音樂:', str(background_music))
            all_background_music = [  #遊戲背景音樂
                os.path.join('music',"Treenan Lucasliu9595's.mp3"),  #0
                os.path.join('music',"Song  -Zeric-'s.mp3"),  #1
                os.path.join('music',"_Alan Walker - Force    Indian-Programmer's.mp3"),  #2
                os.path.join('music',"Among Us Theme Song (Moondai Remix) kemie's.wav")   #3
                ]
        if not channel.get_busy():
            choice_background_music(all_background_music_switching_method[background_music_switching_method])
            play_background_music(background_music)


    def adjust_background_music(event):
        '''調整音量、音軌，並且偵測暫停'''
        global voice, is_pausing_background_music, background_music
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:  #調大聲
                if voice < 1:
                    voice += 0.1
                    pygame.mixer.music.set_volume(voice)
                    channel.set_volume(voice)
                    shoot_sound.set_volume(voice)
                    expl_sound.set_volume(voice)
                    enemy_shoot_sound.set_volume(voice * 0.5)
            if event.key == pygame.K_z:  #調小聲
                if voice > 0:
                    voice -= 0.1
                    channel.set_volume(voice)
                    pygame.mixer.music.set_volume(voice)
                    shoot_sound.set_volume(voice)
                    expl_sound.set_volume(voice)
                    enemy_shoot_sound.set_volume(voice * 0.5)
            if event.key == pygame.K_k:  #暫停
                if is_pausing_background_music == 0:
                    channel.pause()
                    is_pausing_background_music = 1
                elif is_pausing_background_music == 1:
                    channel.unpause()
                    is_pausing_background_music = 0
                else:
                    print(f'錯誤: is_pausing_background_music == {is_pausing_background_music}')
            if is_pause and len(all_background_music) != 4:
                if event.key == pygame.K_LEFT:  #上一首音樂
                    channel.stop()
                    background_music = get_background_music_index('previous')
                    play_background_music(background_music)
                if event.key == pygame.K_RIGHT:  #下一首音樂
                    channel.stop()
                    background_music = get_background_music_index('next')
                    play_background_music(background_music)


    def get_background_music_index(previous_or_next):
        result = background_music
        new_previous_or_next = previous_or_next
        if isinstance(previous_or_next, str):
            new_previous_or_next = new_previous_or_next.lower()
        if new_previous_or_next in [True, 'previous']:
            result += 1
        elif new_previous_or_next in [False, 'next']:
            result -= 1
        #調整範圍，才不會下標越界
        while result < 0:
            result += len(all_background_music)
        while result >=len(all_background_music):
            result -= len(all_background_music)
        return result
        


    #設定類別
    #star以設定過
    '''
    class Star(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = random.uniform(2, 3.5)
            self.image = pygame.Surface((self.size, self.size))
            self.rect = self.image.get_rect()
            pygame.draw.circle(self.image, white, self.rect.center, self.size)
            self.rect.bottom = random.randint(-height, height)
            self.rect.centerx = random.randint(1, width-1)
        
        def update(self):
            self.rect.centery += star_speed
            if self.rect.top > height:
                self.size = random.uniform(2, 3.5)
                self.image = pygame.Surface((self.size, self.size))
                self.rect = self.image.get_rect()
                pygame.draw.circle(self.image, white, self.rect.center, self.size)
                self.rect.bottom = random.randint(-height, 0)
                self.rect.centerx = random.randint(1, width-1)
            elif self.rect.bottom < 0:
                self.size = random.uniform(2, 3.5)
                self.image = pygame.Surface((self.size, self.size))
                self.rect = self.image.get_rect()
                pygame.draw.circle(self.image, white, self.rect.center, self.size)
                self.rect.top = height
                self.rect.centerx = random.randint(1, width-1)
    '''


    class Title_word(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = title_picture #pygame.transform.scale(player_picture,(, ))


    class Bullet(pygame.sprite.Sprite):
        def __init__(self,x,y,speedx,speedy):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface((5,30))
            self.image.fill(red)
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.centery = y
            self.old_speedy = -9
            self.speedx = speedx/3
            self.speedy = self.old_speedy
        
        def update(self):
            #校正        
            if self.rect.bottom<0:
                self.kill()
            #if self.rect.left>width:
            #    self.rect.right=0
            #elif self.rect.right<0:
            #    self.rect.left=width

            #移動
            self.rect.centery += self.speedy
            self.rect.centerx += self.speedx


    class Enemy_bullet(pygame.sprite.Sprite):
        def __init__(self,x,y,speedx,speedy):
            pygame.sprite.Sprite.__init__(self)
            self.name = 'enemy3 bullet'
            self.image = pygame.Surface((5,30))
            self.image.fill(SKIBLUE)
            self.radius = 1
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.centery = y
            self.old_speedy = 9
            self.speedx = speedx/3
            self.speedy = self.old_speedy
            self.hp = 1
        
        def update(self):
            #校正        
            if self.hp <= 0:
                self.kill()
            if self.rect.bottom<0:
                self.kill()
            #if self.rect.left>width:
            #    self.rect.right=0
            #elif self.rect.right<0:
            #    self.rect.left=width

            #移動
            self.rect.centery += self.speedy
            self.rect.centerx += self.speedx


    class Player(pygame.sprite.Sprite):  #不動時有摩擦力
        def __init__(self, type):
            pygame.sprite.Sprite.__init__(self)
            self.type = type
            self.image = pygame.transform.scale(player_picture,(10*7,9*7))#pygame.Surface((50,50))
            self.image.set_colorkey(white)
            #self.image.fill(green)
            self.radius = 32
            self.rect = self.image.get_rect()
            self.rect.centerx = width/2
            self.rect.bottom  = height-20
            self.speedx = 0
            self.speedy = 0
            self.highest_speed = 8
            if self.type == 1:
                self.acceleration  = 0.5
            else:
                self.acceleration = 1.5
            self.slowest_speed = 0.2
            self.Automatic = [0,0,0,0]#上、下、左、右。

        def update(self):
            global player_before_site

            #鍵盤操控
            key_pressed = pygame.key.get_pressed()
            if key_pressed[pygame.K_UP] or key_pressed[pygame.K_w] or self.Automatic[0]:#上
                
                if self.speedy > 0-self.highest_speed:
                    self.speedy -= self.acceleration
                    
            if key_pressed[pygame.K_DOWN] or key_pressed[pygame.K_s] or self.Automatic[1]:#下
                
                if self.speedy < self.highest_speed:
                    self.speedy += self.acceleration
                    
            if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a] or self.Automatic[2]:#左
                
                if self.speedx > 0-self.highest_speed:
                    self.speedx -= self.acceleration
                    
            if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d] or self.Automatic[3]:#右
                
                if self.speedx < self.highest_speed:
                    self.speedx += self.acceleration

            #摩擦力
            if self.type == 1:
                if not(key_pressed[pygame.K_UP] or key_pressed[pygame.K_w] or key_pressed[pygame.K_DOWN] or key_pressed[pygame.K_s]) and self.Automatic[0:2] == [0, 0]:
                    self.speedy*=0.85
                if abs(self.speedy)<self.slowest_speed:
                    self.speedy=0

                if not(key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a] or key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]) and self.Automatic[2:4] == [0, 0]:
                    self.speedx*=0.85
                if abs(self.speedx)<self.slowest_speed:
                    self.speedx=0
            else:
                self.speedy*=0.85
                if abs(self.speedy)<self.slowest_speed:
                    self.speedy=0

                self.speedx*=0.85
                if abs(self.speedx)<self.slowest_speed:
                    self.speedx=0
            #校正        
            if self.rect.left>width:
                self.rect.right=0
            elif self.rect.right<0:
                self.rect.left=width
            if self.rect.bottom>height:
                self.speedy=0
                self.rect.bottom=height
            elif self.rect.top<0:
                self.speedy=0
                self.rect.top=0
            #移動
            self.rect.centery += self.speedy
            self.rect.centerx += self.speedx
            #紀錄位置

            player_before_site.append((self.rect.centerx - self.speedx*5, self.rect.centery - self.speedy*5))
            if len(player_before_site) > 30:
                player_before_site.pop(0)

        def shoot(self):
            shoot_sound.play()
            bullet=Bullet(self.rect.centerx,self.rect.top,self.speedx,self.speedy)
            all_sprite.add(bullet)
            bullets.add(bullet)
            #self.rect.centery+=5


    class Enemy1(pygame.sprite.Sprite):
        def __init__(self):
            global enemy1_count
            pygame.sprite.Sprite.__init__(self)
            enemy1_count += 1
            self.name  = 'enemy1'
            self.image = pygame.transform.scale(enemy1_picture, (43,63))
            self.image.set_colorkey(white)
            self.radius = 22
            self.rect = self.image.get_rect()
            self.rect.right  = random.randint(43,width)
            self.rect.bottom = random.randint(-60,-1)
            self.speedx = random.randint(-3,3)
            self.speedy = random.randint(2,7)
            self.hp = 1 

        def update(self):
            global enemy1_count, score
            #校正        
            if self.hp <= 0:
                explosion = Explosion(self.rect.centerx, self.rect.centery, 'lg')
                all_sprite.add(explosion)
                expl_sound.play()
                score += 5
                self.kill()
            if self.rect.top > height:
                self.kill()
            if self.rect.left > width:
                self.kill()
                #self.rect.right=0
            elif self.rect.right < 0:
                self.kill()
                #self.rect.left=width

            #移動
            self.rect.centery += self.speedy
            self.rect.centerx += self.speedx

        def __del__(self):
            global enemy1_count
            enemy1_count -= 1
            #print("enemy1:", enemy1_count, most_enemy1)


    class Enemy2(pygame.sprite.Sprite):
        def __init__(self):
            global enemy2_count
            pygame.sprite.Sprite.__init__(self)
            enemy2_count += 1
            self.name = 'enemy2'
            self.old_image = pygame.transform.scale(enemy2_picture,(43,63))
            self.old_image.set_colorkey(white)
            self.image = self.old_image.copy()
            self.radius = 22
            self.rect = self.image.get_rect()
            self.rect.right = random.randint(43,width)
            self.rect.bottom = random.randint(-60,-1)
            if player_before_site[len(player_before_site)-1][1]-self.rect.centery == 0 and player_before_site[len(player_before_site)-1][0]-self.rect.centerx < 0:
                self.direction = 180
            else:
                try:
                    self.direction = math.atan((player_before_site[len(player_before_site)-1][1]-self.rect.centery)/(player_before_site[len(player_before_site)-1][0]-self.rect.centerx))*(180/math.pi)
                except ZeroDivisionError:
                    if (player_before_site[len(player_before_site)-1][1]-self.rect.centery) > 0:
                        self.direction = -90
                    else:
                        self.direction = 90
                if player_before_site[len(player_before_site)-1][0]-self.rect.centerx < 0:
                    self.direction = (self.direction +180)%360
            self.speed  = random.uniform((0 ** 2 + 2 ** 2) ** 0.5+2, (3**2 + 7**2)**0.5)
            self.speedx = self.speed*math.cos(self.direction/(180/math.pi))
            self.speedy = self.speed*math.sin(self.direction/(180/math.pi))
            self.hp = 1
            #print(self.direction, self.speed, self.speedx, self.speedy)
            #self.angle  = 0

        def rotate(self):
            self.image = pygame.transform.rotate(self.old_image, (0-self.direction)-90+180)
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        def update(self):
            global enemy2_count, score
            #校正        
            if self.hp <= 0:
                explosion = Explosion(self.rect.centerx, self.rect.centery, 'lg')
                all_sprite.add(explosion)
                expl_sound.play()
                #enemy2_count -=1
                score += 5
                self.kill()
            if self.rect.top>height:
                #enemy2_count -=1
                self.kill()
            '''
            if self.rect.left>width:
                self.kill()
                #self.rect.right=0
            elif self.rect.right<0:
                self.kill()
                #self.rect.left=width
            '''

            #改變方向
            self.relative_locationx = player_before_site[len(player_before_site)-1][0]-self.rect.centerx
            self.relative_locationy = player_before_site[len(player_before_site)-1][1]-self.rect.centery
            try:
                self.direction = math.atan(self.relative_locationy/self.relative_locationx)*(180/math.pi)
            except ZeroDivisionError:
                if self.relative_locationy > 0:
                    self.direction = 90
                else:
                    self.direction = -90
            #if int(now_time) % 10 == 0:
                #print(player_before_site[len(player_before_site)-1][0], self.rect.centerx, sep = '  ')
            if self.relative_locationx < 0:
                self.direction = (self.direction + 180) % 360
            self.speedx = self.speed*math.cos(self.direction/(180/math.pi))
            self.speedy = self.speed*math.sin(self.direction/(180/math.pi))
            self.rotate()

            #移動
            self.rect.centery += self.speedy
            self.rect.centerx += self.speedx

        def __del__(self):
            global enemy2_count
            enemy2_count -= 1
            #print(enemy2_count, most_enemy2)


    class Enemy3(pygame.sprite.Sprite):
        def __init__(self):
            global enemy3_count
            pygame.sprite.Sprite.__init__(self)
            enemy3_count += 1
            self.name  = 'enemy3'
            self.image = pygame.transform.scale(enemy3_picture, (90, 100))#(43,63))
            self.image.set_colorkey(white)
            self.radius = 50
            self.rect = self.image.get_rect()
            self.rect.right  = random.randint(43,width)
            self.rect.bottom = random.randint(-60,-1)
            self.speedx = random.randint(-3,3)
            self.speedy = random.randint(2,7)
            self.shoot_interval = 1.5
            self.last_shoot_time = now_time - self.shoot_interval + 0.5
            self.hp = 2

        def update(self):
            global enemy3_count, score
            #校正        
            if self.hp <= 0:
                explosion = Explosion(self.rect.centerx, self.rect.centery, 'lg')
                all_sprite.add(explosion)
                expl_sound.play()
                enemy3_count -= 1
                score += 5
                self.kill()
            if self.rect.top>height:
                enemy3_count -=1
                self.kill()
            if self.rect.left>width:
                enemy3_count -=1
                self.kill()
                #self.rect.right=0
            elif self.rect.right<0:
                enemy3_count -=1
                self.kill()
                #self.rect.left=width

            #射子彈
            if now_time - self.last_shoot_time >= self.shoot_interval:
                self.shoot()

            #移動
            self.rect.centery += self.speedy
            self.rect.centerx += self.speedx

        def shoot(self):
            enemy_shoot_sound.play()
            enemy_bullet = Enemy_bullet(self.rect.centerx, self.rect.centery + 30, self.speedx, self.speedy)
            all_sprite.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
            self.last_shoot_time = now_time
            #self.rect.centery+=5


    class Missile1(pygame.sprite.Sprite):
        def __init__(self, x, y):
            global missile1_count
            pygame.sprite.Sprite.__init__(self)
            self.old_image = pygame.transform.scale(missile1_picture,(43,63))
            self.old_image.set_colorkey(white)
            self.image = self.old_image.copy()
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.centery = y
            self.speedx = 0
            self.speedy = random.uniform(-11.0, -9.0)
            self.speed  = 0
            self.fastest_speed  = random.uniform(12.0, 14.0)
            self.add_speedx     = 0
            self.add_speedy     = 0
            self.air_resistance = 0
            self.fastest_add_speed = random.uniform(4.0, 7.0)
            self.hp = 1
            self.name = 'missile1'
            missile1_count += 1
        
        def update(self):
            global score
            if self.hp <= 0:
                explosion = Explosion(self.rect.centerx, self.rect.centery, 'lg')
                all_sprite.add(explosion)
                expl_sound.play()
                score += 5
                self.kill()
            self.fly((player.rect.centerx, player.rect.centery))

        def rotate(self, angle):
            self.image = pygame.transform.rotate(self.old_image, (0 - angle) + 90 + 180)
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        def fly(self, destination):
            x_distance = destination[0] - self.rect.centerx
            y_distance = destination[1] - self.rect.centery
            destination_distance = (x_distance ** 2 + y_distance ** 2) **0.5
            destination_direction = self.get_angle(x_distance, y_distance)
            self.rotate(destination_direction)
            if destination_distance < self.fastest_add_speed:
                self.add_speedx = x_distance * 0.05
                self.add_speedy = y_distance * 0.05
            else:
                self.add_speedx = (self.fastest_add_speed * ((x_distance / destination_distance) if destination_distance != 0 else 0)) * 0.05
                self.add_speedy = (self.fastest_add_speed * ((y_distance / destination_distance) if destination_distance != 0 else 0)) * 0.05
            self.speedx += self.add_speedx - (self.air_resistance * ((self.speedx / self.speed) if self.speed != 0 else 0))
            self.speedy += self.add_speedy - (self.air_resistance * ((self.speedy / self.speed) if self.speed != 0 else 0))
            self.speed   = (self.speedx ** 2 + self.speedy ** 2) ** 0.5
            self.air_resistance = ((self.add_speedx * (self.speed / self.fastest_speed)) ** 2 + (self.add_speedy * (self.speed / self.fastest_speed)) ** 2) ** 0.5
            self.rect.centerx  += self.speedx
            self.rect.centery  += self.speedy

        def get_angle(self, x, y):
            if x == 0:
                if y == 0:
                    return 180
                elif y > 0:
                    return 180
                elif y < 0:
                    return 0
            elif y == 0:
                if x > 0:
                    return 90
                elif x < 0:
                    return -90
            else:
                angle = math.atan(y / x) * (180 / math.pi)
                if x < 0:
                    angle += 180
                return angle

        def __del__(self):
            global missile1_count
            missile1_count -= 1


    class Explosion(pygame.sprite.Sprite):
        def __init__(self, x, y, size):
            pygame.sprite.Sprite.__init__(self)
            self.size = size
            self.image = all_expl[self.size][0]
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.centery = y
            self.now_img = 0
            self.last_update = now_time
            self.img_change_time = 50*10**-3
            #expl_sound.play()

        def update(self):
            global died_expl
            now = now_time
            if now-self.last_update >= self.img_change_time:
                self.now_img += 1
                if self.now_img >= len(all_expl[self.size]):
                    if self.size == 'died':
                        self.rect.centerx =-1000
                        if now-self.last_update >= 1:
                            died_expl = 'finish'
                            self.kill()
                    else:
                        self.kill()
                else:
                    center = (self.rect.centerx, self.rect.centery)
                    self.image = all_expl[self.size][self.now_img]
                    self.rect = self.image.get_rect()
                    self.rect.centerx = center[0]
                    self.rect.centery = center[1]
                    self.last_update = now_time

    all_sprite    = pygame.sprite.Group()
    players       = pygame.sprite.Group()
    enemys        = pygame.sprite.Group()
    bullets       = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()


    #製作玩家
    player = Player(spaceship_characteristic)
    all_sprite.add(player)
    players.add(player)


    if have_ad:
        stop_ad(screen)


    #遊戲迴圈
    start_game_time=time.time()
    now_time=0
    while running:
        clock.tick(FPS) 
        width, height = screen.get_size()
        #輸入
        for event in pygame.event.get():  #鍵盤事件和關閉

            if event.type == pygame.QUIT:  #關閉
                running = False

            if event.type == pygame.VIDEORESIZE:  #視窗大小改變
                # 動態重新設定畫面尺寸
                screen = pygame.display.set_mode(
                    (event.w, event.h), 
                    pygame.RESIZABLE
                )

            if event.type == pygame.KEYDOWN:  #按鍵盤

                adjust_background_music(event)

                if event.key == pygame.K_SPACE:  #按空白鍵
                    if game_state == PLAYING_STATE:  #發射子彈
                        player.shoot()

                if event.key == pygame.K_p:  #按P鍵
                    if game_state == PLAYING_STATE:  #暫停
                        is_pause = 1
                        game_state = PAUSING_STATE

        if game_state == MENU_STATE:
            if old_game_state != MENU_STATE:
                can_change_old_game_state = True
            screen.blit(menu_background, (0, 0))
            pygame.display.update()
            pass


        if game_state == PAUSING_STATE:  #is_pause:#暫停時
            #print(old_game_state)
            if old_game_state != PAUSING_STATE:
                can_change_old_game_state = True
                #game_state = PAUSING_STATE
                channel.pause()
                is_pausing_background_music = 1
                #pygame.mixer.music.pause()
                start_pause_time = now_time
                #draw_text(screen,'pausing……',100,pink,width/2,200)
                pygame.display.update()
                transparency = [0]
                transparency_change=1
            #while is_pause and running :
            #clock.tick(FPS)

            check_is_playing_music()
            screen.fill(blue)
            screen.blit(background,(0,0))
            #stars.update()
            stars.draw(screen)
            all_sprite.draw(screen)
            if blood > 0:                            #↓以前是100
                draw_text(screen,'score:'+str(score),50,orange,wordX,wordY)
            else:
                draw_text(screen,'Game over',100,purple,width/2,200)
                running=0
            draw_blood(screen, show_blood, 5, 15, green)

            pausing = all_font_name[1].render('pausing......',1,pink)#+tuple(transparency))
            try:
                #if transparency[0] >= 5:
                pausing.set_alpha(transparency[0])
            except:
                print(transparency)
                running = 0
            screen.blit(pausing, (width/2-200,250))
            #draw_text(screen,'pausing……',100,pink+tuple(transparency),width/2,200)
            transparency[0] += 5.1*transparency_change
            if transparency[0] > 300 or transparency[0] < 0:
                transparency_change *= -1
                #print(transparency)
            for event in pygame.event.get():#暫停時離開
                if event.type == pygame.QUIT:
                    running = 0
                if event.type == pygame.KEYDOWN:
                    adjust_background_music(event)
                    if event.key == pygame.K_p:#繼續玩
                        is_pause = 0
                        game_state = PLAYING_STATE
            pygame.display.update()

        if game_state != PAUSING_STATE and old_game_state == PAUSING_STATE:
            channel.unpause()
            is_pausing_background_music = 0
            #pygame.mixer.music.unpause()
            pause_time+=time.time()-start_game_time-pause_time-start_pause_time

        '''
        wordX-=5
        if wordX>850:
            wordX=-200
        if wordX<-200:
            wordX=850
            '''

        if game_state == PLAYING_STATE:
            if old_game_state != PLAYING_STATE:
                can_change_old_game_state = True

            #更新
            check_is_playing_music()
            #if not pygame.mixer.music.get_busy():
            #    choice_background_music(all_background_music_switching_method[background_music_switching_method])
            #    play_background_music(background_music)
                
            now_time=time.time() - start_game_time-pause_time
            all_sprite.update()
            stars.update()
            while score >= 0 and score <= 90 and enemy1_count < most_enemy1 and not died_expl:#加敵人1
                enemy1=Enemy1()
                all_sprite.add(enemy1)
                enemys.add(enemy1)

            while score >= 30 and enemy2_count < most_enemy2 and not died_expl:#加敵人2
                most_enemy1 = 2
                enemy2=Enemy2()
                all_sprite.add(enemy2)
                enemys.add(enemy2)

            while score >= 90 and enemy3_count < most_enemy3 and not died_expl:#加敵人3
                most_enemy1 = 1
                most_enemy2 = 2
                enemy3=Enemy3()
                all_sprite.add(enemy3)
                enemys.add(enemy3)
            
            while score >= 20 and missile1_count < most_missile1 and not died_expl:#加飛彈
                missile1 = Missile1(random.randint(0,width), random.randint(-60,-1))
                all_sprite.add(missile1)
                enemys.add(missile1)

            hits=pygame.sprite.groupcollide(enemys, bullets, 0, 1)#射敵人
            if not hits=={}:
                #print(type(hits))
                for hit1 in hits:
                    hit1.hp -= 1
                    if hit1.hp > 0:
                        for hit2 in hits[hit1]:
                            explosion = Explosion(hit2.rect.centerx, hit2.rect.centery, 'sm')
                            all_sprite.add(explosion)
                            expl_sound.play()
                    '''
                    if hit1.name == 'enemy1':
                    enemy1_count -= 1
                    elif hit1.name == 'enemy2':
                        enemy2_count -= 1
                    elif hit1.name == 'enemy3':
                        enemy3_count -= 1
                    score+=5
                    '''

            hits=pygame.sprite.groupcollide(enemys,players,1,0,pygame.sprite.collide_circle)#被敵人撞
            if not hits=={}:
                #print(type(hits))
                for hit1 in hits:
                    explosion = Explosion(hit1.rect.centerx, hit1.rect.centery, 'sm')
                    all_sprite.add(explosion)
                    expl_sound.play()
                    hit1.kill()
                    if hit1.name == 'enemy1':
                        pass
                    elif hit1.name == 'enemy2':
                        pass
                    elif hit1.name == 'enemy3':
                        enemy3_count -= 1
                    elif hit1.name == 'missile1':
                        pass
                    blood -= 10

            hits=pygame.sprite.groupcollide(enemy_bullets,players,1,0,pygame.sprite.collide_circle)#被敵人射
            if not hits=={}:
                for hit1 in hits:
                    explosion = Explosion(hit1.rect.centerx, hit1.rect.centery, 'sm')
                    all_sprite.add(explosion)
                    expl_sound.play()
                    hit1.kill()
                    if hit1.name == 'enemy1':
                        pass
                    elif hit1.name == 'enemy2':
                        pass
                    elif hit1.name == 'enemy3':
                        #enemy3_count -= 1
                        pass
                    blood -= 5

            hits=pygame.sprite.groupcollide(enemy_bullets, bullets, 0, 1)#射敵人的子彈
            if not hits=={}:
                for hit1 in hits:
                    hit1.hp -= 1
                    if hit1.hp > 0:
                        for hit2 in hits[hit1]:
                            explosion = Explosion(hit2.rect.centerx, hit2.rect.centery, 'sm')
                            all_sprite.add(explosion)
                            expl_sound.play()


            if blood < 0:
                blood = 0
            if blood > show_blood:
                show_blood += 1
            elif blood < show_blood:
                show_blood -= 1
            
            #most_enemy1 = score//100+1
                
            #除錯資訊
            '''
            if int(now_time) % 1 == 0:
                os.system('cls')
                print(enemy2.direction)
            '''
            #顯示

            screen.fill(blue)
            screen.blit(background,(0,0))
            stars.draw(screen)
            all_sprite.draw(screen)
            if show_blood > 0:                            #↓以前是100
                draw_text(screen,'score:'+str(score),50,orange,wordX,wordY)
            else:
                if not died_expl:
                    died_expl = Explosion(player.rect.centerx, player.rect.centery, 'died')
                    old_player_x = player.rect.centerx
                    all_sprite.add(died_expl)
                    expl_sound.play()
                player.rect.centerx = -2000
                draw_text(screen,'score:'+str(score),50,orange,wordX,wordY)
                if died_expl == 'finish':
                    draw_text(screen,'Game over',100,purple,width/2,200)
                    game_state = DIED_STATE
            draw_blood(screen, show_blood, 5, 15, green)
            pygame.display.update()

            '''print(running, show_blood)
            if show_blood <= 0:  #(not running) and   #校正 running 和 game_state
                print(running, game_state)
                running = True
                game_state = DIED_STATE'''


            
        if game_state == DIED_STATE:  #blood <= 0:  #死了

            if old_game_state != DIED_STATE:
                can_change_old_game_state = True
                player.kill()
                del players
                start_died_time = time.time()

            #while not is_quit:# and not time.time() - start_died_time >= SHOW_DIED_TIME:
                #clock.tick(FPS)
            check_is_playing_music()
                #if not pygame.mixer.music.get_busy():
                #    choice_background_music(all_background_music_switching_method[background_music_switching_method])
                #    play_background_music(background_music)
            for event in pygame.event.get():  #離開和音量
                    if event.type == pygame.QUIT:  #離開
                        running = False
                    if event.type==pygame.KEYDOWN:
                        if is_fullscreen and event.key == pygame.K_q:  #離開
                            running = False
                        
                        '''if is_fullscreen and event.key == pygame.K_r:  #繼續遊玩
                            #製作玩家
                            print('restart')
                            player = Player(spaceship_characteristic)
                            all_sprite.add(player)
                            players.add(player)
                            blood = 100
                            score = 0
                            game_state = PLAYING_STATE'''
                        
                        adjust_background_music(event)
            stars.update()
            all_sprite.update()
            screen.fill(blue)
            screen.blit(background, (0, 0))
            stars.draw(screen)
            all_sprite.draw(screen)
            draw_text(screen, 'score:' + str(score), 50, orange, wordX, wordY)
            draw_text(screen, 'Game over', 100, purple, width / 2, 200)
            draw_blood(screen, show_blood, 5, 15, green)
            pygame.display.update()

        if can_change_old_game_state:
            old_game_state = game_state
            can_change_old_game_state = False
        await asyncio.sleep(0)
asyncio.run(main())
'''
if blood <= 0:
    start_died_time = time.time()
    while not is_quit and not time.time() - start_died_time >= (50*10**-3)*10 + 1:
        clock.tick(FPS)
        for event in pygame.event.get():#暫停時離開
                if event.type == pygame.QUIT:
                    is_quit = 1
'''
pygame.quit()
