import pygame
import random

pygame.init()

AMBIENCE = pygame.mixer.Sound("assets/audio/ambience.wav")
JOURNAL_SFX = pygame.mixer.Sound("assets/audio/journal.wav")
MOUSE_SFX = pygame.mixer.Sound("assets/audio/mouse_over.wav")
MOUSE_SFX.set_volume(0)
SELECT_SFX = pygame.mixer.Sound("assets/audio/select.wav")
TEXT_SFX = [pygame.mixer.Sound(f"assets/audio/text{i + 1}.wav") for i in range(4)]
for t in TEXT_SFX: t.set_volume(0)

SMALL_FONT = pygame.font.SysFont("courier", 16)
FONT = pygame.font.SysFont("courier", 32)
JOURNAL_FONT = pygame.font.SysFont("courier", 28)

WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Glossolalia")

from glyphs import *
from journal import pages, journal_glyph_data
from dictionary import dictionary

player_dictionary = {
    "~a": "."
}

def clamp(a, minv, maxv):
    return min(max(minv, a), maxv)

def darken(c, a=0.1):
    c = pygame.Color(c)
    v = 1-a
    return c.r * v, c.g * v, c.b * v

def translate(gloss: str):
    final = []
    for line in gloss.split('\n'):
        text = ""
        for bit in line.split(' '):
            text += '-a'.join(dictionary[token] for token in filter(lambda t: t in dictionary, bit.split('.')))
            text += " "
        final.append(text[:-1])
    return "\n".join(final)

def thought_translation(string: str):
    output = []
    for line in string.splitlines():
        words = line.split(' ')
        final_words = []
        for word in words:
            if '-a' in word:
                for w in word.split('-a'):
                    final_words.append(w)
                    final_words.append('-')
                final_words.pop()
            else:
                final_words.append(word)
        for w in final_words:
            if w not in player_dictionary.keys() and w != '-':
                player_dictionary.update({w: "???"})
        output.append(" ".join([player_dictionary[a] if a != '-' else '-' for a in final_words]))
    return "\n".join(output)

def main():
    clock = pygame.time.Clock()
    delta = 0

    scroll_y = 0

    percent = 0

    journal_open = False
    journal_open_time = 0.0
    journal_tab = 0
    tabs = [
        "Pg 1",
        "Pg 2",
        "Pg 3",
        "Pg 4",
        "Pg 5",
    ]

    texts = [
        # "we thank the gods for feeding us"
        ("A Prayer Carved\nInto the Side\nof a Bowl", translate("we god.PL we\nfeed thank STOP")),
        # "we need milk, nuts, and eggs"
        ("A Grocery List\nWritten on a\nScrap Piece of\nPaper", translate("we milk and nut\nand egg need STOP")),
        # "i want you to know [that] i love you"
        ("A Love Note\nHidden Under a\nFloor Tile", translate("i you i you love know want STOP")),
        # "don't run in the house"
        ("A Family Rule\nEtched Into the\nFireplace Mantle", translate("you house LOC STOP you run NEG STOP")),
        # "the bird and the fish were arguing. the bird and the fish spoke with each other. the bird said the the fish, 'we should not be arguing. it is not helpful'. the bird and the fish no longer argued."
        ("A Folk Tale\nWritten on a\nScrap of Paper", translate("bird and fish dispute.PERF STOP\nbird and fish self talk.PERF\nSTOP bird we self dispute should\nNEG say.PERF STOP bird and fish\ndispute.PERF NEG STOP")),
        ("A Joke Painted\non the Inside\nof a Closet Door", translate("")),
        ("A Blessing Hidden\nUnder the Lip of\na Chalice", translate("")),
        ("A Lost Prayer\nSewn into a Wound\nDressing", translate("")),
        ("A Code Hidden\nin the Folds of\na Flag", translate("")),
        ("A False\nConfession\nWritten in Ink", translate("")),
        ("test", translate("you who forest go and\nwho and water leave know want\nQUESTION STOP i you can tell STOP she\npale woman is STOP\nbird and fish dispute.PERF STOP\nbird and fish self talk.PERF\nSTOP bird we self dispute should\nNEG say.PERF STOP bird and fish\ndispute.PERF NEG STOP")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
        ("test", translate("")),
    ]

    current_text = 0
    texts_per_line = 5

    editing_word = None

    in_menu = True

    AMBIENCE.play(-1)

    mouse_over = -1

    run = True
    while run:
        left_click = False

        delta = clock.tick_busy_loop(30.0) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: left_click = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if not editing_word and not in_menu:
                        journal_open = not journal_open
                        journal_open_time = 1.0
                        JOURNAL_SFX.play()
                elif event.key == pygame.K_BACKSPACE:
                    if editing_word:
                        player_dictionary[editing_word] = player_dictionary[editing_word][:-1]
                elif event.key == pygame.K_RETURN:
                    if editing_word:
                        if player_dictionary[editing_word] == "":
                            player_dictionary[editing_word] = "???"
                        editing_word = None
                elif event.key == pygame.K_ESCAPE:
                    if not editing_word and not journal_open:
                        in_menu = True
                        current_text = -1
                        mouse_over = -1
            elif event.type == pygame.TEXTINPUT:
                if editing_word:
                    if len(player_dictionary[editing_word]) < 10:
                        a = event.text
                        player_dictionary[editing_word] += a
            elif event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * 25

                scroll_y = clamp(scroll_y, 0, 500)

        if journal_open_time:
            journal_open_time = max(0, journal_open_time - delta)

        if not journal_open and not in_menu:
            t = texts[current_text][1]
            t = t[:int(len(t) * percent)]
            percent = min(1, percent + delta / 2.0)
            t2 = texts[current_text][1]
            t2 = t2[:int(len(t2) * percent)]
            if len(t) and t != t2 and t[-1] in ' aeiou' and t2[-1] != ' ':
                random.choice(TEXT_SFX).play()
            if left_click:
                x = 0
                y = 60
                h = 60
                text = texts[current_text][1]
                for line in text.splitlines():
                    words = []
                    wds = line.split(' ')

                    for w in wds:
                        words += w.split('-a')

                    for word in words:
                        w = 60 * (len(word) // 2)
                        if pygame.Rect(x, y - scroll_y, w, h).collidepoint(pygame.mouse.get_pos()):
                            editing_word = word
                            SELECT_SFX.play()
                        x += w + 60
                    x = 0
                    y += 60

        screen.fill('#26353F')

        t = pygame.time.get_ticks() // 150
        t %= 60

        for x in range(WIDTH // 60 + 1):
            for y in range(HEIGHT // 60 + 1):
                if (x + y) & 1:
                    r = (-t + 30 + x * 60 + -t + 30 + y * 60) / (WIDTH + HEIGHT)
                    r = 1 - abs(2 * (r - 0.5))
                    r *= 30
                    pygame.draw.circle(screen, '#22313B', (-t + 30 + x * 60, -t + 30 + y * 60), r)

        if in_menu:
            ox = WIDTH // 2 - (190 * min(len(texts), texts_per_line) - 10) // 2
            oy = ox
            for i in range(len(texts)):
                x = ox + 190 * (i % texts_per_line)
                y = oy + 110 * (i // texts_per_line)
                c = pygame.Color("#408040").lerp("#804040", (i // texts_per_line) / (len(texts) // texts_per_line))
                r = pygame.Rect(x, y, 180, 100)
                if r.collidepoint(pygame.mouse.get_pos()):
                    if mouse_over != i:
                        MOUSE_SFX.play()
                    mouse_over = i
                    if left_click:
                        in_menu = False
                        current_text = i
                        percent = 0
                        SELECT_SFX.play()
                    pygame.draw.rect(screen, c, r, 0, 8)
                else:
                    pygame.draw.rect(screen, darken(c), r, 0, 8)
                screen.blit(t := SMALL_FONT.render(texts[i][0], True, 'white'), (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))
        else:
            text = texts[current_text][1]

            screen.blit(FONT.render("You see:", True, '#ffff80'), (4, 4 - scroll_y))
            draw_text(text, screen, 2, 62 - scroll_y, percent, 'black',  editing_word)
            draw_text(text, screen, 0, 60 - scroll_y, percent, '#80ff80',  editing_word)

            screen.blit(FONT.render("You think this means:", True, '#ffff80'), (4, -scroll_y + 60 + 60 * len(text.splitlines()) + 4))
            shown_translation = "\n".join(" ".join([a for a in line.split(' ')]) for line in text.splitlines())
            tt = thought_translation(shown_translation)
            for i, line in enumerate(tt[:int(len(tt) * percent)].splitlines()):
                screen.blit(FONT.render(line, True, 'black'), (6, -scroll_y + 122 + 60 * (len(text.splitlines()) + i) + 4))
                screen.blit(FONT.render(line, True, '#80ff80'), (4, -scroll_y + 120 + 60 * (len(text.splitlines()) + i) + 4))

            if journal_open or journal_open_time:
                journal_surf = pygame.Surface((WIDTH * 0.8, HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(journal_surf, '#36454F', (0, 0, *journal_surf.get_size()), 0, 8)

                n_tabs = len(tabs)
                tab_width = journal_surf.get_width() / n_tabs

                for i in range(n_tabs):
                    if journal_tab == i:
                        color = '#36454F'
                    else:
                        color = '#46555F'
                    pygame.draw.rect(journal_surf, color, (i * tab_width, 0, tab_width, 20), 0, -1, 8, 8)
                    journal_surf.blit(t := SMALL_FONT.render(tabs[i], True, 'white' if journal_tab == i else 'gray'), (i * tab_width + tab_width // 2 - t.get_width() // 2, 10 - t.get_height() // 2))

                    if pygame.Rect(WIDTH - journal_surf.get_width() + i * tab_width, 0, tab_width, 20).collidepoint(pygame.mouse.get_pos()) and left_click:
                        journal_tab = i
                        JOURNAL_SFX.play()

                k = journal_tab
                journal_surf.blit(JOURNAL_FONT.render(pages[k], True, 'white'), (0, 20))

                for gd in journal_glyph_data[k]:
                    draw_text(gd["text"], journal_surf, gd['x'], gd['y'] + 20)

                screen.blit(journal_surf, (WIDTH - (journal_surf.get_width() * pow(1 - journal_open_time if journal_open else journal_open_time, 2.0)), 0))
            else:
                pygame.draw.aacircle(screen, 'gray', (WIDTH - 6, 6 + (HEIGHT - 12) * (scroll_y / 500)), 4)

            if editing_word:
                t = FONT.render(player_dictionary[editing_word] + ('|' if (pygame.time.get_ticks() // 500) & 1 else ' '), True, '#80ff80')
                x, y = -4 + WIDTH // 2 - t.get_width() // 2, -4 + HEIGHT // 2 - t.get_height() // 2
                pygame.draw.rect(screen, '#46555F', (x, y, t.get_width() + 8, t.get_height() + 8), 0, 8)
                screen.blit(t, (x + 4, y + 4))

        pygame.display.flip()

    pygame.quit()

main()