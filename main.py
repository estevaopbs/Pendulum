import pygame
from pygame.locals import *
import pygame_menu
import numpy as np
from pygame_menu import events
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from math import floor, ceil
import multiprocessing


def thread_export_graph():
    global pause
    pause = True
    work = multiprocessing.Process(target=export_graph)
    work.start()


def export_graph():
    t0, tf = interval.get_value()
    t0_index = floor((t0 + 20) * 60)
    tf_index = ceil((tf + 20) * 60)
    time_data = np.zeros([(tf_index - t0_index)])
    for n in range(len(time_data)):
        time_data[n] = n * 1/60
    if graph_selector.get_value()[1] == 0:
        fig, ax = plt.subplots(num='Energias')
        ax.plot(time_data, T_energies_ex[t0_index:tf_index], 'r-', label='Energia total')
        ax.plot(time_data, k_energies_ex[t0_index:tf_index], 'g-', label='Energia cinética')
        ax.plot(time_data, p_energies_ex[t0_index:tf_index], 'b-', label='Energia Potencial')
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Energia (J)')
        plt.legend()
        plt.show()
    elif graph_selector.get_value()[1] == 2:
        fig, ax = plt.subplots(num='Posições')
        ax.plot(time_data, x_positions_ex[t0_index:tf_index], 'r-', label='Posição em x')
        ax.plot(time_data, y_positions_ex[t0_index:tf_index], 'g-', label='Posição em y')
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Posição (m)')
        plt.legend()
        plt.show()
    elif graph_selector.get_value()[1] == 1:
        fig, ax = plt.subplots(num='Ângulo')
        ax.plot(time_data, angles[t0_index:tf_index], 'r-')
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Ângulo (rad)')
        plt.show()


def create_menu(w, h):
    menu_theme = pygame_menu.Theme(background_color=(0, 0, 0, 100), fps=60)
    menu = pygame_menu.Menu('Oscilador harmônico', w, h, theme=menu_theme)
    lenght = menu.add.text_input('Comprimento (m): ', default='10', align=pygame_menu.locals.ALIGN_LEFT, 
                                 onchange=change_lenght, valid_chars=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                                                                      '.'])
    mass = menu.add.text_input('Massa (kg): ', default='1', align=pygame_menu.locals.ALIGN_LEFT, onchange=update_mass, 
                               valid_chars=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'])
    gravity = menu.add.text_input('Aceleração gravitacional (m/s²): ', default='10', 
                                  align=pygame_menu.locals.ALIGN_LEFT,
                                  onchange=update_gravity, valid_chars=['0', '1', '2', '3', '4', '5', '6', '7', '8', 
                                                                        '9', '.'])
    resistive_force = menu.add.text_input('Fator de arraste: ', default='0', align=pygame_menu.locals.ALIGN_LEFT, 
                                          onchange=update_resistive_force, valid_chars=['0', '1', '2', '3', '4', '5', 
                                                                                        '6', '7', '8', '9', '.'])
    graph_selector = menu.add.selector(title='Gráfico: ', items=[('Energias', 0), ('Ângulo', 1), ('Posições', 2)], 
                                       default=0, align=pygame_menu.locals.ALIGN_LEFT)
    menu.add.button('Exportar gráfico', thread_export_graph, align=pygame_menu.locals.ALIGN_LEFT)
    interval = menu.add.range_slider('Intervalo', (-20, 0), (-20, 0), 0.1, align=pygame_menu.locals.ALIGN_LEFT,
                                     value_format= lambda t: str(round(t, 1)) + ' s')
    menu.add.button('Sair', pygame_menu.events.EXIT, align=pygame_menu.locals.ALIGN_LEFT)
    return menu, lenght, mass, gravity, resistive_force, graph_selector, interval


def update_gravity(f):
    global gravity_value
    global k_energies, p_energies, T_energies, x_positions, y_positions
    global redimension
    global old_gravity_value
    global last_pressed_cos, last_pressed_sin
    if gravity_value != 0:
        old_gravity_value = gravity_value
    global gravity
    if not f.replace('.', '', 1).isdigit():
        gravity_value = 0
    elif float(f) != 0:
        gravity_value = float(f)
        if old_gravity_value > gravity_value:
            last_pressed_sin, last_pressed_cos = 1, 0
        if redimension:
            for n in range(1200):
                k_energies[n] = old_gravity_value/gravity_value * k_energies[n]
                p_energies[n] = old_gravity_value/gravity_value * p_energies[n]
                T_energies[n] = old_gravity_value/gravity_value * T_energies[n]


def update_mass(M):
    global mass_value
    old_mass_value = mass_value
    try:
        mass_value = float(M)
        if redimension:
            for n in range(1200):
                k_energies[n] = old_mass_value/mass_value * k_energies[n]
                p_energies[n] = old_mass_value/mass_value * p_energies[n]
                T_energies[n] = old_mass_value/mass_value * T_energies[n]
    except:
        mass_value = 0


def update_resistive_force(a):
    global resistive_force_factor
    signal = ''
    if len(a) > 0:
        while a[0] == '0' and a != '0':
            a = a[1:]
    if len(a) > 0:
        if a[0] == '+' or a[0] == '-':
            signal = a[0]
            a = a[1:]
        if len(a) > 0:
            while a[0] == '0' and a != '0':
                a = a[1:]
    try:
        resistive_force_factor = float(signal + a)
    except:
        resistive_force_factor = 0
    if not a.replace('.', '', 1).isdigit():
        resistive_force_factor = 0


def change_lenght(l):
    global cable_lenght
    global update, pause
    global V0x, V0y, Vx, Vy
    global k_energies, p_energies, T_energies, x_positions, y_positions
    global last_pressed_cos, last_pressed_sin
    old_cable_lenght = cable_lenght
    try:
        if float(l) != 0:
            cable_lenght = float(l)
            sin_theta_ = (weight_pos[0]) / np.sqrt(weight_pos[0] ** 2 + weight_pos[1] **2)
            cos_theta_ = (weight_pos[1]) / np.sqrt(weight_pos[0] ** 2 + weight_pos[1] **2)
            weight_pos[0] = cable_lenght * sin_theta_
            weight_pos[1] = cable_lenght * cos_theta_
            if redimension:
                for n in range(1200):
                    k_energies[n] = old_cable_lenght/cable_lenght * k_energies[n]
                    p_energies[n] = old_cable_lenght/cable_lenght * p_energies[n]
                    T_energies[n] = old_cable_lenght/cable_lenght * T_energies[n]
                    x_positions[n] = old_cable_lenght/cable_lenght * x_positions[n]
                    y_positions[n] = old_cable_lenght/cable_lenght * y_positions[n]
            if cable_lenght < old_cable_lenght:
                last_pressed_sin, last_pressed_cos = 1, 0
    except:
        pass
    update = True


def roll_positions(array):
    for n, position in enumerate(array[1:]):
        array[n] = position


def clear():
    global k_energies, p_energies, T_energies, x_positions, y_positions, angles, k_energies_ex, p_energies_ex, T_energies_ex, x_positions_ex, y_positions_ex
    k_energies = np.zeros(1200)
    p_energies = np.zeros(1200)
    T_energies = np.zeros(1200)
    x_positions = np.zeros(1200)
    y_positions = np.zeros(1200)
    angles = np.zeros(1200)
    k_energies_ex = np.zeros(1200)
    p_energies_ex = np.zeros(1200)
    T_energies_ex = np.zeros(1200)
    x_positions_ex = np.zeros(1200)
    y_positions_ex = np.zeros(1200)



def draw_E_graph():
    E_graph_surf.fill((0, 0, 0))
    for n, energy in enumerate(reversed(T_energies)):
        pygame.draw.circle(E_graph_surf, (255, 0, 0), (1219 - n, energy + 301), 2)
    for n, energy in enumerate(reversed(p_energies)):
        pygame.draw.circle(E_graph_surf, (0, 0, 255), (1219 - n, energy + 301), 2)
    for n, energy in enumerate(reversed(k_energies)):
        pygame.draw.circle(E_graph_surf, (0, 255, 0), (1219 - n, energy + 301), 2)
    pygame.draw.rect(E_graph_surf, (0, 0, 0), ((15, 307), (1210, 50)))
    pygame.draw.line(E_graph_surf, (255, 255, 255), (15, 304), (1224, 304), 4)
    pygame.draw.line(E_graph_surf, (255, 255, 255), (15, 0), (15, 306), 4)
    step = max_energy/(scale_lenght)
    for n, energy in enumerate(np.arange(0, max_energy + step, step)):
        scale_pos = 304 - (energy/max_energy) * 290 - 15
        energy_text = str(energy)
        if len(energy_text) > 5:
            energy_text = format(energy, '.0e')
        E_graph_surf.blit(font.render(energy_text, True, (255, 255, 255)), (1215 + 20, scale_pos + 4))
        pygame.draw.line(E_graph_surf, (255, 255, 255), (1204 + 20, scale_pos + 11), (1208 + 20, scale_pos + 11), 2)
    for n, time in enumerate(reversed(range(0, -21,  -1))):
        time_pos = n * 60
        time_text = str(time)
        E_graph_surf.blit(font.render(time_text, True, (255, 255, 255)), (time_pos + 14 - 5*(len(time_text) - 1), 313))
        pygame.draw.line(E_graph_surf, (255, 255, 255), (time_pos + 18, 305), (time_pos + 18, 310), 2)
    pygame.draw.line(E_graph_surf, (255, 255, 255), (1202 + 20, 0), (1202 + 20, 304), 4)
    pygame.draw.circle(E_graph_surf, (255, 0, 0), (17 + 20, 18), 4)
    pygame.draw.circle(E_graph_surf, (0, 255, 0), (17 + 20, 38), 4)
    pygame.draw.circle(E_graph_surf, (0, 0, 255), (17 + 20, 58), 4)
    E_graph_surf.blit(font.render('Energia total', True, (255, 255, 255)), (30 + 20, 10))
    E_graph_surf.blit(font.render('Energia cinética', True, (255, 255, 255)), (30 + 20, 30))
    E_graph_surf.blit(font.render('Energia potencial', True, (255, 255, 255)), (30 + 20, 50))
    E_graph_surf.blit(font.render('Tempo (s)', True, (255, 255, 255)), (580, 330))
    E_graph_surf.blit(font.render('Energia (J)', True, (255, 255, 255)), (1300, 148))
    screen.blit(E_graph_surf, (500, 660))


def draw_P_graph():
    P_graph_surf.fill((0, 0, 0))
    for n, position in enumerate(reversed(x_positions)):
        pygame.draw.circle(P_graph_surf, (255, 0, 0), (1219 - n, position + 156), 2)
    for n, position in enumerate(reversed(y_positions)):
        pygame.draw.circle(P_graph_surf, (0, 255, 0), (1219 - n, position + 156), 2)
    pygame.draw.rect(P_graph_surf, (0, 0, 0), ((15, 307), (1210, 50)))
    pygame.draw.line(P_graph_surf, (255, 255, 255), (15, 304), (1224, 304), 4)
    pygame.draw.line(P_graph_surf, (255, 255, 255), (15, 0), (15, 306), 4)
    pygame.draw.line(P_graph_surf, (255, 255, 255), (1202 + 20, 0), (1202 + 20, 304), 4)
    step = 2 * cable_lenght/(scale_lenght)
    for n, energy in enumerate(np.arange(-cable_lenght, cable_lenght + step, step)):
        scale_pos = 156 - (energy/cable_lenght) * 145 - 12
        energy_text = str(energy)
        if len(energy_text) > 5:
            energy_text = format(energy, '.0e')
        P_graph_surf.blit(font.render(energy_text, True, (255, 255, 255)), (1215 + 20, scale_pos + 4))
        pygame.draw.line(P_graph_surf, (255, 255, 255), (1204 + 20, scale_pos + 11), (1208 + 20, scale_pos + 11), 2)
    for n, time in enumerate(reversed(range(0, -21,  -1))):
        time_pos = n * 60
        time_text = str(time)
        P_graph_surf.blit(font.render(time_text, True, (255, 255, 255)), (time_pos + 14 - 5*(len(time_text) - 1), 313))
        pygame.draw.line(P_graph_surf, (255, 255, 255), (time_pos + 18, 305), (time_pos + 18, 310), 2)
    P_graph_surf.blit(font.render('Tempo (s)', True, (255, 255, 255)), (580, 330))
    P_graph_surf.blit(font.render('Posição (m)', True, (255, 255, 255)), (1300, 148))
    pygame.draw.circle(P_graph_surf, (255, 0, 0), (17 + 20, 18), 4)
    pygame.draw.circle(P_graph_surf, (0, 255, 0), (17 + 20, 38), 4)
    P_graph_surf.blit(font.render('Posição em x', True, (255, 255, 255)), (30 + 20, 10))
    P_graph_surf.blit(font.render('Posição em y', True, (255, 255, 255)), (30 + 20, 30))
    screen.blit(P_graph_surf, (500, 660))


def draw_angles_graph():
    angles_graph_surf.fill((0, 0, 0))
    for n, angle in enumerate(reversed(angles)):
        pygame.draw.circle(angles_graph_surf, (255, 0, 0), (1219 - n, -145 * angle/(np.pi/2) + 156), 2)
    pygame.draw.rect(angles_graph_surf, (0, 0, 0), ((15, 307), (1210, 50)))
    pygame.draw.line(angles_graph_surf, (255, 255, 255), (15, 304), (1224, 304), 4)
    pygame.draw.line(angles_graph_surf, (255, 255, 255), (15, 0), (15, 306), 4)
    pygame.draw.line(angles_graph_surf, (255, 255, 255), (1202 + 20, 0), (1202 + 20, 304), 4)
    step = np.pi/(scale_lenght)
    for n, angle in enumerate(np.arange(-np.pi/2, np.pi/2 + step, step)):
        scale_pos = 156 - (2*angle/np.pi) * 145 - 12
        angle_text = str(angle)
        angle_text = format(angle/(np.pi/2), '.1f')
        angle_text += ' \N{GREEK SMALL LETTER PI}'
        angles_graph_surf.blit(font.render(angle_text, True, (255, 255, 255)), (1215 + 20, scale_pos + 4))
        pygame.draw.line(angles_graph_surf, (255, 255, 255), (1204 + 20, scale_pos + 11), (1208 + 20, scale_pos + 11), 2)
    for n, time in enumerate(reversed(range(0, -21,  -1))):
        time_pos = n * 60
        time_text = str(time)
        angles_graph_surf.blit(font.render(time_text, True, (255, 255, 255)), (time_pos + 14 - 5*(len(time_text) - 1), 313))
        pygame.draw.line(angles_graph_surf, (255, 255, 255), (time_pos + 18, 305), (time_pos + 18, 310), 2)
    angles_graph_surf.blit(font.render('Tempo (s)', True, (255, 255, 255)), (580, 330))
    angles_graph_surf.blit(font.render('Ângulo (rad)', True, (255, 255, 255)), (1300, 148))
    screen.blit(angles_graph_surf, (500, 660))


if __name__ == '__main__':
    w, h = 1920, 1016 
    pygame.init()
    pygame.display.set_caption('Oscilador harmônico')
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((w, h))
    background_surf = pygame.Surface((w,h))
    menu_surf = pygame.surface.Surface((w, h))
    pendulum_surf = pygame.surface.Surface((1199, 600))
    pendulum_surf.set_colorkey((0, 0, 0))
    E_graph_surf = pygame.surface.Surface((1400, 350))
    E_graph_surf.fill((255, 255, 255))
    P_graph_surf = pygame.surface.Surface((1400, 350))
    P_graph_surf.fill((255, 255, 255))
    angles_graph_surf = pygame.surface.Surface((1400, 350))
    angles_graph_surf.fill((255, 255, 255))
    menu, lenght, mass, gravity, resistive_force, graph_selector, interval = create_menu(w, h)
    weight_pos = np.array([0, float(lenght.get_value())])
    weight_vel = np.array([0, 0])
    cable_lenght = float(lenght.get_value())
    update = False
    sin_theta = 0
    cos_theta = 1
    Vx = 0
    Vy = 0
    resistive_force_factor = 0
    k_energies = np.zeros(1200)
    p_energies = np.zeros(1200)
    T_energies = np.zeros(1200)
    x_positions = np.zeros(1200)
    y_positions = np.zeros(1200)
    angles = np.zeros(1200)
    k_energies_ex = np.zeros(1200)
    p_energies_ex = np.zeros(1200)
    T_energies_ex = np.zeros(1200)
    x_positions_ex = np.zeros(1200)
    y_positions_ex = np.zeros(1200)
    mass_value = float(mass.get_value())
    gravity_value = float(gravity.get_value())
    weight_diameter = 50
    delta_t = 1/60
    scale_lenght = 10
    font = pygame.font.SysFont(None, 25)
    r_font = pygame.font.SysFont(None, 60)
    pause = False
    redimension = False
    old_gravity_value = 10
    last_pressed_sin = 0
    last_pressed_cos = 1
    while True:
        clock.tick(60)
        V0x, V0y = Vx, Vy
        events = pygame.event.get()
        menu.update(events)
        if update:
            screen.blit(menu_surf, (0, 0))
            screen.blit(pendulum_surf, (600, 80))
            if  pause:
                pygame.draw.rect(screen, (255, 0, 0), ((1820, 50), (10, 30)))
                pygame.draw.rect(screen, (255, 0, 0), ((1838, 50), (10, 30)))
            if redimension:
                screen.blit(r_font.render('R', True, (255, 255, 255)), (1870, 47))
            if graph_selector.get_value()[1] == 0:
                draw_E_graph()
            elif graph_selector.get_value()[1] == 1:
                draw_angles_graph()
            elif graph_selector.get_value()[1] == 2:
                draw_P_graph()
            pygame.display.update()
            update = False
            continue
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_p:
                    pause = not pause
                if event.key == K_r:
                    redimension = not redimension
                if event.key == K_c:
                    clear()
        menu.draw(menu_surf)
        if mass_value == 0 or not lenght.get_value().replace('.', '', 1).isdigit() or cable_lenght == 0 or gravity_value == 0 or pause or cable_lenght == 0:
            screen.blit(menu_surf, (0, 0))
            screen.blit(pendulum_surf, (600, 80))
            if  pause:
                pygame.draw.rect(screen, (255, 0, 0), ((1820, 50), (10, 30)))
                pygame.draw.rect(screen, (255, 0, 0), ((1838, 50), (10, 30)))
            if redimension:
                screen.blit(r_font.render('R', True, (255, 255, 255)), (1870, 47))
            if graph_selector.get_value()[1] == 0:
                draw_E_graph()
            elif graph_selector.get_value()[1] == 1:
                draw_angles_graph()
            elif graph_selector.get_value()[1] == 2:
                draw_P_graph()
            pygame.display.update()
            continue
        elif pygame.mouse.get_pressed()[0] == True:
            mouse_pos = pygame.mouse.get_pos()
            mouse_to_origin = np.array([mouse_pos[0] - 1200, mouse_pos[1] - 105])
            distance = np.sqrt((mouse_to_origin[0] + (500 * sin_theta)) ** 2 + ((mouse_to_origin[1] - (500* cos_theta)) ** 2))
            if distance <= weight_diameter or pressing:
                Vx, Vy, V0y, V0x = 0, 0, 0, 0
                pressing = True
                mouse_lenght = np.sqrt((mouse_pos[0] - 1200) ** 2 + ((mouse_pos[1] - 105) ** 2))
                if mouse_lenght == 0:
                    mouse_lenght = 1
                    mouse_to_origin = (600, 0)
                sin_theta = -(mouse_to_origin[0])/mouse_lenght
                cos_theta = (mouse_to_origin[1])/mouse_lenght
                weight_pos[0] = cable_lenght * sin_theta
                weight_pos[1] = cable_lenght * cos_theta
                last_pressed_cos = cos_theta
                last_pressed_sin = sin_theta
            else:
                pressing = False
        else:
            pressing = False
        if weight_pos[1] < cable_lenght * last_pressed_cos:
            Vx, Vy, V0x, V0y = 0, 0, 0, 0
            weight_pos = np.array([cable_lenght * abs(last_pressed_sin) * sin_theta/abs(sin_theta),
                                   cable_lenght * last_pressed_cos])
        if weight_pos[1] < 0:
            weight_pos[1] = 0
            Vx, Vy, V0x, V0y = 0, 0, 0, 0
            if weight_pos[0] > 0:
                weight_pos[0] = cable_lenght
            else:
                weight_pos[0] = - cable_lenght
        try:
            mass_value = float(mass.get_value())
        except:
            mass_value = 0
        screen.blit(menu_surf, (0, 0))
        roll_positions(p_energies)
        roll_positions(k_energies)
        roll_positions(T_energies)
        roll_positions(x_positions)
        roll_positions(y_positions)
        roll_positions(angles)
        roll_positions(p_energies_ex)
        roll_positions(k_energies_ex)
        roll_positions(T_energies_ex)
        roll_positions(x_positions_ex)
        roll_positions(y_positions_ex)
        pendulum_surf.fill((0, 0, 0))
        sin_theta = (weight_pos[0]) / cable_lenght
        cos_theta = (weight_pos[1]) / cable_lenght
        angles[-1] = -np.arcsin(sin_theta)
        pygame.draw.circle(pendulum_surf, (255, 255, 255),  (600, 0), 50, 10)
        pygame.draw.circle(pendulum_surf, (255, 255, 255), (600, 25), 9)
        pygame.draw.line(pendulum_surf, (255, 255, 255), (599, 25), (599 - 500 * sin_theta, 25 + 500 * cos_theta), 4)
        pygame.draw.circle(pendulum_surf, (80, 150, 240), (600 - 500 * sin_theta, 25 + 500 * cos_theta), weight_diameter)
        screen.blit(pendulum_surf, (600, 80))
        x_positions[-1] = 145 * weight_pos[0] / cable_lenght
        y_positions[-1] = -145 * (cable_lenght - weight_pos[1]) / cable_lenght
        max_energy = mass_value * gravity_value * cable_lenght
        k_energy = -((mass_value * (Vx**2 + Vy**2)/2)/(max_energy)) * 290
        k_energies[-1] = k_energy
        p_energy = - 290 + (mass_value * gravity_value * cos_theta*cable_lenght)/(max_energy) * 290
        p_energies[-1] = p_energy
        T_energy = k_energy + p_energy
        T_energies[-1] = T_energy
        p_energies_ex[-1] =  - mass_value * gravity_value * cos_theta * cable_lenght + max_energy
        k_energies_ex[-1] = mass_value * (Vx**2 + Vy**2)/2
        T_energies_ex[-1] = p_energies_ex[-1] + k_energies_ex[-1]
        x_positions_ex[-1] = -weight_pos[0]
        y_positions_ex[-1] = -weight_pos[1] + cable_lenght
        if graph_selector.get_value()[1] == 0:
            draw_E_graph()
        elif graph_selector.get_value()[1] == 1:
            draw_angles_graph()
        elif graph_selector.get_value()[1] == 2:
            draw_P_graph()
        if redimension:
            screen.blit(r_font.render('R', True, (255, 255, 255)), (1870, 47))
        pygame.display.update()
        T = ((mass_value * (Vx ** 2 + Vy ** 2))/(cable_lenght)) + (mass_value * gravity_value * cos_theta)
        Fx = - T * sin_theta - resistive_force_factor *(Vx)
        Fy = - T * cos_theta + mass_value * gravity_value - resistive_force_factor*(Vy)
        ax = Fx/mass_value
        ay = Fy/mass_value
        Vx_2 = (ax * (delta_t/2)) + Vx
        Vy_2 = (ay * (delta_t/2)) + Vy
        x_2 = weight_pos[0] + Vx * (delta_t/2)
        y_2 = weight_pos[1] + Vy * (delta_t/2)
        sin_theta_2 = (x_2) / cable_lenght
        cos_theta_2 = (y_2) / cable_lenght
        T_2 = ((mass_value * (Vx_2 ** 2 + Vy_2 ** 2))/(cable_lenght)) + (mass_value * gravity_value * cos_theta_2)
        Fx_2 = - T_2 * sin_theta_2 - resistive_force_factor*(Vx_2)
        Fy_2 = - T_2 * cos_theta_2 + mass_value * gravity_value - resistive_force_factor*(Vy_2)
        ax_2 = Fx_2/mass_value
        ay_2 = Fy_2/mass_value
        Vx = (ax_2 * (delta_t)) + V0x
        Vy = (ay_2 * (delta_t)) + V0y
        x = weight_pos[0] + Vx_2 * (delta_t)
        y = weight_pos[1] + Vy_2 * (delta_t)
        weight_pos = np.array([x, y])
