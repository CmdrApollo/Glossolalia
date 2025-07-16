import pygame

pygame.init()

SMALL_FONT = pygame.font.SysFont("courier", 16)
FONT = pygame.font.SysFont("courier", 32)
JOURNAL_FONT = pygame.font.SysFont("courier", 28)

WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Glossolalia")

from glyphs import *
from journal import pages
from dictionary import dictionary

player_dictionary = {
    "~a": "."
}

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
        translate("she fish eat.FUT STOP\nshe and man forest go.FUT STOP"),
        translate("you what with bird water sit\nsee.PERF QUESTION STOP"),
        translate("he and me and small_animal eat.PAST\n1.PL river sit.PAST STOP"),
        translate("you who forest go and\nwho and water leave know want\nQUESTION STOP i you talk know STOP she\npale woman is STOP"),
        translate("me and bird man who\nis know want STOP"),
        translate("1.PL man who is know\nwant.PERF STOP")
    ]

    current_text = 0

    editing_word = None

    run = True
    while run:
        left_click = False

        delta = clock.tick_busy_loop(30.0) / 1000.0

        percent += delta / 2.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: left_click = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    journal_open = not journal_open
                    journal_open_time = 1.0
                elif event.key == pygame.K_BACKSPACE:
                    if editing_word:
                        player_dictionary[editing_word] = player_dictionary[editing_word][:-1]
                elif event.key == pygame.K_RETURN:
                    if editing_word:
                        if player_dictionary[editing_word] == "":
                            player_dictionary[editing_word] = "???"
                        editing_word = None
            elif event.type == pygame.TEXTINPUT:
                if editing_word:
                    if len(player_dictionary[editing_word]) < 10:
                        a = event.text
                        player_dictionary[editing_word] += a

        if journal_open_time:
            journal_open_time = max(0, journal_open_time - delta)

        if left_click and not journal_open:
            x = 0
            y = 60
            h = 60
            text = texts[current_text]
            for line in text.splitlines():
                words = []
                wds = line.split(' ')

                for w in wds:
                    words += w.split('-a')

                for word in words:
                    w = 60 * (len(word) // 2)
                    if pygame.Rect(x, y, w, h).collidepoint(pygame.mouse.get_pos()):
                        editing_word = word
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

        text = texts[current_text]

        screen.blit(FONT.render("You see:", False, '#ffff80'), (4, 4))
        draw_text(text, screen, 2, 62, percent, 'black',  editing_word)
        draw_text(text, screen, 0, 60, percent, '#80ff80',  editing_word)

        screen.blit(FONT.render("You think this means:", False, '#ffff80'), (4, 60 + 60 * len(text.splitlines()) + 4))
        shown_translation = "\n".join(" ".join([a for a in line.split(' ')]) for line in text.splitlines())
        tt = thought_translation(shown_translation)
        for i, line in enumerate(tt[:int(len(tt) * percent)].splitlines()):
            screen.blit(FONT.render(line, False, 'black'), (6, 122 + 60 * (len(text.splitlines()) + i) + 4))
            screen.blit(FONT.render(line, False, '#80ff80'), (4, 120 + 60 * (len(text.splitlines()) + i) + 4))

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
                journal_surf.blit(t := SMALL_FONT.render(tabs[i], False, 'white' if journal_tab == i else 'gray'), (i * tab_width + tab_width // 2 - t.get_width() // 2, 10 - t.get_height() // 2))

                if pygame.Rect(WIDTH - journal_surf.get_width() + i * tab_width, 0, tab_width, 20).collidepoint(pygame.mouse.get_pos()) and left_click:
                    journal_tab = i

            k = int(tabs[journal_tab][-1]) - 1
            journal_surf.blit(JOURNAL_FONT.render(pages[k], False, 'white'), (0, 20))

            screen.blit(journal_surf, (WIDTH - (journal_surf.get_width() * pow(1 - journal_open_time if journal_open else journal_open_time, 2.0)), 0))

        if editing_word:
            t = FONT.render(player_dictionary[editing_word] + ('|' if (pygame.time.get_ticks() // 500) & 1 else ' '), False, '#80ff80')
            x, y = -4 + WIDTH // 2 - t.get_width() // 2, -4 + HEIGHT // 2 - t.get_height() // 2
            pygame.draw.rect(screen, '#46555F', (x, y, t.get_width() + 8, t.get_height() + 8), 0, 8)
            screen.blit(t, (x + 4, y + 4))

        pygame.display.flip()

    pygame.quit()

main()