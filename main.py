import pygame
import json
from random import choice
import math

pygame.init()

JOURNAL_SFX = pygame.mixer.Sound("assets/audio/journal.wav")
JOURNAL_SFX.set_volume(0.1)
MOUSE_SFX = pygame.mixer.Sound("assets/audio/mouse_over.wav")
MOUSE_SFX.set_volume(0.1)
SELECT_SFX = pygame.mixer.Sound("assets/audio/select.wav")
SELECT_SFX.set_volume(0.1)
MUSIC = [pygame.mixer.Sound(f"assets/audio/track{i + 1}.wav") for i in range(5)]
for m in MUSIC: m.set_volume(0.1)

bag = MUSIC.copy()

SMALL_FONT = pygame.font.SysFont("courier", 16)
FONT = pygame.font.SysFont("courier", 32)
JOURNAL_FONT = pygame.font.SysFont("courier", 28)
BIG_FONT = pygame.font.SysFont("courier", 56)

TS = 60

WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_icon(pygame.image.load("assets/icon.bmp"))
pygame.display.set_caption("Glossolalia")

TITLE = pygame.image.load("assets/visuals/title.png").convert_alpha()

from glyphs import *
from journal import pages, journal_glyph_data
from dictionary import dictionary

for k, v in dictionary.items():
    if "ch" in v:
        dictionary.update({k: v.replace("ch", "C")})
    if "sh" in v:
        dictionary.update({k: v.replace("sh", "S")})
    if "zh" in v:
        dictionary.update({k: v.replace("zh", "Z")})

data = json.load(open("data/save.json", "r", encoding="utf-8"))

player_dictionary = data['dictionary']

def clamp(a, minv, maxv):
    return min(max(minv, a), maxv)

def darken(c, a=0.1):
    c = pygame.Color(c)
    v = 1-a
    return c.r * v, c.g * v, c.b * v

def translate(gloss: str, max_width: int = 36):
    final = []
    current_line = ""
    current_length = 0

    for bit in gloss.split(' '):
        word = '-a'.join(dictionary[token] for token in filter(lambda t: t in dictionary, bit.split('.')))
        word_length = len(word)

        # A space between words takes up 2 character units
        if current_length + (2 if current_line else 0) + word_length > max_width:
            final.append(current_line)
            current_line = word
            current_length = word_length
        else:
            if current_line:
                current_line += " " + word
                current_length += 2 + word_length
            else:
                current_line = word
                current_length = word_length

    if current_line:
        final.append(current_line)

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

    def main_menu():
        mouse_over = 0

        run = True
        while run:
            delta = clock.tick_busy_loop(30.0) / 1000.0

            left_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    left_click = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        run = False
            
            screen.fill('#26353F')

            t = pygame.time.get_ticks() // 150
            t %= TS

            for x in range(WIDTH // TS + 1):
                for y in range(HEIGHT // TS + 1):
                    if (x + y) & 1:
                        r = (-t + TS // 2 + x * TS + -t + TS // 2 + y * TS) / (WIDTH + HEIGHT)
                        r = 1 - abs(2 * (r - 0.5))
                        r *= TS // 2
                        pygame.draw.circle(screen, '#22313B', (-t + TS // 2 + x * TS, -t + TS // 2 + y * TS), r)
            
            screen.blit(TITLE, (WIDTH // 2 - TITLE.get_width() // 2, HEIGHT // 4 - TITLE.get_height() // 2 + math.sin(pygame.time.get_ticks() / 400) * 6))

            ox = WIDTH // 2 - 90
            oy = HEIGHT * 0.75
            for i in range(2):
                x = ox
                y = oy + i * 60
                c = '#404040'
                w = 180
                r = pygame.Rect(x, y, w, 50)
                if r.collidepoint(pygame.mouse.get_pos()):
                    if mouse_over != i:
                        MOUSE_SFX.play()
                    mouse_over = i
                    if left_click:
                        if i == 0:
                            run = False
                        else:
                            return False
                        SELECT_SFX.play()
                    pygame.draw.rect(screen, c, r, 0, 8)
                else:
                    pygame.draw.rect(screen, darken(c), r, 0, 8)
                screen.blit(t := SMALL_FONT.render(["Play", "Quit"][i], True, 'white'), (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))
        
            pygame.display.flip()
        
        return True

    def game():
        global MUSIC, bag, player_dictionary

        gloss_percent = 0

        scroll_y = 0

        percent = 0

        journal_open = False
        journal_open_time = 0.0
        journal_tab = 0
        tabs = data['tabs']

        texts = [
            # "we thank the gods for feeding us"
            ("A Meal-time\nPrayer", translate("we god.PL we food give thank STOP")),
            # "we need milk, nuts, and eggs"
            ("A Grocery List", translate("we milk and nut and egg need STOP")),
            # "i want you to know [that] i love you"
            ("A Love Note", translate("i you i you love know want STOP")),
            # "don't run in the house"
            ("A Family Rule", translate("you house when LOC you run NEG STOP")),
            # "the bird and the fish were arguing. the bird and the fish spoke with each other. the bird said the the fish, 'we should not be arguing. it is not helpful'. the bird and the fish no longer argued."
            ("A Folk Tale", translate("bird and fish dispute.PERF STOP bird and fish self talk.PERF STOP bird we self dispute should NEG say.PERF STOP bird and fish dispute.PERF NEG STOP")),
            # "why did the person fight the cow? they wanted milk."
            ("A Joke", translate("man cow why fight.PERF STOP he milk want.PERF STOP")),
            # "the gods are protecting us. we are fed. we are safe."
            ("A Blessing", translate("god.PL we protect STOP we feed take STOP we safe be STOP")),
            # "we thank the gods. they give us food. they let us eat. they let us live."
            ("A Lost Prayer", translate("we god.PL thank STOP 3.PL we food give STOP 3.PL we eat let STOP 3.PL we live let STOP")),
            # "leave the house. run to the forest. watch the river."
            ("Secret\nInstructions", translate("you house leave STOP you forest run STOP you river watch STOP")),
            # "i said that i fought. i didn't fight. i couldn't fight."
            ("A Confession", translate("i i fight.PERF say.PERF STOP i fight.PERF NEG STOP i fight can.PERF NEG STOP")),
            # "you want to know who enters the forest and leaves with water? i can tell you. she is the pale-lady."
            ("The Pale-Lady", translate("you who forest go and who and water leave know want QUESTION STOP i you tell can STOP she pale woman is STOP")),
            # "the warrior went to the town's tavern. he desired a drink and a bed. after drinking, he slept for a long time. when he woke up, he couldn't find anybody."
            ("The Warrior", translate("warrior town.GEN bed.house go.PERF STOP he consume.NMLZ and bed desire.PERF STOP consume.NMLZ.GEN lead.NMLZ.hour LOC PASSIVE warrior large time sleep.PERF STOP he sleep.NMLZ when finish he nobody find can.PERF STOP")),
            # "during the dark hour, do not go to the river. do not follow the light. when you hear your name spoken, do not speak."
            ("A Warning", translate("dark hour LOC you river go NEG STOP you light go NEG STOP you you.GEN name when hear you speak NEG STOP")),
            # "as i speak, my words come back to me. they never leave me alone. they consume me, returning me to the gods."
            ("An Echo", translate("i speak STOP 1.GEN word return STOP never they me peace give STOP they me consume and they god.PL me give STOP")),
            # "the knife cuts. the chicken dies. the person eats. the time ends. what is the knife? what causes death? what killed the chicken? the person sees. the person knows. the person watches. the gods are dark. the gods are light. the gods are. the person eats."
            ("A Poem", translate("knife cut STOP chicken die STOP person eat STOP time finish STOP what knife be QUESTION STOP what death cause QUESTION STOP what chicken die cause QUESTION STOP person see STOP person know STOP person watch STOP god.PL black be STOP god.PL white be STOP god.PL be STOP person eat STOP")),
            # "when you find us, we will kill you. you should end your search. if you don't stop, we will find you and we will kill you."
            ("A Threat", translate("you we when find we you die cause.FUT STOP you you.GEN find.NMLZ finish should STOP you if finish NEG we you find.FUT and we you die cause.FUT STOP")),
            ("A Voice", translate("")),
            ("A Message in\nReverse", translate("")),
            ("A Testimony", translate("")),
            ("A Farewell", translate("")),
            # "begin log. it appears that we have been compromised. subject has become aware of sensitive information. it is unclear what the subject plans to do with this information. however, subject must be terminated at all costs. if we fail in this task, subject may spread unwanted knowledge to others. such an outcome must be avoided by any means necessary. the powers that be require our success in this endeavor, we must not fail them. for if we do, we have failed the well-being of our country. praise the gods and good luck on this mission. end log."
            ("Glossolalia", translate("speech begin STOP i we find take.PERF think STOP subject important know.NOM find.PERF STOP i subject perform plan know NEG but we subject die cause need.need STOP we if fail subject person.PL know.NOM give can STOP we this stop need.need STOP leader.PL we.GEN succeed.NOM need STOP we they fail need.need NEG STOP we if fail we we.GEN country.GEN health fail.FUT STOP we god.PL thank STOP i they you.PL strength give hope STOP speech finish STOP")),
        ]

        unused_words = []
        used_words = []

        for _, t in texts:
            for line in t.splitlines():
                used_words += line.split(' ')
                for bit in line.split(' '):
                    used_words += bit.split('-a')

        used_words = list(set(used_words))

        for word in dictionary:
            if dictionary[word] not in used_words and word not in unused_words:
                unused_words.append(word)
        
        open('unused.txt', 'w').write('\n'.join(sorted(unused_words)))

        current_text = 0
        texts_per_line = 5

        editing_word = None

        in_menu = True

        mouse_over = -1

        current_song = choice(MUSIC)
        MUSIC.remove(current_song)
        current_song.play(fade_ms=1000)
        length = current_song.get_length()

        song_timer = 0

        popup = ""
        popup_time = 0.0

        run = True
        while run:
            ogp = gloss_percent

            gloss_percent = 0
            for word in player_dictionary:
                if word != '~a' and not "?" in player_dictionary[word] and player_dictionary[word] != "":
                    gloss_percent = min(1, gloss_percent + 1 / (len(set(dictionary.values())) - 1))

            if ogp < gloss_percent:
                if gloss_percent >= 0.4:
                    if "Pg 8" not in tabs:
                        tabs.append("Pg 8")
                        popup = "New Journal Entry Unlocked!"
                        popup_time = 1.0
                    if "Pg 9" not in tabs:
                        tabs.append("Pg 9")
                        popup = "New Journal Entry Unlocked!"
                        popup_time = 1.0
                elif gloss_percent >= 0.2:
                    if "Pg 6" not in tabs:
                        tabs.append("Pg 6")
                        popup = "New Journal Entry Unlocked!"
                        popup_time = 1.0
                    if "Pg 7" not in tabs:
                        tabs.append("Pg 7")
                        popup = "New Journal Entry Unlocked!"
                        popup_time = 1.0

            left_click = False

            delta = clock.tick_busy_loop(30.0) / 1000.0

            song_timer += delta
            if song_timer >= length:
                if not len(MUSIC):
                    MUSIC = bag.copy()

                current_song = choice(MUSIC)
                MUSIC.remove(current_song)
                current_song.play(fade_ms=1000)
                length = current_song.get_length()

                song_timer = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    json.dump({"tabs": tabs, "dictionary": player_dictionary}, open("data/save.json", "w", encoding="utf-8"))
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: left_click = True
                    if event.button == 3: print(f"{gloss_percent * 100:.2f}")
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
                    scroll_y -= event.y * 50

                    scroll_y = clamp(scroll_y, 0, 1250)

            if journal_open_time:
                journal_open_time = max(0, journal_open_time - delta)

            if not journal_open and not in_menu:
                t = texts[current_text][1]
                t = t[:int(len(t) * percent)]
                percent = min(1, percent + delta / 2.0)
                t2 = texts[current_text][1]
                t2 = t2[:int(len(t2) * percent)]
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
            t %= TS

            for x in range(WIDTH // TS + 1):
                for y in range(HEIGHT // TS + 1):
                    if (x + y) & 1:
                        r = (-t + TS // 2 + x * TS + -t + TS // 2 + y * TS) / (WIDTH + HEIGHT)
                        r = 1 - abs(2 * (r - 0.5))
                        r *= TS // 2
                        pygame.draw.circle(screen, '#22313B', (-t + TS // 2 + x * TS, -t + TS // 2 + y * TS), r)

            if in_menu:
                ox = WIDTH // 2 - (190 * min(len(texts), texts_per_line) - 10) // 2
                oy = ox // 2 + 60
                for i in range(len(texts) - 1 if gloss_percent < 0.6 else len(texts)):
                    x = ox + 190 * (i % texts_per_line)
                    y = oy + 110 * (i // texts_per_line)
                    c = pygame.Color("#408040").lerp("#804040", (i // texts_per_line) / (len(texts) // texts_per_line))
                    w = 180
                    if i == len(texts) - 1:
                        w *= 5
                        w += 40
                    r = pygame.Rect(x, y, w, 100)
                    if r.collidepoint(pygame.mouse.get_pos()):
                        if mouse_over != i:
                            MOUSE_SFX.play()
                        mouse_over = i
                        if left_click:
                            in_menu = False
                            current_text = i
                            percent = 0
                            scroll_y = 0
                            SELECT_SFX.play()
                        pygame.draw.rect(screen, c, r, 0, 8)
                    else:
                        pygame.draw.rect(screen, darken(c), r, 0, 8)
                    screen.blit(t := SMALL_FONT.render(texts[i][0], True, 'white'), (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))
            else:
                text = texts[current_text][1]

                screen.blit(FONT.render("You see:", True, '#ffff80'), (4, 4 - scroll_y))
                draw_text(text, screen, 2, TS + 2 - scroll_y, percent, 'black',  editing_word)
                draw_text(text, screen, 0, TS - scroll_y, percent, '#80ff80',  editing_word)

                screen.blit(FONT.render("You think this means:", True, '#ffff80'), (4, -scroll_y + 60 + 60 * len(text.splitlines()) + 4))
                shown_translation = "\n".join(" ".join([a for a in line.split(' ')]) for line in text.splitlines())
                tt = thought_translation(shown_translation)
                for i, line in enumerate(tt[:int(len(tt) * percent)].splitlines()):
                    screen.blit(FONT.render(line, True, 'black'), (6, -scroll_y + TS * 2 + 2 + TS * (len(text.splitlines()) + i) + 4))
                    screen.blit(FONT.render(line, True, '#80ff80'), (4, -scroll_y + TS * 2 + TS * (len(text.splitlines()) + i) + 4))

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
                    pygame.draw.aacircle(screen, 'gray', (WIDTH - 6, 6 + (HEIGHT - 12) * (scroll_y / 1250)), 4)

                if editing_word:
                    t = FONT.render(player_dictionary[editing_word] + ('|' if (pygame.time.get_ticks() // 500) & 1 else ' '), True, '#80ff80')
                    x, y = -4 + WIDTH // 2 - t.get_width() // 2, -4 + HEIGHT // 2 - t.get_height() // 2
                    pygame.draw.rect(screen, '#46555F', (x, y, t.get_width() + 8, t.get_height() + 8), 0, 8)
                    screen.blit(t, (x + 4, y + 4))

            if popup_time:
                popup_time = max(0, popup_time - delta / 3)

                t = FONT.render(popup, True, 'white')

                s = pygame.Surface((t.get_width() + 16, t.get_height() + 16), pygame.SRCALPHA)
                pygame.draw.rect(s, '#46555F', (0, 0, *s.get_size()), 0, 8)
                s.blit(t, (8, 8))
                s.set_alpha(255 * popup_time)

                screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT - s.get_height() - 8))

            pygame.display.flip()

        json.dump({"tabs": tabs, "dictionary": player_dictionary}, open("data/save.json", "w", encoding="utf-8"))

        return True

    if main_menu():
        game()

    pygame.quit()

main()