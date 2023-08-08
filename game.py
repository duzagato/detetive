import curses
import ctypes
import random
from time import sleep
import unidecode

global players, players_info, crime
players = []
players_info = {}
crime = []
w = ['Pá', 'Arma Química', 'Pé de Cabra', 'Espingarda', 'Faca', 'Tesoura', 'Veneno', 'Soco Inglês']
l = ['Restaurante', 'Prefeitura', 'Praça Pública', 'Hospital', 'Floricultura', 'Banco', 'Hotel', 'Mansão', 'Cemitério', 'Estação de Trem', 'Boate', 'Delegacia']
p = ['Mordomo', 'Advogado', 'Chefe de Cozinha', 'Coveiro', 'Sargento', 'Dançarina', 'Florista', 'Médica']
PERSONS = sorted(p)
WEAPONS = sorted(w)
LOCALS = sorted(l)

def str_to_function(str):
    str_sem_acentos = unidecode.unidecode(str.lower())

    replacer = {
        ' ': '_',
        '-': '_',
        '/': '_',
        '.': ''
    }

    for char, replace_char in replacer.items():
        str_func = str_sem_acentos.replace(char, replace_char)
    str_func = eval(str_func)

    return str_func

def get_nvda():
    nvda_dll = ctypes.CDLL("./nvda.dll")
    speak = nvda_dll.nvdaController_speakText
    nvda_silence = nvda_dll.nvdaController_cancelSpeech
    
    return nvda_silence, speak

def print_menu(stdscr, selected_row_idx, options, message):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    if message:
        title_x = width//2 - len(message)//2
        title_y = y = height//2 - len(options)//2 - 1
        stdscr.addstr(title_y, title_x, message)

    NVDA_SPEAK(options[selected_row_idx])

    for idx, option in enumerate(options):
        x = width//2 - len(option)//2
        y = height//2 - len(options)//2 + idx + 1
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.insstr(y, x, option)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, option)

    stdscr.refresh()

def newMenu(stdscr, options, message = False):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row_idx = 0
    if message:
        NVDA_SPEAK(message)
    print_menu(stdscr, current_row_idx, options, message)

    while True:
        key = stdscr.getch()
        stdscr.clear()
        NVDA_SILENCE()
        if key == curses.KEY_UP:
            if current_row_idx > 0:
                current_row_idx -= 1
            else:
                current_row_idx = len(options) - 1
        elif key == curses.KEY_DOWN: 
            if current_row_idx < len(options)-1:
                current_row_idx += 1
            else:
                current_row_idx = 0
        elif key == ord('\n'):
            return options[current_row_idx]
        elif key == ord('q'):
            break
        
        NVDA_SPEAK(options[current_row_idx])
        print_menu(stdscr, current_row_idx, options, message)

def get_max_window(stdscr):
    height, width = stdscr.getmaxyx()
    win = curses.newwin(height, width, 0, 0)
    win.clear()

    return win

def win_center_message(win, message, time_sleep = 5, y_ajust = 0):
    win.clear()
    height, width = win.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2 - y_ajust
    win.addstr(y, x, message)
    NVDA_SPEAK(message)
    win.refresh()
    sleep(time_sleep)

def center_message(stdscr, message, y_ajust = 0):
    height, width = stdscr.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2 - y_ajust
    stdscr.addstr(y, x, message)
    NVDA_SPEAK(message)
    stdscr.refresh()

def insert_user_input(win, message, only_num = False):
    curses.curs_set(1)
    height, width = win.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2
    win.addstr(y-1, x, message)
    win.refresh()
    curses.echo()
    if only_num == True:
        while True:
            win.clear()
            win.addstr(y-1, x, message)
            win.refresh()
            curses.echo()
            input_str = win.getstr(y, x, 20).decode('utf-8')
            if input_str.isdigit():  # Verifica se a entrada é composta apenas de dígitos
                break
            else:
                curses.beep()
                win_center_message(win, 'Digite apenas números')
    else:
        input_str = win.getstr(y, x, 20).decode('utf-8')
    curses.noecho()
    curses.curs_set(0)

    return input_str

def show_possibilities(stdscr):
    global players_info, players
    options = players.copy()
    options.append('Voltar')
    while True:
        pl = newMenu(stdscr, options, 'Selecione o jogador')
        stdscr.clear()
    
        if pl != 'Voltar':
            cards_type = newMenu(stdscr, ['persons', 'weapons', 'locals', 'cartas mostradas'], 'Selecione o tipo de carta')
            stdscr.clear()
            if cards_type == 'cartas mostradas':
                ctp = newMenu(stdscr, ['persons', 'weapons', 'locals'], 'Selecione o itpo')
                showed = players_info[pl]['shown_cards'][ctp]
                if len(showed) > 0:
                    cs = newMenu(stdscr, showed, 'Cartas Mostradas')
            else:
                cards = newMenu(stdscr, players_info[pl]['possibilities'][cards_type], f'Possibilidades de {pl}')
                stdscr.clear()
        else:
            break

def get_cards(pls):
    global players_info, crime
    persons = PERSONS.copy()
    locals = LOCALS.copy()
    weapons = WEAPONS.copy()
    nr = random.randint(0, len(persons) - 1)
    crime.append(persons[nr])
    del persons[nr]
    nr = random.randint(0, len(locals) - 1)
    crime.append(locals[nr])
    del locals[nr]
    nr = random.randint(0, len(weapons) - 1)
    crime.append(weapons[nr])
    del weapons[nr]
    all_cards = locals + persons + weapons
    random.shuffle(all_cards)
    ended = False
    while True:
        for pl in pls:
            if len(all_cards) > 0:
                nr = random.randint(0, len(all_cards) - 1)
                players_info[pl]['cards'].append(all_cards[nr])
                del all_cards[nr]
            else:
                ended = True
        if ended == True:
            break

    for pl in players:
        players_info[pl]['shown_cards'] = {}
        players_info[pl]['shown_cards']['persons'] = []
        players_info[pl]['shown_cards']['weapons'] = []
        players_info[pl]['shown_cards']['locals'] = []
        players_info[pl]['possibilities'] = {}
        players_info[pl]['possibilities']['persons'] = []
        players_info[pl]['possibilities']['weapons'] = []
        players_info[pl]['possibilities']['locals'] = []
        players_info[pl]['possibilities']['persons'] = [card for card in PERSONS if card not in players_info[pl]['cards']]
        players_info[pl]['possibilities']['weapons'] = [card for card in WEAPONS if card not in players_info[pl]['cards']]
        players_info[pl]['possibilities']['locals'] = [card for card in LOCALS if card not in players_info[pl]['cards']]
    
def list_cards(stdscr, pl):
    global players_info
    cards = players_info[pl]['cards']
    options = newMenu(stdscr, cards, f'Cartas de {pl}. Aperte enter para voltar')

    return False

def list_compare (l1, l2):
    return set(l1) == set(l2)

def set_showed_cards(pl, card):
    global players_info

    if card in PERSONS:
        players_info[pl]['shown_cards']['persons'].append(card)
    elif card in WEAPONS:
        players_info[pl]['shown_cards']['weapons'].append(card)
    elif card in LOCALS:
        players_info[pl]['shown_cards']['locals'].append(card)

def possibilities():
    global players, players_info
    for pl in players:
        if players_info[pl]['type'] == 'c':
            poss_func = str_to_function('set_'+players_info[pl]['nivel']+'_possibilities')
            poss_func(pl)

def set_facil_1_possibilities(pl):
    global players, players_info
    for p in players:
        if p != pl:
            refresh_poss(p, pl, 3)

def set_facil_2_possibilities(pl):
    global players, players_info
    for p in players:
        if p != pl:
            refresh_poss(p, pl, 2)

def set_medio_1_possibilities(pl):
    global players, players_info
    for p in players:
        if p != pl:
            refresh_poss(p, pl, 0)

def set_medio_2_possibilities(pl):
    global players, players_info
    for p in players:
        if p != pl:
            refresh_poss(p, pl, 0)

def set_dificil_1_possibilities(pl):
    global players, players_info
    for p in players:
        if p != pl:
            refresh_poss(p, pl, 0)

def set_dificil_2_possibilities(pl):
    global players, players_info
    for p in players:
        if p != pl:
            refresh_poss(p, pl, 0)

def refresh_poss(p, pl, filter):
    global players, players_info
    p_persons = players_info[p]['shown_cards']['persons']
    pl_persons = players_info[pl]['possibilities']['persons']
    p_weapons = players_info[p]['shown_cards']['weapons']
    pl_weapons = players_info[pl]['possibilities']['weapons']
    p_locals = players_info[p]['shown_cards']['locals']
    pl_locals = players_info[pl]['possibilities']['locals']
    for per in p_persons:
        num_rand = random.randint(1, 10)
        if per in pl_persons and num_rand > filter:
            players_info[pl]['possibilities']['persons'].remove(per)
            
    for w in p_weapons:
        num_rand = random.randint(0, 10)
        if w in pl_weapons and num_rand > filter:
            players_info[pl]['possibilities']['weapons'].remove(w)
                
    for l in p_locals:
        num_rand = random.randint(0, 10)
        if l in pl_locals and num_rand > filter:
            players_info[pl]['possibilities']['locals'].remove(l)

def get_option(pl):
    global players_info
    level = players_info[pl]['nivel']
    qtd_poss = len(players_info[pl]['possibilities']['persons']) + len(players_info[pl]['possibilities']['weapons']) + len(players_info[pl]['possibilities']['locals'])
    if level == 'Fácil_1' or level == 'Médio_1' or level == 'Dificil_1':
        if qtd_poss > 3:
            return 'Palpitar'
        else:
            return 'Acusar'
    elif level == 'Fácil_2' or level == 'Dificil_2':
        if qtd_poss > 4:
            return 'Palpitar'
        else:
            return 'Acusar'
    else:
        if qtd_poss > 5:
            return 'Palpitar'
        else:
            return 'Acusar'
        
def get_accusation(pl):
    global players_info
    if len(players_info[pl]['possibilities']['persons']) == 1:
        person = players_info[pl]['possibilities']['persons'][0]
    else:
        num_rand = random.randint(0, len(players_info[pl]['possibilities']['persons']) - 1)
        person = players_info[pl]['possibilities']['persons'][num_rand]
    
    if len(players_info[pl]['possibilities']['weapons']) == 1:
        weapon = players_info[pl]['possibilities']['weapons'][0]
    else:
        num_rand = random.randint(0, len(players_info[pl]['possibilities']['weapons']) - 1)
        weapon = players_info[pl]['possibilities']['weapons'][num_rand]

    if len(players_info[pl]['possibilities']['locals']) == 1:
        local = players_info[pl]['possibilities']['locals'][0]
    else:
        num_rand = random.randint(0, len(players_info[pl]['possibilities']['locals']) - 1)
        local = players_info[pl]['possibilities']['locals'][num_rand]

    return person, weapon, local

def get_palp(pl):
    global players_info
    num_rand = random.randint(0, len(players_info[pl]['possibilities']['persons']) - 1)
    person = players_info[pl]['possibilities']['persons'][num_rand]
    num_rand = random.randint(0, len(players_info[pl]['possibilities']['weapons']) - 1)
    weapon = players_info[pl]['possibilities']['weapons'][num_rand]
    num_rand = random.randint(0, len(players_info[pl]['possibilities']['locals']) - 1)
    local = players_info[pl]['possibilities']['locals'][num_rand]

    return person, weapon, local
    

def game_start(game_win, stdscr):
    global players, players_info, crime
    game_end = False
    game_win.clear()
    win_center_message(game_win, 'O jogo vai começar')
    while True:
        if game_end == True:
            break
        game_win.clear()
        for pl in players:
            if game_end == True:
                break
            while True:
                game_win.clear()
                if game_end == True:
                    break
                player_type = players_info[pl]['type']
                if player_type == 'h':
                    option = newMenu(stdscr, ['Palpitar', 'Acusar', 'Cartas','Sair'], f'Turno de {pl}')
                else:
                    option = get_option(pl)
                if option == 'Palpitar':
                    if player_type == 'h':
                        person = newMenu(stdscr, PERSONS, 'Escolha a pessoa que você suspeita.')
                        weapon = newMenu(stdscr, WEAPONS, 'Escolha a arma do crime.')
                        local = newMenu(stdscr, LOCALS, 'Escolha o local do assassinato.')
                    else:
                        person, weapon, local = get_palp(pl)
                    cards_list = [person, weapon, local]
                    win_center_message(game_win, f'O palpite de {pl} é', 3)
                    win_center_message(game_win, f'Assassino: {person}', 3)
                    win_center_message(game_win, f'Arma: {weapon}', 3)
                    win_center_message(game_win, f'Local: {local}', 3)
                    summary = []
                    summary.append(f'Palpite do Assassino: {person}')
                    summary.append(f'Palpite da Arma:: {weapon}')
                    summary.append(f'Palpite do Local: {local}')
                    for p in players:
                        if p != pl:
                            cards = [card for card in cards_list if card in players_info[p]['cards']]
                            if len(cards) == 1:
                                win_center_message(game_win, f'{p} tem a carta {cards[0]}')
                                set_showed_cards(p, cards[0])
                                summary.append(f'{p} tem a carta {cards[0]}')
                            elif len(cards) > 1:
                                if players_info[p]['type'] == 'h':
                                    option = newMenu(stdscr, cards, f'{p}, escolha a carta que você deseja mostrar')
                                else:
                                    num_rand = random.randint(0, len(cards) - 1)
                                    option = cards[num_rand]
                                win_center_message(game_win, f'{p} tem a carta {option}')
                                set_showed_cards(p, option)
                                summary.append(f'{p} tem a carta {option}')
                            else:
                                win_center_message(stdscr, f'{p} não mostrou nenhuma carta.')
                                summary.append(f'{p} não mostrou nenhuma carta.')
                    possibilities()
                    sm = newMenu(stdscr, summary,'Resumo da Rodada (Aperte Enter para continuar)')
                    stdscr.clear()
                    break
                elif option == 'Acusar':
                    if player_type == 'h':
                        person = newMenu(stdscr, PERSONS, 'Quem é o assassino?')
                        weapon = newMenu(stdscr, WEAPONS, 'Qual foi a arma do crime?')
                        local = newMenu(stdscr, LOCALS, 'Onde ocorreu o assassinato?')
                    else:
                        person, weapon, local = get_accusation(pl)
                    win_center_message(game_win, f'{pl} deseja fazer uma acusação', 3)
                    win_center_message(game_win, f'Assassino: {person}', 3)
                    win_center_message(game_win, f'Arma: {weapon}', 3)
                    win_center_message(game_win, f'Local: {local}', 3)
                    cards_list = [person, weapon, local]
                    if list_compare(cards_list, crime):
                        win_center_message(game_win, f'{pl} ganhou o jogo!')
                        raise StopIteration
                    else:
                        win_center_message(game_win, f'{pl} errou! Está eliminado do jogo')
                        players.remove(pl)
                        if len(players) > 1:
                            if player_type == 'h':
                                option = newMenu(stdscr, ['Ver o jogo', 'Sair'], 'Você perdeu! O que deseja fazer?')
                                if option == 'Sair':
                                    raise StopAsyncIteration
                            else:
                                sc = newMenu(stdscr, players_info[pl]['cards'], f'Todas as cartas de {pl}. (Aperte enter para continuar).')
                        else:
                            win_center_message(game_win, f'{players[0]} ganhou o jogo!')
                            game_end = True
                    break
                elif option == 'Cartas':
                    list_cards(stdscr, pl)
                elif option == 'Sair':
                    opt = newMenu(stdscr, ['Sim', 'Não'], 'Tem certeza que você deseja sair?')
                    if opt == 'Sim':
                        raise StopIteration

def main(stdscr):
    global players, players_info
    NVDA_SILENCE()
    curses.curs_set(0)
    message = 'Bem-Vindo ao Detetive'
    center_message(stdscr, message)
    NVDA_SPEAK(message)
    sleep(2)
    stdscr.clear()
    option = newMenu(stdscr, ['Novo Jogo', 'Sair'], 'Menu Principal')
    if option == 'Novo Jogo':
        while True:
            stdscr.clear()
            options = ['3 Jogadores', '4 Jogadores', '5 Jogadores', '6 Jogadores']
            option = newMenu(stdscr, options, 'Selecione o número de jogadores')
            num = option.split(' ')[0]
            persons = ['Senhor Marinho', 'Dona Branca', 'Senhorita Rosa', 'Dona Violeta', 'James', 'Tony Gourmet', 'Sérgio Soturno', 'Senhor Bigode']
            stdscr.clear()
            person = newMenu(stdscr, persons, 'Escolha seu personagem')
            players.append(person)
            players_info[person] = {}
            players_info[person]['type'] = 'h'
            players_info[person]['cards'] = []
            persons.remove(person)
            for i in range(2, int(num)+1):
                n = i - 1
                person = newMenu(stdscr, persons, f'Escolha o personagem do Computador {n}')
                level = newMenu(stdscr, ['Fácil', 'Médio', 'Dificil'], 'Escolha o nível')
                players.append(person)
                players_info[person] = {}
                players_info[person]['type'] = 'c'
                num_rand = random.randint(1, 2)
                players_info[person]['nivel'] = f'{level}_{num_rand}'
                players_info[person]['cards'] = []
                persons.remove(person)
            game_win = get_max_window(stdscr)
            random.shuffle(players)
            pls = players.copy()
            get_cards(pls)
            game_start(game_win, stdscr)


NVDA_SILENCE, NVDA_SPEAK = get_nvda()
curses.wrapper(main)