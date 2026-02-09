import os
import pygame

def load_image(images_dir: str, filename: str, max_size=(420, 420)):
    path = os.path.join(images_dir, filename)
    if not os.path.exists(path):
        return None

    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    mw, mh = max_size
    scale = min(mw / w, mh / h, 1.0)

    if scale < 1.0:
        img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
    return img
