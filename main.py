import pygame

pygame.init()

FONT = pygame.font.SysFont("courier", 32)

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Glossolalia")

from glyphs import *

dictionary = {
    "eat": "poke'i",
    "consume": "poke'i",
    "see": "pujo",
    "bird": "'ako",
    "fish": "'ako",
    "small_animal": "'ako",
    "person": "chati",
    "man": "chati",
    "woman": "chati",
    "1": "wa",
    "i": "wa",
    "me": "wa",
    "2": "di",
    "you": "di",
    "3": "to",
    "he": "to",
    "him": "to",
    "she": "to",
    "her": "to",
    "it": "to",
    "PERF": "na",
    "finish": "na",
    "QUESTION": "ku",
    "?": "ku",
    "FUTURE": "so",
    "FUT": "so",
    "go": "so",
    "and": "re",
    "with": "re",
    "be": "'abu",
    "live": "'abu",
    "exist": "'abu",
    "want": "jota",
    "desire": "jota",
    "talk": "kepa",
    "speak": "kepa",
    "leave": "'echa"
}

player_dictionary = {}

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
            if w not in player_dictionary.keys():
                player_dictionary.update({w: "???"})
        output.append(" ".join([player_dictionary[a] if a != '-' else '-' for a in final_words]))
    return "\n".join(output)

def main():
    clock = pygame.time.Clock()
    delta = 0

    percent = 0

    journal_open = False

    journal_open_time = 0.0

    run = True
    while run:
        delta = clock.tick_busy_loop(30.0) / 1000.0

        percent += delta / 2.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    journal_open = not journal_open
                    journal_open_time = 1.0
        
        if journal_open_time:
            journal_open_time = max(0, journal_open_time - delta)

        screen.fill('#26353F')

        t = pygame.time.get_ticks() // 150
        t %= 50

        for x in range(WIDTH // 50 + 1):
            for y in range(HEIGHT // 50 + 1):
                if (x + y) & 1:
                    r = (-t + 25 + x * 50 + -t + 25 + y * 50) / (WIDTH + HEIGHT)
                    r = 1 - abs(2 * (r - 0.5))
                    r *= 25
                    pygame.draw.circle(screen, '#22313B', (-t + 25 + x * 50, -t + 25 + y * 50), r)

        text = translate("bird man see.PERF\nbird and man talk.PERF\nbird leave want.PERF\nman bird eat.PERF")

        screen.blit(FONT.render("You see:", False, '#ffff80'), (4, 4))
        draw_text(text, screen, 2, 62, percent, 'black')
        draw_text(text, screen, 0, 60, percent, '#80ff80')

        screen.blit(FONT.render("You think this means:", False, '#ffff80'), (4, 60 + 60 * len(text.splitlines()) + 4))
        shown_translation = "\n".join(" ".join([a for a in line.split(' ')]) for line in text.splitlines())
        tt = thought_translation(shown_translation)
        for i, line in enumerate(tt[:int(len(tt) * percent)].splitlines()):
            screen.blit(FONT.render(line, False, 'black'), (6, 122 + 60 * (len(text.splitlines()) + i) + 4))
            screen.blit(FONT.render(line, False, '#80ff80'), (4, 120 + 60 * (len(text.splitlines()) + i) + 4))

        if journal_open or journal_open_time:
            journal_surf = pygame.Surface((WIDTH // 2, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(journal_surf, '#36454F', (0, 0, *journal_surf.get_size()), 0, 8)

            screen.blit(journal_surf, (WIDTH - (journal_surf.get_width() * pow(1 - journal_open_time if journal_open else journal_open_time, 2.0)), 0))

        pygame.display.flip()

    pygame.quit()

main()