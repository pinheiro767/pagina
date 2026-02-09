import os
import sys
import time
import math
import pygame
from src.questions import QUESTIONS
from src.assets_loader import load_image

W, H = 1100, 650
FPS = 60

class Fade:
    def __init__(self, duration=0.55):
        self.duration = duration
        self.active = False
        self.t = 0.0
        self.on_mid = None
        self.mode = "out"

    def start(self, on_mid=None):
        self.active = True
        self.t = 0.0
        self.mode = "out"
        self.on_mid = on_mid

    def update(self, dt):
        if not self.active:
            return 0
        self.t += dt
        half = self.duration / 2
        if self.mode == "out" and self.t >= half:
            self.mode = "in"
            if self.on_mid:
                self.on_mid()
                self.on_mid = None
        if self.t >= self.duration:
            self.active = False
        if self.t <= half:
            return int(255 * (self.t / half))
        return int(255 * (1 - (self.t - half) / half))

def draw_wrap(surf, font, text, x, y, max_w, color=(235, 240, 255)):
    words = text.split(" ")
    line = ""
    yy = y
    for w in words:
        test = (line + " " + w).strip()
        if font.size(test)[0] > max_w:
            surf.blit(font.render(line, True, color), (x, yy))
            yy += font.get_height() + 4
            line = w
        else:
            line = test
    if line:
        surf.blit(font.render(line, True, color), (x, yy))
        yy += font.get_height() + 4
    return yy

class Button:
    def __init__(self, rect, label, font):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.hover = False

    def handle(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            return self.rect.collidepoint(ev.pos)
        return False

    def draw(self, surf):
        bg = (40, 55, 85) if not self.hover else (60, 80, 120)
        pygame.draw.rect(surf, bg, self.rect, border_radius=14)
        pygame.draw.rect(surf, (140, 170, 220), self.rect, 2, border_radius=14)
        txt = self.font.render(self.label, True, (240, 245, 255))
        surf.blit(txt, txt.get_rect(center=self.rect.center))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("CardioResp Escape")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 44, bold=True)
        self.font_mid = pygame.font.SysFont("arial", 26, bold=True)
        self.font = pygame.font.SysFont("arial", 20)

        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.images_dir = os.path.join(self.base_dir, "assets", "images")
        self.img_cache = {}

        self.fade = Fade()

        self.state = "menu"
        self.level_idx = 0

        # progresso
        self.keys_main = 0
        self.penalty = 0.0
        self.start_time = time.time()

        # recompensas
        self.score = 0
        self.combo = 0
        self.shields = 0

        self.feedback = ""
        self.feedback_ok = False

        self.btn_start = Button((W//2 - 160, H//2 + 80, 320, 58), "INICIAR", self.font_mid)
        self.btn_map = Button((W - 190, 14, 170, 46), "MAPA", self.font)
        self.btn_exit = Button((30, H - 70, 170, 46), "SAIR", self.font)

    def reset_run(self):
        self.keys_main = 0
        self.penalty = 0.0
        self.start_time = time.time()
        self.score = 0
        self.combo = 0
        self.shields = 0

    def elapsed(self):
        return (time.time() - self.start_time) + self.penalty

    def pulse(self, t):
        return 1.0 + 0.04 * math.sin(t * 7.0) + 0.02 * math.sin(t * 13.0)

    def get_img(self, filename):
        if filename in self.img_cache:
            return self.img_cache[filename]
        img = load_image(self.images_dir, filename)
        self.img_cache[filename] = img
        return img

    def draw_bg(self):
        t = pygame.time.get_ticks() / 1000.0
        self.screen.fill((8, 12, 22))
        for i in range(14):
            y = int((H/14)*i + 18*math.sin(t*1.2 + i))
            pygame.draw.line(self.screen, (20, 30, 55), (0, y), (W, y), 2)

    def draw_topbar(self):
        pygame.draw.rect(self.screen, (15, 22, 40), (0, 0, W, 70))
        pygame.draw.line(self.screen, (70, 90, 130), (0, 70), (W, 70), 2)

        t = self.elapsed()
        mm = int(t // 60)
        ss = int(t % 60)
        hud = f"⏱️ {mm:02d}:{ss:02d}   🔑 {self.keys_main}/5   🪙 {self.score}   🔥 {self.combo}   💠 {self.shields}"
        self.screen.blit(self.font_mid.render(hud, True, (235, 240, 255)), (22, 18))
        self.btn_map.draw(self.screen)

    def goto(self, new_state):
        self.state = new_state

    def menu(self, events, dt):
        self.draw_bg()
        title = self.font_big.render("CARDIORESP ESCAPE", True, (245, 248, 255))
        self.screen.blit(title, title.get_rect(center=(W//2, 160)))
        draw_wrap(self.screen, self.font_mid, "Escape game com fases + imagens + recompensa!", W//2 - 360, 220, 720)

        t = pygame.time.get_ticks() / 1000.0
        img = self.get_img("heart_photo.jpg") or self.get_img("heart_diagram.png")
        if img:
            s = self.pulse(t)
            im = pygame.transform.smoothscale(img, (int(img.get_width()*s), int(img.get_height()*s)))
            self.screen.blit(im, im.get_rect(center=(W//2, 360)))

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.btn_start.handle(ev) and not self.fade.active:
                self.reset_run()
                self.fade.start(on_mid=lambda: self.goto("map"))

        self.btn_start.draw(self.screen)

        a = self.fade.update(dt)
        if a:
            ov = pygame.Surface((W, H)); ov.fill((0,0,0)); ov.set_alpha(a)
            self.screen.blit(ov, (0,0))

    def map(self, events, dt):
        self.draw_bg()
        self.draw_topbar()

        draw_wrap(self.screen, self.font_big, "MAPA DO LABORATÓRIO", 30, 92, W-60)
        draw_wrap(self.screen, self.font, "Fases principais em ordem. Bônus a qualquer momento.", 30, 145, W-60)

        buttons = []
        for i, q in enumerate(QUESTIONS):
            x = 70 + (i % 3)*330
            y = 210 + (i // 3)*140
            label = f"{i+1}. " + ("FASE" if q["main"] else "BÔNUS")
            buttons.append((q, i, Button((x, y, 290, 70), label, self.font_mid)))

        main_indices = [i for i,q in enumerate(QUESTIONS) if q["main"]]
        next_main_idx = main_indices[self.keys_main] if self.keys_main < len(main_indices) else None

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.btn_exit.handle(ev) and not self.fade.active:
                pygame.quit(); sys.exit()

        for q, i, btn in buttons:
            unlocked = (not q["main"]) or (i == next_main_idx) or (q["main"] and i in main_indices[:self.keys_main])
            btn.hover = btn.rect.collidepoint(pygame.mouse.get_pos())

            if not unlocked:
                pygame.draw.rect(self.screen, (22, 28, 40), btn.rect, border_radius=14)
                pygame.draw.rect(self.screen, (60, 70, 90), btn.rect, 2, border_radius=14)
                lock = self.font_mid.render("BLOQUEADO", True, (160, 170, 190))
                self.screen.blit(lock, lock.get_rect(center=btn.rect.center))
            else:
                btn.draw(self.screen)

            draw_wrap(self.screen, self.font, q["id"], btn.rect.x, btn.rect.bottom + 6, btn.rect.width)

            for ev in events:
                if unlocked and btn.handle(ev) and not self.fade.active:
                    self.feedback = ""
                    self.feedback_ok = False
                    self.fade.start(on_mid=lambda idx=i: self.open_question(idx))

        self.btn_exit.draw(self.screen)

        a = self.fade.update(dt)
        if a:
            ov = pygame.Surface((W, H)); ov.fill((0,0,0)); ov.set_alpha(a)
            self.screen.blit(ov, (0,0))

    def open_question(self, idx):
        self.level_idx = idx
        self.goto("question")

    def question(self, events, dt):
        self.draw_bg()
        self.draw_topbar()

        q = QUESTIONS[self.level_idx]
        panel = pygame.Rect(30, 90, W-60, H-120)
        pygame.draw.rect(self.screen, (12, 18, 34), panel, border_radius=22)
        pygame.draw.rect(self.screen, (80, 110, 160), panel, 2, border_radius=22)

        img = self.get_img(q["image"])
        t = pygame.time.get_ticks() / 1000.0
        if img:
            s = self.pulse(t) if q["main"] else (1.0 + 0.02*math.sin(t*10))
            im = pygame.transform.smoothscale(img, (int(img.get_width()*s), int(img.get_height()*s)))
            self.screen.blit(im, im.get_rect(center=(panel.left+230, panel.top+220)))

        x0 = panel.left + 450
        y0 = panel.top + 26

        tag = "🗝️ FASE PRINCIPAL" if q["main"] else "🧩 SALA BÔNUS"
        draw_wrap(self.screen, self.font_mid, f"{tag} — {q['id']}", x0, y0, panel.width-480)
        y = y0 + 50
        y = draw_wrap(self.screen, self.font_mid, q["prompt"], x0, y, panel.width-480)

        option_rects = []
        oy = y + 10
        for i, opt in enumerate(q["options"]):
            r = pygame.Rect(x0, oy + i*54, panel.width-480, 46)
            option_rects.append((r, opt))
            hovered = r.collidepoint(pygame.mouse.get_pos())
            bg = (35, 48, 78) if not hovered else (55, 75, 115)
            pygame.draw.rect(self.screen, bg, r, border_radius=12)
            pygame.draw.rect(self.screen, (120, 150, 210), r, 2, border_radius=12)
            draw_wrap(self.screen, self.font, opt, r.x+12, r.y+12, r.width-24)

        fb = pygame.Rect(x0, panel.bottom-108, panel.width-480, 80)
        pygame.draw.rect(self.screen, (10, 14, 26), fb, border_radius=14)
        pygame.draw.rect(self.screen, (90, 110, 150), fb, 2, border_radius=14)

        if self.feedback:
            col = (70, 230, 160) if self.feedback_ok else (255, 170, 110)
            draw_wrap(self.screen, self.font_mid, self.feedback, fb.x+14, fb.y+10, fb.width-28, color=col)
            draw_wrap(self.screen, self.font, q["explain"], fb.x+14, fb.y+42, fb.width-28)
        else:
            draw_wrap(self.screen, self.font, "Acerto = +100 🪙. A cada 3 acertos seguidos ganha 1 💠 escudo.", fb.x+14, fb.y+24, fb.width-28)

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if self.btn_map.handle(ev) and not self.fade.active:
                self.fade.start(on_mid=lambda: self.goto("map"))

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not self.fade.active:
                for r, opt in option_rects:
                    if r.collidepoint(ev.pos):
                        picked = opt.split(")")[0].strip()

                        if picked == q["answer"]:
                            self.feedback_ok = True
                            self.feedback = "✅ CORRETO! +100 🪙"
                            self.score += 100
                            self.combo += 1
                            if self.combo % 3 == 0:
                                self.shields += 1

                            if q["main"]:
                                main_indices = [i for i,qq in enumerate(QUESTIONS) if qq["main"]]
                                if self.level_idx == main_indices[self.keys_main]:
                                    self.keys_main += 1

                            if self.keys_main >= 5:
                                self.fade.start(on_mid=lambda: self.goto("win"))
                            else:
                                self.fade.start(on_mid=lambda: self.goto("map"))
                        else:
                            self.feedback_ok = False
                            self.combo = 0
                            if self.shields > 0:
                                self.shields -= 1
                                self.feedback = "❌ ERRO… mas o 💠 escudo te salvou!"
                            else:
                                self.feedback = "❌ INCORRETO. +10s"
                                self.penalty += 10.0

        a = self.fade.update(dt)
        if a:
            ov = pygame.Surface((W, H)); ov.fill((0,0,0)); ov.set_alpha(a)
            self.screen.blit(ov, (0,0))

    def win(self, events, dt):
        self.draw_bg()
        t = self.elapsed()
        mm, ss = int(t//60), int(t%60)

        msg = self.font_big.render("VOCÊ ESCAPOU! 🫀🌬️", True, (245, 248, 255))
        self.screen.blit(msg, msg.get_rect(center=(W//2, 160)))

        txt = self.font_mid.render(f"Tempo: {mm:02d}:{ss:02d}   Pontos: {self.score}", True, (235, 240, 255))
        self.screen.blit(txt, txt.get_rect(center=(W//2, 230)))

        btn_again = Button((W//2 - 170, 400, 340, 58), "JOGAR DE NOVO", self.font_mid)
        btn_exit = Button((W//2 - 110, 475, 220, 48), "SAIR", self.font_mid)

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_again.handle(ev):
                self.reset_run()
                self.fade.start(on_mid=lambda: self.goto("map"))
            if btn_exit.handle(ev):
                pygame.quit(); sys.exit()

        btn_again.draw(self.screen)
        btn_exit.draw(self.screen)

        a = self.fade.update(dt)
        if a:
            ov = pygame.Surface((W, H)); ov.fill((0,0,0)); ov.set_alpha(a)
            self.screen.blit(ov, (0,0))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            if self.state == "menu":
                self.menu(events, dt)
            elif self.state == "map":
                self.map(events, dt)
            elif self.state == "question":
                self.question(events, dt)
            elif self.state == "win":
                self.win(events, dt)

            pygame.display.flip()
