import os
import sys
import time
import math
import pygame
from src.questions import QUESTIONS
from src.assets_loader import load_image

W, H = 1100, 650
FPS = 60

# Cada fase principal (0..4) dá 1 dígito do código final, na ordem.
MAIN_CODE_DIGITS = ["7", "3", "9", "1", "4"]
FINAL_CODE = "".join(MAIN_CODE_DIGITS)

# Terminais (perguntas) na sala: 5 principais (q_index 0..4)
TERMINALS = [
    {"q_index": 0, "pos": (220, 190)},
    {"q_index": 1, "pos": (520, 170)},
    {"q_index": 2, "pos": (820, 220)},
    {"q_index": 3, "pos": (330, 440)},
    {"q_index": 4, "pos": (760, 470)},
]

# 3 bônus (q_index 5..7) — opcionais
BONUS_TERMINALS = [
    {"q_index": 5, "pos": (980, 360)},
    {"q_index": 6, "pos": (110, 510)},
    {"q_index": 7, "pos": (560, 520)},
]

DOOR_RECT = pygame.Rect(W - 150, H//2 - 90, 110, 180)

def clamp(v, a, b):
    return max(a, min(b, v))

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

class Fade:
    def __init__(self, duration=0.45):
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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("CardioResp Escape — Sala de Fuga")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 44, bold=True)
        self.font_mid = pygame.font.SysFont("arial", 26, bold=True)
        self.font = pygame.font.SysFont("arial", 20)

        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.images_dir = os.path.join(self.base_dir, "assets", "images")
        self.img_cache = {}

        self.fade = Fade()

        # estados: menu, room, question, keypad, win
        self.state = "menu"
        self.active_terminal = None
        self.feedback = ""
        self.feedback_ok = False

        # tempo/pontos/recompensas
        self.start_time = time.time()
        self.penalty = 0.0
        self.score = 0
        self.combo = 0
        self.shields = 0

        # progresso de escape
        self.solved = set()
        self.keys_main = 0
        self.collected_digits = []
        self.keypad_input = ""

        # player (bolinha)
        self.px, self.py = 120.0, H / 2
        self.pr = 16
        self.speed = 250.0

        # objetos na sala (colecionáveis)
        self.items = [
            {"name": "Lanterna", "pos": [160, 120], "taken": False},
            {"name": "Chave de fenda", "pos": [430, 560], "taken": False},
            {"name": "Cartão de acesso", "pos": [650, 110], "taken": False},
        ]
        self.inventory = []

        # botões do menu
        self.btn_start = pygame.Rect(W//2 - 170, H//2 + 70, 340, 58)
        self.btn_exit = pygame.Rect(W//2 - 110, H//2 + 140, 220, 46)

        self.hint = "WASD anda • E interage • ESC volta. Resolva as 5 fases principais para liberar o teclado da porta."

    def get_img(self, filename):
        if filename in self.img_cache:
            return self.img_cache[filename]
        img = load_image(self.images_dir, filename, max_size=(460, 460))
        self.img_cache[filename] = img
        return img

    def elapsed(self):
        return (time.time() - self.start_time) + self.penalty

    def reset_run(self):
        self.start_time = time.time()
        self.penalty = 0.0
        self.score = 0
        self.combo = 0
        self.shields = 0
        self.solved = set()
        self.keys_main = 0
        self.collected_digits = []
        self.keypad_input = ""
        self.px, self.py = 120.0, H / 2
        for it in self.items:
            it["taken"] = False
        self.inventory = []
        self.feedback = ""

    def draw_bg(self):
        t = pygame.time.get_ticks() / 1000.0
        self.screen.fill((8, 12, 22))
        for i in range(14):
            y = int((H / 14) * i + 18 * math.sin(t * 1.2 + i))
            pygame.draw.line(self.screen, (18, 26, 46), (0, y), (W, y), 2)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (15, 22, 40), (0, 0, W, 70))
        pygame.draw.line(self.screen, (70, 90, 130), (0, 70), (W, 70), 2)
        t = self.elapsed()
        mm, ss = int(t // 60), int(t % 60)
        hud = f"⏱️ {mm:02d}:{ss:02d}   🔑 {self.keys_main}/5   🪙 {self.score}   🔥 {self.combo}   💠 {self.shields}   🔢 {''.join(self.collected_digits)}"
        self.screen.blit(self.font_mid.render(hud, True, (235, 240, 255)), (18, 18))

    def set_state(self, st):
        self.state = st

    def menu(self, events, dt):
        self.draw_bg()
        title = self.font_big.render("CARDIORESP ESCAPE", True, (245, 248, 255))
        self.screen.blit(title, title.get_rect(center=(W // 2, 170)))
        draw_wrap(self.screen, self.font_mid, "Sala de fuga com terminais (perguntas), itens e porta com código final.", W // 2 - 420, 230, 840)

        img = self.get_img("heart_photo.jpg") or self.get_img("heart_diagram.png")
        if img:
            im = pygame.transform.smoothscale(img, (360, 360))
            self.screen.blit(im, im.get_rect(center=(W // 2, 365)))

        mx, my = pygame.mouse.get_pos()

        def draw_btn(r, text):
            hov = r.collidepoint((mx, my))
            bg = (60, 80, 120) if hov else (40, 55, 85)
            pygame.draw.rect(self.screen, bg, r, border_radius=14)
            pygame.draw.rect(self.screen, (140, 170, 220), r, 2, border_radius=14)
            self.screen.blit(self.font_mid.render(text, True, (240, 245, 255)), self.font_mid.render(text, True, (240, 245, 255)).get_rect(center=r.center))

        draw_btn(self.btn_start, "INICIAR")
        draw_btn(self.btn_exit, "SAIR")

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not self.fade.active:
                if self.btn_start.collidepoint((mx, my)):
                    self.reset_run()
                    self.fade.start(on_mid=lambda: self.set_state("room"))
                if self.btn_exit.collidepoint((mx, my)):
                    pygame.quit(); sys.exit()

        a = self.fade.update(dt)
        if a:
            ov = pygame.Surface((W, H)); ov.fill((0, 0, 0)); ov.set_alpha(a)
            self.screen.blit(ov, (0, 0))

    def room(self, events, dt):
        self.draw_bg()
        self.draw_hud()

        # movimento
        keys = pygame.key.get_pressed()
        vx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
        vy = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)
        norm = math.hypot(vx, vy) or 1.0
        self.px += (vx / norm) * self.speed * dt
        self.py += (vy / norm) * self.speed * dt
        self.px = clamp(self.px, 40, W - 40)
        self.py = clamp(self.py, 90, H - 40)

        # porta
        pygame.draw.rect(self.screen, (28, 32, 46), DOOR_RECT, border_radius=18)
        pygame.draw.rect(self.screen, (120, 150, 210), DOOR_RECT, 2, border_radius=18)
        self.screen.blit(self.font_mid.render("PORTA", True, (235, 240, 255)),
                         self.font_mid.render("PORTA", True, (235, 240, 255)).get_rect(center=(DOOR_RECT.centerx, DOOR_RECT.y + 34)))
        lock_txt = "TRANCADA" if self.keys_main < 5 else "PRONTA"
        self.screen.blit(self.font.render(lock_txt, True, (235, 240, 255)),
                         self.font.render(lock_txt, True, (235, 240, 255)).get_rect(center=(DOOR_RECT.centerx, DOOR_RECT.y + 70)))

        # terminais
        def draw_terminal(px, py, solved):
            r = pygame.Rect(px - 28, py - 22, 56, 44)
            bg = (40, 90, 70) if solved else (55, 70, 110)
            pygame.draw.rect(self.screen, bg, r, border_radius=10)
            pygame.draw.rect(self.screen, (160, 200, 255), r, 2, border_radius=10)
            return r

        all_terminals = []
        for t in TERMINALS:
            qi = t["q_index"]
            all_terminals.append((t, draw_terminal(t["pos"][0], t["pos"][1], qi in self.solved)))

        for t in BONUS_TERMINALS:
            qi = t["q_index"]
            all_terminals.append((t, draw_terminal(t["pos"][0], t["pos"][1], qi in self.solved)))

        # itens
        for it in self.items:
            if it["taken"]:
                continue
            x, y = it["pos"]
            r = pygame.Rect(x - 14, y - 14, 28, 28)
            pygame.draw.rect(self.screen, (130, 110, 60), r, border_radius=8)
            pygame.draw.rect(self.screen, (220, 210, 160), r, 2, border_radius=8)

        # player
        pygame.draw.circle(self.screen, (160, 220, 255), (int(self.px), int(self.py)), self.pr)
        pygame.draw.circle(self.screen, (20, 30, 50), (int(self.px), int(self.py)), self.pr, 3)

        draw_wrap(self.screen, self.font, self.hint, 18, 78, W - 260, color=(210, 220, 240))
        inv_txt = "🎒 Itens: " + (", ".join(self.inventory) if self.inventory else "nenhum")
        draw_wrap(self.screen, self.font, inv_txt, 18, H - 34, W - 220, color=(220, 230, 250))

        prompt = ""
        near_terminal = None
        near_item = None
        can_open_door = False

        # porta
        if DOOR_RECT.collidepoint((int(self.px), int(self.py))):
            if self.keys_main >= 5:
                prompt = "Pressione E para digitar o código"
                can_open_door = True
            else:
                prompt = "Porta trancada: faltam fases principais"

        # terminais
        for t, rect in all_terminals:
            if rect.collidepoint((int(self.px), int(self.py))):
                qi = t["q_index"]
                if qi in self.solved:
                    prompt = "Terminal resolvido ✅"
                else:
                    prompt = "Pressione E para usar o terminal"
                    near_terminal = qi
                break

        # itens (simples: pega se encostar)
        for it in self.items:
            if it["taken"]:
                continue
            dx = self.px - it["pos"][0]
            dy = self.py - it["pos"][1]
            if dx*dx + dy*dy <= 44*44:
                prompt = f"Pressione E para pegar: {it['name']}"
                near_item = it
                break

        if prompt:
            box = pygame.Rect(18, H - 86, W - 260, 46)
            pygame.draw.rect(self.screen, (10, 14, 26), box, border_radius=12)
            pygame.draw.rect(self.screen, (90, 110, 150), box, 2, border_radius=12)
            self.screen.blit(self.font.render(prompt, True, (235, 240, 255)), (box.x + 12, box.y + 13))

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and not self.fade.active:
                self.fade.start(on_mid=lambda: self.set_state("menu"))

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_e and not self.fade.active:
                if near_item is not None:
                    near_item["taken"] = True
                    self.inventory.append(near_item["name"])
                elif near_terminal is not None:
                    self.active_terminal = near_terminal
                    self.feedback = ""
                    self.feedback_ok = False
                    self.fade.start(on_mid=lambda: self.set_state("question"))
                elif can_open_door:
                    self.keypad_input = ""
                    self.fade.start(on_mid=lambda: self.set_state("keypad"))

        a = self.fade.update(dt)
        if a:
            ov = pygame.Surface((W, H)); ov.fill((0, 0, 0)); ov.set_alpha(a)
            self.screen.blit(ov, (0, 0))

    def question(self, events, dt):
        self.draw_bg()
        self.draw_hud()

        qi = self.active_terminal
        q = QUESTIONS[qi]

        panel = pygame.Rect(30, 90, W - 60, H - 120)
        pygame.draw.rect(self.screen, (12, 18, 34), panel, border_radius=22)
        pygame.draw.rect(self.screen, (80, 110, 160), panel, 2, border_radius=22)

        img = self.get_img(q["image"])
        t = pygame.time.get_ticks() / 1000.0
        if img:
            s = 1.0 + 0.02 * math.sin(t * 10)
            im = pygame.transform.smoothscale(img, (int(img.get_width() * s), int(img.get_height() * s)))
            self.screen.blit(im, im.get_rect(center=(panel.left + 230, panel.top + 220)))

        x0 = panel.left + 450
        y0 = panel.top + 26
        tag = "🗝️ PRINCIPAL" if q["main"] else "🧩 BÔNUS"
        draw_wrap(self.screen, self.font_mid, f"{tag} — {q['id']}", x0, y0, panel.width - 480)
        y = y0 + 50
        y = draw_wrap(self.screen, self.font_mid, q["prompt"], x0, y, panel.width - 480)

        option_rects = []
        oy = y + 10
        for i, opt in enumerate(q["options"]):
            r = pygame.Rect(x0, oy + i * 54, panel.width - 480, 46)
            option_rects.append((r, opt))
            hovered = r.collidepoint(pygame.mouse.get_pos())
            bg = (35, 48, 78) if not hovered else (55, 75, 115)
            pygame.draw.rect(self.screen, bg, r, border_radius=12)
            pygame.draw.rect(self.screen, (120, 150, 210), r, 2, border_radius=12)
            draw_wrap(self.screen, self.font, opt, r.x + 12, r.y + 12, r.width - 24)

        fb = pygame.Rect(x0, panel.bottom - 108, panel.width - 480, 80)
        pygame.draw.rect(self.screen, (10, 14, 26), fb, border_radius=14)
        pygame.draw.rect(self.screen, (90, 110, 150), fb, 2, border_radius=14)

        if self.feedback:
            col = (70, 230, 160) if self.feedback_ok else (255, 170, 110)
            draw_wrap(self.screen, self.font_mid, self.feedback, fb.x + 14, fb.y + 10, fb.width - 28, color=col)
            draw_wrap(self.screen, self.font, q["explain"], fb.x + 14, fb.y + 42, fb.width - 28)
        else:
            draw_wrap(self.screen, self.font, "Clique numa alternativa. (ESC volta para a sala).", fb.x + 14, fb.y + 28, fb.width - 28)

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and not self.fade.active:
                self.fade.start(on_mid=lambda: self.set_state("room"))

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

                            self.solved.add(qi)

                            if q["main"] and qi in [0,1,2,3,4]:
                                digit = MAIN_CODE_DIGITS[qi]
                                if digit not in self.collected_digits:
                                    self.collected_digits.append(digit)
                                self.keys_main = len([x for x in range(5) if x in self.solved])

                            self.fade.start(on_mid=lambda: self.set_state("room"))
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
            ov = pygame.Surface((W, H)); ov.fill((0, 0, 0)); ov.set_alpha(a)
            self.screen.blit(ov, (0, 0))

    def keypad(self, events, dt):
        self.draw_bg()
        self.draw_hud()

        panel = pygame.Rect(W - 290, H // 2 - 160, 260, 320)
        pygame.draw.rect(self.screen, (12, 18, 34), panel, border_radius=22)
        pygame.draw.rect(self.screen, (80, 110, 160), panel, 2, border_radius=22)

        draw_wrap(self.screen, self.font_mid, "TECLADO DA PORTA", panel.x + 16, panel.y + 18, panel.w - 32)
        draw_wrap(self.screen, self.font, "Digite o código e pressione ENTER.", panel.x + 16, panel.y + 54, panel.w - 32)

        disp = pygame.Rect(panel.x + 16, panel.y + 90, panel.w - 32, 44)
        pygame.draw.rect(self.screen, (10, 14, 26), disp, border_radius=12)
        pygame.draw.rect(self.screen, (90, 110, 150), disp, 2, border_radius=12)

        show = self.keypad_input + ("_" if (pygame.time.get_ticks() // 400) % 2 == 0 else "")
        self.screen.blit(self.font_mid.render(show, True, (235, 240, 255)), (disp.x + 12, disp.y + 8))

        hint = f"Dígitos coletados: {''.join(self.collected_digits)}"
        draw_wrap(self.screen, self.font, hint, panel.x + 16, panel.y + 146, panel.w - 32)

        if self.keys_main < 5:
            draw_wrap(self.screen, self.font, "Ainda faltam fases principais.", panel.x + 16, panel.y + 170, panel.w - 32, color=(255, 170, 110))

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and not self.fade.active:
                self.fade.start(on_mid=lambda: self.set_state("room"))

            if ev.type == pygame.KEYDOWN and not self.fade.active:
                if ev.key == pygame.K_BACKSPACE:
                    self.keypad_input = self.keypad_input[:-1]
                elif ev.key == pygame.K_RETURN:
                    if self.keys_main >= 5 and self.keypad_input == FINAL_CODE:
                        self.fade.start(on_mid=lambda: self.set_state("win"))
                    else:
                        self.keypad_input = ""
                        self.penalty += 10.0
                else:
                    ch = ev.unicode
                    if ch.isdigit() and len(self.keypad_input) < 8:
                        self.keypad_input += ch

        a = self.fade.update(dt)
        if a:
            ov = pygame.Surface((W, H)); ov.fill((0, 0, 0)); ov.set_alpha(a)
            self.screen.blit(ov, (0, 0))

    def win(self, events, dt):
        self.draw_bg()
        t = self.elapsed()
        mm, ss = int(t // 60), int(t % 60)

        msg = self.font_big.render("VOCÊ ESCAPOU! 🫀🌬️", True, (245, 248, 255))
        self.screen.blit(msg, msg.get_rect(center=(W // 2, 170)))

        txt = self.font_mid.render(f"Tempo: {mm:02d}:{ss:02d}   Pontos: {self.score}", True, (235, 240, 255))
        self.screen.blit(txt, txt.get_rect(center=(W // 2, 240)))

        tip = "ESC volta ao menu."
        draw_wrap(self.screen, self.font, tip, W // 2 - 180, 310, 360)

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and not self.fade.active:
                self.fade.start(on_mid=lambda: self.set_state("menu"))

        a = self.fade.update(dt)
        if a:
            ov = pygame.Surface((W, H)); ov.fill((0, 0, 0)); ov.set_alpha(a)
            self.screen.blit(ov, (0, 0))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            if self.state == "menu":
                self.menu(events, dt)
            elif self.state == "room":
                self.room(events, dt)
            elif self.state == "question":
                self.question(events, dt)
            elif self.state == "keypad":
                self.keypad(events, dt)
            elif self.state == "win":
                self.win(events, dt)

            pygame.display.flip()
