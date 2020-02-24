# 游戏原理：和动画原理相同，快速切换图片
# 为了避免上一次贴图，每次刷新前，重贴所有图片

# 游戏类：Game
# 属性：window窗口(512,768)
# 背景图
# 方法：
# 贴图 draw
# 刷新 update
# 运行
# 英雄飞机类
# 属性：飞机图片 img
# 飞机坐标 x,y
# 方法：移动  move
# 发射子弹 fire
# 子弹类
# 属性：子弹图片 img
# 子弹坐标 x,y
# 方法：向上移动  move_up
# 敌机类
# 属性：敌机图片 img
# 敌机坐标
# 方法：向下移动 move_down
# 地图类
# 属性：地图图片 img
# 地图坐标
# 方法：向下移动 move_down
import random

import pygame
import time
import sys

# while True:
#     window = pygame.display.set_mode((512,768))# 创建窗口
#     image = pygame.image.load("res/img_bg_level_2.jpg")# 加载图片文件，返回图片对象
#     window.blit(image,(0,0))# 贴图（指定坐标，将图片绘制到窗口）
#     pygame.display.update()# 刷新界面  不刷新不会更新显示的内容
WINDOWS_H = 768  # 窗口高度
WINDOWS_W = 512  # 窗口宽度
ENEMY_COUNT = 8
ENEMY_SPEED = 10
HERO_PLANE_SPEED = 12
HERO_PLANE_BULLET_SPEED = 14


class Item:  # 把重复代码写成基类，让其他类继承
    def __init__(self, img, x, y):
        self.x = x
        self.y = y
        self.img = pygame.image.load(img)


class Boss(Item):
    def __init__(self, img, x, y):
        super(Boss, self).__init__(img, x, y)
        self.move = "左"
        self.boss_bullets = []

    def boss_move(self):
        if self.x >= 0 and self.move == "左":
            self.x -= 3
        else:
            self.move = "右"
        if self.x <= WINDOWS_W - 50 and self.move == "右":
            self.x += 3
        else:
            self.move = "左"

    def boss_fire(self):
        bullet = Bullet("res/bullet_2.png", self.x + 50 - 10, self.y + 68)  # 创建子弹对象
        self.boss_bullets.append(bullet)


class Map(Item):
    def __init__(self, img, x, y):
        super(Map, self).__init__(img, x, y)
        self.x2 = x
        self.y2 = y - WINDOWS_H
        self.img2 = pygame.image.load(img)

    def move_down(self):
        self.y += 4
        self.y2 += 4


class Enemy(Item):
    def __init__(self, img, x, y):
        super(Enemy, self).__init__(img, x, y)
        self.enemy_is_hited = False  # 敌机碰撞属性，初始为False

    def move_down(self):
        self.y += ENEMY_SPEED


class Bullet(Item):
    def move_up(self):
        self.y -= HERO_PLANE_BULLET_SPEED

    def move_down(self):
        self.y += HERO_PLANE_BULLET_SPEED

    def __del__(self):
        print("子弹消失了")

    def hero_bullet_is_hited(self, enemy_plane):  # 敌机和子弹相撞
        bullet_rect = pygame.Rect(self.x, self.y, 20, 31)  # 子弹矩形区域
        enemy_rect = pygame.Rect(enemy_plane.x, enemy_plane.y, 100, 68)
        # 判断两个矩形是否相交，相交返回True, 否则返回False
        flag = pygame.Rect.colliderect(bullet_rect, enemy_rect)
        return flag


class HeroPlane(Item):
    def __init__(self, img, x, y):
        super(HeroPlane, self).__init__(img, x, y)
        self.bullets = []  # 把子弹对象存到列表中

    def move_left(self):
        self.x -= HERO_PLANE_SPEED

    def move_right(self):
        self.x += HERO_PLANE_SPEED

    def move_up(self):
        self.y -= HERO_PLANE_SPEED

    def move_down(self):
        self.y += HERO_PLANE_SPEED

    def fire(self):
        bullet = Bullet("res/bullet_9.png", self.x + 50 - 10, self.y - 31)  # 创建子弹对象
        self.bullets.append(bullet)

    def hero_enemy_hited(self, enemy_plane):  # 敌机和我方飞机相撞
        hero_rect = pygame.Rect(self.x, self.y, 100, 68)  # 我方飞机矩形区域
        enemy_rect = pygame.Rect(enemy_plane.x, enemy_plane.y, 100, 68)  # 敌机矩形区域
        # 判断两个矩形是否相交，相交返回True, 否则返回False
        flag = pygame.Rect.colliderect(hero_rect, enemy_rect)
        return flag


class Game:
    def __init__(self):
        pygame.init()
        # 加载背景音乐
        pygame.mixer.music.load("./res/bg2.ogg")
        # 循环播放背景音乐
        pygame.mixer.music.play(-1)
        # 生成敌机爆炸音效对象
        self.boom_sound = pygame.mixer.Sound("./res/baozha.ogg")
        # 生成敌机爆炸音效对象
        self.shoot_sound = pygame.mixer.Sound("./res/bullet2.wav")
        # 生成游戏结束音效对象
        self.gameover_sound = pygame.mixer.Sound("./res/gameover.wav")
        self.window = pygame.display.set_mode((WINDOWS_W, WINDOWS_H))  # 创建窗口
        # self.bg_image = pygame.image.load("res/img_bg_level_2.jpg")  # 加载图片文件，返回图片对象
        self.map = Map("res/img_bg_level_2.jpg", 0, 0)  # 加载地图图片
        self.hero_plane = HeroPlane("res/hero.png", WINDOWS_W / 2 - 50, WINDOWS_H * 2 / 3)  # 创建飞机对象
        self.enemy_planes = []
        for i in range(ENEMY_COUNT):
            enemy_plane = Enemy("res/img-plane_%d.png" % (random.randint(1, 7)), random.randint(0, 412),
                                random.randint(-2000, -68))  # 创建敌机对象
            self.enemy_planes.append(enemy_plane)
        self.score = 0  # 初始化得分
        self.is_start = False
        self.is_over = False
        self.eneny_boom_lst = []  # 爆炸效果图列表
        for i in range(1, 8):
            eneny_boom = pygame.image.load("res/bomb-%d.png" % i)
            self.eneny_boom_lst.append(eneny_boom)
        self.boos = Boss("res/img-plane_1.png", WINDOWS_W / 2 - 50, 0)

    def draw_boss(self):
        if self.score >= 50:
            self.window.blit(self.boos.img, (self.boos.x, self.boos.y))
            self.boos.boss_move()
            num = random.randint(1, 80)
            if num == 1:
                self.boos.boss_fire()
        for bullet in self.boos.boss_bullets:
            self.window.blit(bullet.img, (bullet.x, bullet.y))

    def draw_map(self):
        # self.window.blit(self.bg_image, (0, 0))  # 贴图（指定坐标，将图片绘制到窗口）
        self.window.blit(self.map.img, (self.map.x, self.map.y))
        self.window.blit(self.map.img2, (self.map.x2, self.map.y2))
        if self.map.y > 768:
            self.map.y = 0
            self.map.y2 = -768

    def draw_hero_plane(self):
        for enemy_plane in self.enemy_planes:  # 取出每一架敌机，让其和英雄飞机进行碰撞检测
            if self.hero_plane.hero_enemy_hited(enemy_plane):  # 如果相撞，游戏结束
                print("游戏结束")
                for bomb in self.eneny_boom_lst:
                    self.window.blit(bomb, (self.hero_plane.x, self.hero_plane.y))
                    self.update()
                self.gameover_sound.play()
                self.is_over = True
                # sys.exit()
        self.window.blit(self.hero_plane.img, (self.hero_plane.x, self.hero_plane.y))  # 贴英雄飞机图

    def draw_hero_bullet(self):
        out_bullets = []  # 收集边界外的子弹
        for bullet in self.hero_plane.bullets:  # 取出每一颗子弹
            if bullet.y < -30:  # 超出边界
                out_bullets.append(bullet)
            else:
                for enemy_plane in self.enemy_planes:  # 将取出的每一颗子弹和每一架敌机进行碰撞检测
                    if bullet.hero_bullet_is_hited(enemy_plane):
                        for bomb in self.eneny_boom_lst:
                            self.window.blit(bomb, (bullet.x, bullet.y))
                        out_bullets.append(bullet)  # 如果相撞,把子弹添加到要删除的子弹列表
                        enemy_plane.enemy_is_hited = True  # 如果相撞，改变敌机的碰撞属性
                        # 播放音效
                        self.boom_sound.play()
                        self.score += 10  # 打中飞机得10分
                        break  # 一旦子弹被撞，这颗子弹就不用和其他敌机再进行碰撞检测了
                    else:
                        self.window.blit(bullet.img, (bullet.x, bullet.y))  # 贴子弹图
        for bullet in out_bullets:
            self.hero_plane.bullets.remove(bullet)

    def draw_enemy_plane(self):
        for enemy_plane in self.enemy_planes:  # 取出每一架敌机
            if enemy_plane.y > 768 or enemy_plane.enemy_is_hited == True:  # 敌机飞出边界或被撞，则重置敌机属性
                enemy_plane.__init__("res/img-plane_%d.png" % (random.randint(1, 7)), random.randint(0, 412),
                                     random.randint(-2000, -68))
            self.window.blit(enemy_plane.img, (enemy_plane.x, enemy_plane.y))  # 贴敌机图

    def draw_text(self, content, score, font_size, position):
        # 加载自定义字体，返回字体对象
        font_obj = pygame.font.Font("res/SIMHEI.TTF", font_size)
        # 设置文本，返回文本对象   render(文本内容， 抗锯齿，颜色)
        if self.score == 0:
            text_obj = font_obj.render("%s" % (content), 1, (255, 255, 255))
        else:
            text_obj = font_obj.render("%s%d" % (content, score), 1, (255, 255, 255))
        # 在指定位置和尺寸绘制指定文字对象
        self.window.blit(text_obj, position)

    def draw(self):
        self.draw_map()
        self.draw_hero_plane()
        self.draw_hero_bullet()
        self.draw_enemy_plane()
        self.draw_boss()
        self.draw_text("得分：", self.score, 30, (30, 30))  # (1文本内容，2分数，3字体大小，4文字坐标)

    def update(self):
        pygame.display.update()  # 刷新界面  不刷新不会更新显示的内容

    def event(self):
        for event in pygame.event.get():  # 获取新事件
            if event.type == pygame.QUIT:  # 窗口关闭
                sys.exit()  # 退出游戏
            if event.type == pygame.KEYDOWN:  # 键盘按下事件
                # if event.key==pygame.K_LEFT or event.key==pygame.K_a:
                #     print("左移")
                #     self.hero_plane.move_left()
                # elif event.key==pygame.K_RIGHT or event.key==pygame.K_d:
                #     print("右移")
                #     self.hero_plane.move_right()
                # if event.key==pygame.K_UP or event.key==pygame.K_w:
                #     print("上移")
                #     self.hero_plane.move_up()
                # elif event.key==pygame.K_DOWN or event.key==pygame.K_s:
                #     print("下移")
                #     self.hero_plane.move_down()
                if event.key == pygame.K_SPACE:  # 空格发射子弹
                    # print("发射子弹")
                    self.hero_plane.fire()
                    self.shoot_sound.play()
        # 键盘长按事件
        # 获取当前键盘所有按键的状态（按下/没有按下），返回bool元组  (0, 0, 0, 0, 1, 0, 0, 0, 0)
        keys = pygame.key.get_pressed()
        # time.sleep(0.2)
        # print(keys)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.hero_plane.x > 0:
                # print("左移")
                self.hero_plane.move_left()
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.hero_plane.x < 412:
                # print("右移")
                self.hero_plane.move_right()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.hero_plane.y > 0:
                # print("上移")
                self.hero_plane.move_up()
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.hero_plane.y < 700:
                # print("下移")
                self.hero_plane.move_down()

    def action(self):  # 主动事件
        for bullet in self.hero_plane.bullets:  # 取出每一颗子弹
            bullet.move_up()  # 让子弹飞
        for enemy_plane in self.enemy_planes:  # 取出每一架敌机
            enemy_plane.move_down()  # 让敌机飞
        self.map.move_down()
        for bullet in self.boos.boss_bullets:
            bullet.move_down()

    def wait_input(self):
        while True:
            for event in pygame.event.get():  # 获取新事件
                if event.type == pygame.QUIT:  # 窗口关闭
                    sys.exit()  # 退出游戏
                if event.type == pygame.KEYDOWN:  # 键盘按下事件
                    if event.key == pygame.K_ESCAPE:  # 按Esc
                        sys.exit()
                    if event.key == pygame.K_RETURN:  # 按Enter
                        if self.is_over:
                            self.__init__()
                        self.is_start = True
                        return

    def game_start(self):  # 游戏开始
        self.draw_map()
        self.draw_text("飞机大战", self.score, 40, (WINDOWS_W / 3, WINDOWS_H / 3))
        self.draw_text("按enter开始游戏，按Esc退出游戏", self.score, 30, (WINDOWS_W / 14, WINDOWS_H / 2))
        self.update()
        self.wait_input()
        time.sleep(0.01)

    def game_over(self):
        self.draw_map()
        self.draw_text("战机被击落，分数是：", self.score, 35, (100, 250))
        self.draw_text("按enter开始游戏，按Esc退出游戏", self.score, 15, (100, 350))
        self.update()
        self.wait_input()
        time.sleep(0.01)

    def run(self):
        while True:  # 游戏在无限循环中
            if not self.is_start:
                self.game_start()
            self.draw()  # 贴图
            self.update()  # 刷新
            self.event()  # 事件检测
            self.action()  # 主动事件
            if self.is_over:
                # 停止背景音乐
                pygame.mixer.music.stop()
                self.game_over()
            time.sleep(0.01)


def main():
    game = Game()  # 创建游戏对象
    game.run()  # 游戏运行


if __name__ == '__main__':  # 判断是否是主动执行文件
    main()
