import pygame

SIZE = 32

GLYPH_IMAGE = pygame.image.load("assets/visuals/glyphs.png").convert_alpha()
MODIFIERS_IMAGE = pygame.image.load("assets/visuals/modifiers.png").convert_alpha()

GLYPHS = {}

for i, cons in enumerate(['p', 'b', 't', 'd', 'k', 'g', 'ch', 'j', 's', 'sh', 'zh', 'h', 'm', 'n', 'r', 'y', 'w', '\'', '-', '~']):
    x = i % 10
    y = i // 10
    GLYPHS[cons] = GLYPH_IMAGE.subsurface(x * SIZE, y * SIZE, SIZE, SIZE)

MODIFIERS = [MODIFIERS_IMAGE.subsurface(i * 16, 0, 16, 16) for i in range(5)]

def draw_syllable(syllable, surf: pygame.Surface, x, y, color='white'):
    s = 2
    if syllable[:-1] in ['b', 'd', 'g', 'j', 'zh']:
        # draw voicing diacritic
        m = MODIFIERS[0].copy()
        m.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(m, (x - SIZE - s, y - 8))

    g = GLYPHS[syllable[:-1]].copy()
    g.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(g, (x - SIZE // 2, y - SIZE // 2))
    
    body = pygame.Rect(x - SIZE // 2, y - SIZE // 2, g.get_width(), g.get_height())

    match syllable[-1]:
        # draw vowel markers
        case 'a':
            pass
        case 'i':
            m = MODIFIERS[1].copy()
            m.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(m, (x - 8, y - SIZE - s))
        case 'u':
            m = MODIFIERS[2].copy()
            m.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(m, (x - 8, y - SIZE - s))
        case 'e':
            m = MODIFIERS[3].copy()
            m.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(m, (x - 8, y - SIZE - s))
        case 'o':
            m = MODIFIERS[4].copy()
            m.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(m, (x - 8, y - SIZE - s))
    
    return body

def draw_text(text: str, surf, x, y, percent=1, color='white'):
    ox = x
    syl = ""
    for i in range(len(text[:int(len(text) * percent)])):
        if text[i] == ' ':
            x += 60
            continue
            
        if text[i] == '\n':
            y += 60
            x = ox
            continue

        syl += text[i]
        if syl[-1] in 'aeiou':
            draw_syllable(syl, surf, x + 36, y + 36, color)
            x += 60

            syl = ""