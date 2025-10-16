import pygame, numpy as np

def make_grayscale(surf: pygame.Surface) -> pygame.Surface:
    rgb = pygame.surfarray.array3d(surf).astype(np.float32)
    gray = (0.2126*rgb[:,:,0] + 0.7152*rgb[:,:,1] + 0.0722*rgb[:,:,2]).astype(np.uint8)
    gray3 = np.dstack([gray, gray, gray])
    gs = pygame.surfarray.make_surface(gray3).convert_alpha()
    # Alpha übernehmen, falls vorhanden
    try:
        a = pygame.surfarray.array_alpha(surf)
        pygame.surfarray.pixels_alpha(gs)[:,:] = a
    except ValueError:
        pass
    return gs

def blit_color_from_bottom(screen, color, gray, pos, p: float):
    p = max(0.0, min(1.0, p))
    x, y = pos
    w, h = color.get_size()
    # 1) Grau voll
    screen.blit(gray, pos)
    # 2) Unteren Anteil farbig
    hh = int(h * p)
    if hh > 0:
        src = pygame.Rect(0, h - hh, w, hh)
        screen.blit(color, (x, y + h - hh), src)

def blit_color_from_bottom_feather(screen, color, gray, pos, p, feather=12):
    p = max(0.0, min(1.0, p))
    x, y = pos
    w, h = color.get_size()
    screen.blit(gray, pos)
    hh = int(h * p)
    if hh <= 0: return
    # Vollfarbbereich
    core = max(0, hh - feather)
    if core > 0:
        src = pygame.Rect(0, h - hh, w, core)
        screen.blit(color, (x, y + h - hh), src)
    # Übergangsstreifen
    if hh > core and feather > 0:
        band_h = min(feather, hh)
        src2 = pygame.Rect(0, h - (hh - core), w, band_h)
        band = color.subsurface(src2).copy()
        # vertikaler Alpha-Gradient
        grad = pygame.Surface((w, band_h), pygame.SRCALPHA)
        for i in range(band_h):
            a = int(255 * (i+1) / band_h)
            grad.fill((255,255,255,a), pygame.Rect(0,i,w,1))
        band.blit(grad, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(band, (x, y + h - (hh - core)))


# Demo
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    img_color = pygame.image.load("assets/images/icon/shield.png").convert_alpha()
    img_gray  = make_grayscale(img_color)

    clock = pygame.time.Clock()
    p = 0.0
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False

        # Beispiel: lädt hoch
        p = min(1.0, p + 0.005)  # ersetze durch echten Ladefortschritt

        screen.fill((20,20,20))
        blit_color_from_bottom_feather(screen, img_color, img_gray, (200,100), p)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
