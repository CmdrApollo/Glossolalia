import pygame

TS = 60

SIZE = 32

GLYPH_IMAGE = pygame.image.load("assets/visuals/glyphsSerif.png").convert_alpha()
MODIFIERS_IMAGE = pygame.image.load("assets/visuals/modifiers.png").convert_alpha()

GLYPHS = {}

for i, cons in enumerate(['p', 'b', 't', 'd', 'k', 'g', 'C', 'j', 's', 'S', 'Z', 'h', 'm', 'n', 'r', 'y', 'w', '\'', '-', '~']):
    x = i % 10
    y = i // 10
    GLYPHS[cons] = GLYPH_IMAGE.subsurface(x * SIZE, y * SIZE, SIZE, SIZE)

MODIFIERS = [MODIFIERS_IMAGE.subsurface(i * 16, 0, 16, 16) for i in range(5)]

def draw_syllable(syllable, surf: pygame.Surface, x, y, color='white'):
    s = 2
    if syllable[:-1] in ['b', 'd', 'g', 'j', 'Z']:
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

def draw_text(text: str, surf, x, y, percent=1, color='white', highlight: str|None = None):
    ox = x
    for line in text[:int(len(text) * percent)].splitlines():
        raw_words = line.split()
        segments = []
        for word in raw_words:
            parts = word.split('-a')
            for i, part in enumerate(parts):
                if part:
                    segments.append(part)
                if i < len(parts) - 1:
                    segments.append('-a')  # treat dash as a valid syllable

        i = 0
        while i < len(segments):
            segment = segments[i]
            if segment == '-a':
                draw_syllable(
                    '-a', surf, x + 36, y + 36,
                    'yellow' if segment == highlight and color != 'black' else color
                )
                x += 60  # dash takes up exactly one space
                i += 1
                continue

            syl = ""
            for char in segment:
                syl += char
                if syl[-1] in 'aeiou':
                    draw_syllable(
                        syl, surf, x + 36, y + 36,
                        'yellow' if segment == highlight and color != 'black' else color
                    )
                    syl = ""
                    x += 60

            # Only add a space after non-dash segments, and only if the next one isn’t a dash
            if i + 1 < len(segments) and segments[i + 1] != '-a':
                x += 60  # space between words

            i += 1

        x = ox
        y += 60