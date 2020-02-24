import pygame
import time
import sys
import random

# 窗口高度
WINDOWS_H = 768
# 窗口宽度
WINDOWS_W = 512
ENEMY_COUNT = 3
ENEMY_SPEED = 10
HERO_SPEED = 12
HERO_BULLET_SPEED = 14
BOSS_BULLET_SPEED = 10


# 把重复代码写成基类，让其他类继承
class Item:
    def __init__(self, img, x, y):
        self.img = pygame.image.load(img)
        self.x = x
        self.y = y


class Boss(Item):
    def __init__(self, img, x, y):
        super(Boss, self).__init__(img, x, y)
        self.move = "L"
        # 用于存放boss机的子弹对象(装弹)
        self.boss_bullets = []

    def boss_move(self):
        if self.x >= 0 and self.move == "L":
            self.x -= 3
        else:
            self.move = "R"
        if self.x <= WINDOWS_W - 50 and self.move == "R":
            self.x += 3
        else:
            self.move = "L"

    def boss_fire(self):
        # 创建boss机的子弹对象
        boss_bullet = Bullet("res/bullet_2.png", self.x + 50 - 10, self.y + 68)
        # 装弹
        self.boss_bullets.append(boss_bullet)


class Map(Item):
    def __init__(self, img, x, y):
        super(Map, self).__init__(img, x, y)
        self.img2 = pygame.image.load(img)
        self.x2 = x
        self.y2 = y - WINDOWS_H

    def move_down(self):
        self.y += 4
        self.y2 += 4


class Enemy(Item):
    def __init__(self, img, x, y):
        super(Enemy, self).__init__(img, x, y)
        # 定义一个类属性，敌机碰撞，初始为False
        self.enemy_is_hit = False

    def move_down(self):
        self.y += ENEMY_SPEED


class Bullet(Item):

    def move_up(self):
        self.y -= HERO_BULLET_SPEED

    def move_down(self):
        self.y += BOSS_BULLET_SPEED

    def __del__(self):
        print("子弹消失了")

    # 敌机与子弹相撞
    def hero_bullet_enemy_is_hit(self, enemy_plane):
        # 英雄飞机的子弹的矩形区域
        bullet_rect = pygame.Rect(self.x, self.y, 20, 31)
        enemy_rect = pygame.Rect(enemy_plane.x, enemy_plane.y, 100, 68)
        # 判断两个矩形区域是否相交，相交返回True,反之返回False
        flag = pygame.Rect.colliderect(bullet_rect, enemy_rect)
        return flag

    # 英雄飞机与子弹相撞
    def boss_bullet_hero_is_hit(self, hero_plane):
        boss_bullet_rect = pygame.Rect(self.x, self.y, 20, 31)
        hero_plane_rect = pygame.Rect(hero_plane.x, hero_plane.y, 100, 68)
        flag = pygame.Rect.colliderect(boss_bullet_rect, hero_plane_rect)
        return flag

    # boss机与子弹相撞
    def hero_bullet_boss_is_hit(self, boss_plane):
        bullet_rect = pygame.Rect(self.x, self.y, 20, 31)
        boss_plane_rect = pygame.Rect(boss_plane.x, boss_plane.y, 100, 68)
        flag = pygame.Rect.colliderect(bullet_rect, boss_plane_rect)
        return flag


class HeroPlane(Item):
    def __init__(self, img, x, y):
        # 加载飞机图片
        super(HeroPlane, self).__init__(img, x, y)
        # 把子弹对象存到列表中
        self.bullet = []

    def move_left(self):
        self.x -= HERO_SPEED

    def move_right(self):
        self.x += HERO_SPEED

    def move_down(self):
        self.y += HERO_SPEED

    def move_up(self):
        self.y -= HERO_SPEED

    # 装弹
    def fire(self):
        # 创建子弹对象并确定子弹位子
        bullet = Bullet("res/bullet_9.png", self.x + 50 - 10, self.y - 31)
        # 向Bullet列表中添加子弹对象
        self.bullet.append(bullet)

    # 敌机与我放飞机相撞
    def hero_enemy_is_hit(self, enemy_plane):
        # 我放飞机的矩形区域
        hero_rect = pygame.Rect(self.x, self.y, 100, 68)
        # 敌方飞机的矩形区域
        enemy_rect = pygame.Rect(enemy_plane.x, enemy_plane.y, 100, 68)
        # 判断两个矩形区域是否相交，相交返回True，否则返回False
        flag = pygame.Rect.colliderect(hero_rect, enemy_rect)
        return flag


class Game:
    def __init__(self):
        pygame.init()
        # 加载背景音乐
        pygame.mixer.music.load("res/bg2.ogg")
        # 循环播放背景音乐
        pygame.mixer.music.play(-1)
        # 加载敌机爆炸音乐对象
        self.boom_sound = pygame.mixer.Sound("res/baozha.ogg")
        # 加载子弹发射音乐对象
        self.bullet_sound = pygame.mixer.Sound("res/bullet2.wav")
        # 生成游戏结束时的音效
        self.game_over_sound = pygame.mixer.Sound("res/gameover.wav")
        # 创建窗口
        self.window = pygame.display.set_mode((WINDOWS_W, WINDOWS_H))
        # 加载背景图片文件，并返回背景图片对象
        # self.bg_image = pygame.image.load("res/img_bg_level_2.jpg")
        # 创建地图对象，加载背景图片
        self.map = Map("res/img_bg_level_3.jpg", 0, 0)
        # 加载英雄飞机图片文件,创建飞机对象
        self.hero_plane = HeroPlane("res/hero.png", WINDOWS_W / 2 - 50, WINDOWS_H * 2 / 3)
        # 用于将敌机对象存放到列表中
        self.enemy_plans = []
        for i in range(ENEMY_COUNT):
            # 创建敌机对象
            enemy_plane = Enemy(f"res/img-plane_{random.randint(1, 7)}.png", random.randint(0, 412),
                                random.randint(-2000, -68))
            self.enemy_plans.append(enemy_plane)
            # 初始化得分
        self.score = 0
        self.boss_HP = 50
        self.is_start = False
        self.is_over = False
        self.is_win = False
        self.enemy_boom_lst = []
        for i in range(1, 8):
            enemy_boom = pygame.image.load(f"res/bomb-{i}.png")
            self.enemy_boom_lst.append(enemy_boom)
        # 创建boss飞机对象
        self.boss = Boss("res/img-plane_1.png", WINDOWS_W / 2 - 50, 0)

    def draw_boss(self):
        self.window.blit(self.boss.img, (self.boss.x, self.boss.y))
        self.boss.boss_move()

    def draw_boss_bullet(self):
        num = random.randint(1, 80)
        if num == 1:
            self.boss.boss_fire()
        for boss_bullet in self.boss.boss_bullets:
            if boss_bullet.boss_bullet_hero_is_hit(self.hero_plane):
                print("游戏结束")
                for bomb in self.enemy_boom_lst:
                    self.window.blit(bomb, (self.hero_plane.x, self.hero_plane.y))
                    self.update()
                self.game_over_sound.play()
                self.is_over = True
            # 贴boss机的子弹图（发射子弹）
            self.window.blit(boss_bullet.img, (boss_bullet.x, boss_bullet.y))

    def draw_map(self):
        # self.window.blit(self.bg_image, (0, 0))
        self.window.blit(self.map.img, (self.map.x, self.map.y))
        self.window.blit(self.map.img2, (self.map.x2, self.map.y2))
        # 让游戏的地图处于循环移动状态
        if self.map.y > WINDOWS_H:
            self.map.y = 0
            self.map.y2 = -WINDOWS_H

    def draw_hero_plane(self):
        # 每取出一架敌机与我方飞机进行碰撞检测
        for enemy_plane in self.enemy_plans:
            # 如果相撞，游戏结束
            if self.hero_plane.hero_enemy_is_hit(enemy_plane):
                print("游戏结束")
                for bomb in self.enemy_boom_lst:
                    self.window.blit(bomb, (self.hero_plane.x, self.hero_plane.y))
                    self.update()
                self.game_over_sound.play()
                self.is_over = True
                # sys.exit()
        # 贴英雄飞机图
        self.window.blit(self.hero_plane.img, (self.hero_plane.x, self.hero_plane.y))

    def draw_hero_bullet(self):
        # 收集超出边界的子弹
        out_bullets = []
        # 每取出一颗子弹对象
        for bullet in self.hero_plane.bullet:
            # 超出边界
            if bullet.y < -30:
                out_bullets.append(bullet)
            else:
                # 没取出一颗子弹与每一架敌机进行碰撞检测
                for enemy_plane in self.enemy_plans:
                    # 如果相撞
                    if bullet.hero_bullet_enemy_is_hit(enemy_plane):
                        for bomb in self.enemy_boom_lst:
                            self.window.blit(bomb, (bullet.x, bullet.y))
                        # 将相撞的子弹添加到要删除的列表中
                        out_bullets.append(bullet)
                        # 如果相撞,改变敌机的碰撞属性
                        enemy_plane.enemy_is_hit = True
                        self.boom_sound.play()
                        self.score += 10
                        # 如果取出的这颗子弹与敌机相撞，就不用和其他敌机进行碰撞检测了，跳出
                        break
                    else:
                        # 帖子弹图
                        self.window.blit(bullet.img, (bullet.x, bullet.y))
        # 将超出边界的子弹对象remove掉
        for bullet in out_bullets:
            self.hero_plane.bullet.remove(bullet)
        # 每取出一颗子弹与boss机进行碰撞检测
        for bullet in self.hero_plane.bullet:
            # 如果相撞
            if bullet.hero_bullet_boss_is_hit(self.boss):
                for bomb in self.enemy_boom_lst:
                    self.window.blit(bomb, (bullet.x, bullet.y))
                    self.boom_sound.play()
                out_bullets.append(bullet)
                self.boss_HP -= 1
                break
            else:
                # 帖子弹图
                self.window.blit(bullet.img, (bullet.x, bullet.y))
        if self.boss_HP == 0:
            self.update()
            print("恭喜您游戏胜利!")
            self.is_win = True

    def draw_enemy_plane(self):
        # 每取出一架敌机
        for enemy_plane in self.enemy_plans:
            # 如果敌机超出边界或者与子弹相撞，重置敌机属性
            if enemy_plane.y > WINDOWS_H or enemy_plane.enemy_is_hit is True:
                enemy_plane.__init__(f"res/img-plane_{random.randint(1, 7)}.png", random.randint(0, 412),
                                     random.randint(-2000, -68))
            self.window.blit(enemy_plane.img, (enemy_plane.x, enemy_plane.y))

    # (1文本内容，2分数，3文字大小，4文字坐标)
    def draw_text(self, content, score, font_size, position):
        # 加载自定义字体，返回字体对象
        font_ojb = pygame.font.Font("res/SIMHEI.TTF", font_size)
        # 设置文本，返回文本对象 render(文本内容，抗锯齿，颜色)
        text_obj = font_ojb.render("%s%d" % (content, score), 1, (255, 255, 255))
        # 在指定位置和尺寸绘制指定文字对象
        self.window.blit(text_obj, position)

    # (1文本内容，32文字大小，3文字坐标)
    def draw_end_text(self, content, font_size, position):
        font_ojb = pygame.font.Font("res/SIMHEI.TTF", font_size)
        text_obj = font_ojb.render(f"{content}", 1, (255, 255, 255))
        self.window.blit(text_obj, position)

    def draw(self):
        self.draw_map()
        self.draw_hero_plane()
        self.draw_hero_bullet()
        self.draw_enemy_plane()
        self.draw_boss()
        self.draw_boss_bullet()
        # (1文本内容，2分数，3字体大小，4文本坐标)
        self.draw_text("得分:", self.score, 30, (30, 30))
        self.draw_text("boss血量：", self.boss_HP, 15, (WINDOWS_W*2/3, 30))

    def update(self):
        pygame.display.update()

    def event(self):
        # 不断的获取新事件
        for event in pygame.event.get():
            # 如果点击窗口关闭，系统就退出游戏
            if event.type == pygame.QUIT:
                sys.exit()
            # 键盘按下事件
            if event.type == pygame.KEYDOWN:
                # 按空格，调用fire方法
                if event.key == pygame.K_SPACE:
                    self.bullet_sound.play()
                    self.hero_plane.fire()
        # 键盘长按事件
        # 获取当前键盘所有案件状态：按下的/没有按下的 返回bool元组（0，0，0，0，1，0，0，0，0）
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT or pygame.K_a]:
            if self.hero_plane.x > 0:
                self.hero_plane.move_left()
        if keys[pygame.K_RIGHT or pygame.K_d]:
            if self.hero_plane.x < 412:
                self.hero_plane.move_right()
        if keys[pygame.K_UP or pygame.K_w]:
            if self.hero_plane.y > 0:
                self.hero_plane.move_up()
        if keys[pygame.K_DOWN or pygame.K_s]:
            if self.hero_plane.y < 700:
                self.hero_plane.move_down()

    # 主动事件
    def action(self):
        # 每取出一颗子弹对象
        for bullet in self.hero_plane.bullet:
            # 让子弹处于向上移动状态
            bullet.move_up()
        # 每取出一架敌机对象
        for enemy_plane in self.enemy_plans:
            # 让敌机处于向下移动状态
            enemy_plane.move_down()
        # 让地图处于向下移动状态
        self.map.move_down()
        # 每取出一颗boss机的子弹对象
        for boss_bullet in self.boss.boss_bullets:
            # 让boss机的子弹处于向下移动状态
            boss_bullet.move_down()

    def wait_input(self):
        while True:
            # 获取新事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    if event.key == pygame.K_RETURN:
                        if self.is_over or self.is_win:
                            self.__init__()
                        self.is_start = True
                        return

    def game_start(self):
        self.draw_map()
        self.draw_end_text("飞机大战", 40, (WINDOWS_W / 3, WINDOWS_H / 3))
        self.draw_end_text("按enter开始游戏，按ESC退出游戏", 30, (WINDOWS_W / 14, WINDOWS_H / 2))
        self.update()
        self.wait_input()
        time.sleep(0.01)

    def game_over(self):
        self.draw_map()
        self.draw_end_text("很遗憾战机爆炸，您没有分数", 15, (WINDOWS_W / 3, WINDOWS_H / 3))
        self.draw_end_text("按enter开始游戏，按ESC退出游戏", 30, (WINDOWS_W / 14, WINDOWS_H / 2))
        self.update()
        self.wait_input()
        time.sleep(0.01)

    def game_win(self):
        self.draw_map()
        self.draw_text("恭喜您游戏取得胜利！您的最终分数是：", self.score, 20, (WINDOWS_W / 14, WINDOWS_H / 3))
        self.draw_end_text("按enter开始游戏，按ESC退出游戏", 30, (WINDOWS_W / 14, WINDOWS_H / 2))
        self.update()
        self.wait_input()
        time.sleep(0.01)

    def run(self):
        # 游戏在无限循环
        while True:
            if not self.is_start:
                self.game_start()
            # 贴图
            self.draw()
            # 刷新
            self.update()
            # 触发事件检查
            self.event()
            # 触发主动事件
            self.action()
            if self.is_over:
                pygame.mixer.music.stop()
                self.game_over()
            elif self.is_win:
                pygame.mixer.music.stop()
                self.game_win()
            time.sleep(0.01)


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
