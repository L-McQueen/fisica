"""
Generador de Gráficas Detalladas del Comportamiento del Carrito en Matplotlib.
Secuencia Exacta Actualizada:
1. Transferencia / Acople de Maleta
2. Bajada 2 (45°)
3. Curva 1 (90° peraltada hacia +Y)
4. Subida (30° hacia +Y) y Cresta
5. Bajada Recta desde la Cresta hasta el Suelo (z=0.796m -> 0.020m, ac=0)
6. Curva de 180° Plana en el Suelo (R=0.25m, z=0.020m)
7. Tramo Recto de Frenado Final en Suelo (L=0.75m, mu=1.35)
"""

import math
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def generar_graficas_carrito():
    # -------------------------------------------------------------
    # 1. PARÁMETROS FÍSICOS Y GEOMÉTRICOS DEL SISTEMA
    # -------------------------------------------------------------
    g = 9.81
    m_maleta = 0.018    # 18 g (base)
    M_carro = 0.200     # 200 g (base)
    M_tot = m_maleta + M_carro # 218 g

    # Rampa 1: Maleta deslizando desde h0=1.20m por 47cm a 30 deg
    L1 = 0.47
    theta1 = math.radians(30)
    mu_rampa1 = 0.02
    a1 = g * (math.sin(theta1) - mu_rampa1 * math.cos(theta1))
    v1 = math.sqrt(2 * a1 * L1) # ~2.11 m/s
    v1_x = v1 * math.cos(theta1) # ~1.83 m/s
    v1_z = v1 * math.sin(theta1) # ~1.055 m/s

    # Caída vertical de 5cm e impacto inelástico en la transferencia
    dh_drop = 0.05
    t_drop = (-v1_z + math.sqrt(v1_z**2 + 2 * g * dh_drop)) / g
    v_post = (m_maleta * v1_x) / M_tot # ~0.151 m/s (con impulso asistido supervisor llega a ~0.50 m/s)
    v_post_efectivo = 0.50 # Asistido por el empuje de acople

    # -------------------------------------------------------------
    # 2. DISCRETIZACIÓN CONTINUA DE LA TRAYECTORIA
    # -------------------------------------------------------------
    s_vals = []
    h_vals = []
    v_vals = []
    a_tang_vals = []
    a_cent_vals = []

    # A: Transferencia (avance en plataforma horizontal z = 0.915m)
    L_a = 0.16
    s_a = np.linspace(0, L_a, 40)
    for s in s_a:
        s_vals.append(s)
        h_vals.append(0.915)
        v_vals.append(v_post_efectivo)
        a_tang_vals.append(0.0)
        a_cent_vals.append(0.0)

    # B: Bajada 45 deg (L = 0.50m total, dh = 0.354m -> h = 0.561m)
    L_b = 0.50
    s_b = np.linspace(0, L_b, 120)
    theta_b = math.radians(45)
    mu_pista = 0.005
    a_b = g * (math.sin(theta_b) - mu_pista * math.cos(theta_b))
    v_curr = v_post_efectivo
    for s in s_b[1:]:
        v = math.sqrt(v_curr**2 + 2 * a_b * s)
        h = 0.915 - s * math.sin(theta_b)
        s_vals.append(s_vals[-1] + (s_b[1] - s_b[0]))
        h_vals.append(h)
        v_vals.append(v)
        a_tang_vals.append(a_b)
        a_cent_vals.append(0.0)
    v_b_end = v_vals[-1]
    h_b_end = h_vals[-1]

    # C: Curva 1 (90 deg peraltada a +Y, R = 0.18m, horizontal a h = 0.561m)
    R1 = 0.18
    L_c = (math.pi / 2.0) * R1
    s_c = np.linspace(0, L_c, 80)
    for s in s_c[1:]:
        v = v_b_end
        a_c = (v**2) / R1
        s_vals.append(s_vals[-1] + (s_c[1] - s_c[0]))
        h_vals.append(h_b_end)
        v_vals.append(v)
        a_tang_vals.append(0.0)
        a_cent_vals.append(a_c)

    # D: Subida 30 deg en +Y (L = 0.47m, dh = 0.235m -> h = 0.796m)
    L_d = 0.47
    s_d = np.linspace(0, L_d, 120)
    theta_d = math.radians(30)
    a_d = -g * (math.sin(theta_d) + mu_pista * math.cos(theta_d))
    v_start_d = v_vals[-1]
    h_start_d = h_vals[-1]
    for s in s_d[1:]:
        v_sq = v_start_d**2 + 2 * a_d * s
        v = math.sqrt(max(0.01, v_sq))
        h = h_start_d + s * math.sin(theta_d)
        s_vals.append(s_vals[-1] + (s_d[1] - s_d[0]))
        h_vals.append(h)
        v_vals.append(v)
        a_tang_vals.append(a_d)
        a_cent_vals.append(0.0)
    v_d_end = v_vals[-1]
    h_d_end = h_vals[-1]

    # E: Cresta plana (L = 0.06m horizontal a h = 0.796m)
    L_e = 0.06
    s_e = np.linspace(0, L_e, 25)
    for s in s_e[1:]:
        s_vals.append(s_vals[-1] + (s_e[1] - s_e[0]))
        h_vals.append(h_d_end)
        v_vals.append(v_d_end)
        a_tang_vals.append(0.0)
        a_cent_vals.append(0.0)

    # F: NUEVA SECCIÓN: BAJADA RECTA AL SUELO (h: 0.796m -> 0.020m)
    # Pendiente 45° recta en +Y, sin giro centrípeto (a_c = 0)
    h_ground = 0.020
    delta_h_bajada = h_d_end - h_ground # 0.776m
    L_f = delta_h_bajada / math.sin(math.radians(45)) # ~1.097m
    s_f = np.linspace(0, L_f, 180)
    a_f = g * (math.sin(math.radians(45)) - mu_pista * math.cos(math.radians(45)))
    v_start_f = v_d_end
    for s in s_f[1:]:
        v_sq = v_start_f**2 + 2 * a_f * s
        v = math.sqrt(v_sq)
        h = h_d_end - s * math.sin(math.radians(45))
        s_vals.append(s_vals[-1] + (s_f[1] - s_f[0]))
        h_vals.append(h)
        v_vals.append(v)
        a_tang_vals.append(a_f)
        a_cent_vals.append(0.0) # RECTA, a_c = 0!
    v_suelo = v_vals[-1]

    # G: NUEVA SECCIÓN: CURVA DE 180° PLANA EN EL SUELO (z = 0.020m constante)
    # R = 0.25m, gira de +Y a -Y, peraltada con guardarraíles de 5.5cm
    R2 = 0.25
    L_g = math.pi * R2 # 0.785m
    s_g = np.linspace(0, L_g, 150)
    mu_curva = 0.008
    a_fric_curva = -mu_curva * g
    v_curr_g = v_suelo
    for s in s_g[1:]:
        v_sq = v_curr_g**2 + 2 * a_fric_curva * s
        v = math.sqrt(max(0.01, v_sq))
        a_c = (v**2) / R2
        s_vals.append(s_vals[-1] + (s_g[1] - s_g[0]))
        h_vals.append(h_ground)
        v_vals.append(v)
        a_tang_vals.append(a_fric_curva)
        a_cent_vals.append(a_c)
    v_brake_entry = v_vals[-1]

    # H: TRAYECTO FINAL DE FRENADO RECTO EN EL SUELO (mu = 1.35)
    mu_freno = 1.35
    a_freno = -mu_freno * g # ~ -13.24 m/s^2
    d_frenado = (v_brake_entry**2) / (2 * mu_freno * g) # ~ 0.58m
    s_h = np.linspace(0, d_frenado, 120)
    for s in s_h[1:]:
        v_sq = v_brake_entry**2 + 2 * a_freno * s
        v = math.sqrt(max(0.0, v_sq))
        s_vals.append(s_vals[-1] + (s_h[1] - s_h[0]))
        h_vals.append(h_ground)
        v_vals.append(v)
        a_tang_vals.append(a_freno)
        a_cent_vals.append(0.0)

    s_arr = np.array(s_vals)
    h_arr = np.array(h_vals)
    v_arr = np.array(v_vals)
    at_arr = np.array(a_tang_vals)
    ac_arr = np.array(a_cent_vals)

    # -------------------------------------------------------------
    # 3. ENERGÍAS
    # -------------------------------------------------------------
    E_cin = 0.5 * M_tot * (v_arr**2)
    E_pot = M_tot * g * (h_arr - h_ground)
    E_tot = E_cin + E_pot
    E_dissipated = E_tot[0] - E_tot

    # -------------------------------------------------------------
    # 4. CONFIGURACIÓN VISUAL MODERNA DE MATPLOTLIB
    # -------------------------------------------------------------
    plt.rcParams['font.sans-serif'] = 'Segoe UI, Arial, DejaVu Sans'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.edgecolor'] = '#cccccc'
    plt.rcParams['axes.linewidth'] = 0.8

    fig = plt.figure(figsize=(18, 12), dpi=180)
    fig.patch.set_facecolor('#0f141d')

    c_blue = '#00b4d8'
    c_orange = '#ff9100'
    c_green = '#06d6a0'
    c_red = '#ef476f'
    c_purple = '#b5179e'
    c_yellow = '#ffd166'
    c_text = '#e2e8f0'
    c_grid = '#232d3f'

    # -------------------------------------------------------------
    # SUBPLOT 1: PERFIL DE VELOCIDAD Y ALTURA
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.set_facecolor('#151c28')
    ax1.grid(True, linestyle='--', alpha=0.5, color=c_grid)

    line_v, = ax1.plot(s_arr, v_arr, color=c_blue, linewidth=2.8, label='Velocidad v(s) [m/s]')
    ax1.set_xlabel('Distancia recorrida a lo largo de la pista s (m)', color=c_text, fontsize=11, fontweight='600')
    ax1.set_ylabel('Velocidad (m/s)', color=c_blue, fontsize=11, fontweight='600')
    ax1.tick_params(colors=c_text)
    ax1.set_ylim(-0.2, 5.0)

    ax1_twin = ax1.twinx()
    line_h, = ax1_twin.plot(s_arr, h_arr, color=c_orange, linewidth=2.2, linestyle='-.', label='Altura z(s) [m]')
    ax1_twin.set_ylabel('Altura z (m)', color=c_orange, fontsize=11, fontweight='600')
    ax1_twin.tick_params(colors=c_text)
    ax1_twin.set_ylim(-0.05, 1.25)

    # Líneas divisorias de secciones
    s_divs = [L_a, L_a+L_b, L_a+L_b+L_c, L_a+L_b+L_c+L_d+L_e, L_a+L_b+L_c+L_d+L_e+L_f, L_a+L_b+L_c+L_d+L_e+L_f+L_g]
    for s_d_pos in s_divs:
        ax1.axvline(x=s_d_pos, color='#64748b', linestyle=':', alpha=0.7)

    ax1.annotate('1. Transferencia\nv=0.50 m/s', xy=(0.04, 0.50), xytext=(0.02, 1.5),
                 color=c_yellow, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_yellow, lw=1.2))

    ax1.annotate(f'2. Fin Bajada 45°\nv = {v_b_end:.2f} m/s', xy=(L_a+L_b, v_b_end), xytext=(L_a+0.1, 3.2),
                 color=c_green, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_green, lw=1.2))

    ax1.annotate(f'4. Cresta Subida\nv = {v_d_end:.2f} m/s', xy=(L_a+L_b+L_c+L_d, v_d_end), xytext=(1.10, 2.3),
                 color=c_orange, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_orange, lw=1.2))

    ax1.annotate(f'5. Llegada Suelo (Recta)\nv = {v_suelo:.2f} m/s', xy=(s_divs[4], v_suelo), xytext=(s_divs[4]-0.4, 4.3),
                 color=c_blue, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_blue, lw=1.2))

    ax1.annotate(f'7. Detenido (v=0)\nd = {d_frenado:.2f} m', xy=(s_arr[-1], 0.0), xytext=(s_arr[-1]-0.45, 0.9),
                 color=c_red, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_red, lw=1.2))

    ax1.set_title('1. Perfil Cinemático: Velocidad y Altura del Carrito', color=c_text, fontsize=13, fontweight='bold', pad=12)
    lines = [line_v, line_h]
    ax1.legend(lines, [l.get_label() for l in lines], loc='upper center', facecolor='#1e293b', edgecolor='none', labelcolor=c_text)

    # -------------------------------------------------------------
    # SUBPLOT 2: BALANCE DE ENERGÍAS
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_facecolor('#151c28')
    ax2.grid(True, linestyle='--', alpha=0.5, color=c_grid)

    ax2.plot(s_arr, E_cin, color=c_blue, linewidth=2.5, label='Energía Cinética $E_k$')
    ax2.plot(s_arr, E_pot, color=c_orange, linewidth=2.5, label='Energía Potencial $E_p$')
    ax2.plot(s_arr, E_tot, color=c_green, linewidth=2.2, linestyle='--', label='Energía Mecánica $E_{mec}$')
    ax2.plot(s_arr, E_dissipated, color=c_red, linewidth=2.0, linestyle=':', label='Trabajo Disipado $W_{fric}$')

    ax2.set_xlabel('Distancia recorrida s (m)', color=c_text, fontsize=11, fontweight='600')
    ax2.set_ylabel('Energía (Joules)', color=c_text, fontsize=11, fontweight='600')
    ax2.set_title('2. Balance Energético Mecánico (M = 218 g)', color=c_text, fontsize=13, fontweight='bold', pad=12)
    ax2.tick_params(colors=c_text)
    ax2.legend(loc='upper right', facecolor='#1e293b', edgecolor='none', labelcolor=c_text, fontsize=9.5)

    # -------------------------------------------------------------
    # SUBPLOT 3: ACELERACIONES (TANGENCIAL Y CENTRÍPETA)
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_facecolor('#151c28')
    ax3.grid(True, linestyle='--', alpha=0.5, color=c_grid)

    ax3.plot(s_arr, at_arr / g, color=c_yellow, linewidth=2.4, label='Acel. Tangencial $a_t$ / g')
    ax3.plot(s_arr, ac_arr / g, color=c_purple, linewidth=2.6, label='Acel. Centrípeta $a_c$ / g ($v^2/R$)')

    ax3.axhline(y=0, color='#64748b', linestyle='-', linewidth=0.8)
    ax3.set_xlabel('Distancia recorrida s (m)', color=c_text, fontsize=11, fontweight='600')
    ax3.set_ylabel('Aceleración normalizada (unidades de g)', color=c_text, fontsize=11, fontweight='600')
    ax3.set_title('3. Aceleraciones Cinemáticas: Bajada Recta ($a_c=0$) y Curvas', color=c_text, fontsize=13, fontweight='bold', pad=12)
    ax3.tick_params(colors=c_text)

    # Anotación pico centripeto Curva 1
    max_ac1 = (v_b_end**2) / R1 / g
    ax3.annotate(f'Curva 1: {max_ac1:.1f} g\n(Peralte 18°)',
                 xy=(L_a+L_b+0.05, max_ac1), xytext=(L_a+L_b+0.12, max_ac1 - 1.5),
                 color=c_purple, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_purple, lw=1.2))

    # Anotación Bajada Recta: ac = 0
    s_desc_mid = s_divs[3] + L_f/2.0
    ax3.annotate('Bajada Recta:\n$a_c = 0$ (Estabilidad total)',
                 xy=(s_desc_mid, 0.0), xytext=(s_desc_mid - 0.25, 2.5),
                 color=c_green, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_green, lw=1.2))

    # Anotación Curva 180 en el Suelo
    max_ac2 = (v_suelo**2) / R2 / g
    ax3.annotate(f'Curva 180° Suelo: {max_ac2:.1f} g\n(Peralte 22° plano)',
                 xy=(s_divs[4] + 0.3, max_ac2), xytext=(s_divs[4], max_ac2 + 1.2),
                 color=c_purple, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_purple, lw=1.2))

    ax3.annotate(f'Frenado: {a_freno/g:.2f} g',
                 xy=(s_arr[-1]-0.15, a_freno/g), xytext=(s_arr[-1]-0.45, a_freno/g - 1.2),
                 color=c_red, fontsize=8.5, fontweight='600',
                 arrowprops=dict(arrowstyle='->', color=c_red, lw=1.2))

    ax3.legend(loc='upper right', facecolor='#1e293b', edgecolor='none', labelcolor=c_text, fontsize=9.5)

    # -------------------------------------------------------------
    # SUBPLOT 4: BARRIDO DE MASA DEL CARRO VS DISTANCIA DE FRENADO
    # -------------------------------------------------------------
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_facecolor('#151c28')
    ax4.grid(True, linestyle='--', alpha=0.5, color=c_grid)

    masas_sweep = np.linspace(50, 500, 200) # gramos
    d_frenos_18g = []
    d_frenos_50g = []
    d_frenos_100g = []

    for M in masas_sweep:
        M_kg = M / 1000.0
        # Maleta 18g
        vp_18 = (0.018 * v1_x) / (0.018 + M_kg) + 0.35
        vs_18 = math.sqrt(vp_18**2 + 2 * g * (0.915 - h_ground))
        d_frenos_18g.append((vs_18**2) / (2 * mu_freno * g))

        # Maleta 50g
        vp_50 = (0.050 * v1_x) / (0.050 + M_kg) + 0.35
        vs_50 = math.sqrt(vp_50**2 + 2 * g * (0.915 - h_ground))
        d_frenos_50g.append((vs_50**2) / (2 * mu_freno * g))

        # Maleta 100g
        vp_100 = (0.100 * v1_x) / (0.100 + M_kg) + 0.35
        vs_100 = math.sqrt(vp_100**2 + 2 * g * (0.915 - h_ground))
        d_frenos_100g.append((vs_100**2) / (2 * mu_freno * g))

    ax4.plot(masas_sweep, d_frenos_18g, color=c_green, linewidth=2.6, label='Maleta base (18 g)')
    ax4.plot(masas_sweep, d_frenos_50g, color=c_yellow, linewidth=2.2, linestyle='--', label='Maleta cargada (50 g)')
    ax4.plot(masas_sweep, d_frenos_100g, color=c_red, linewidth=2.2, linestyle=':', label='Maleta pesada (100 g)')

    ax4.axhline(y=0.75, color='#ef476f', linestyle='--', linewidth=1.8, label='Límite de Pista disponible (0.75 m)')
    ax4.axvline(x=200, color=c_blue, linestyle=':', linewidth=1.5, label='Masa Nominal Carrito (200 g)')

    ax4.plot(200, d_frenado, marker='o', markersize=9, color=c_blue, label=f'Operación Nominal ({d_frenado:.2f} m)')

    ax4.set_xlabel('Masa del Carrito (gramos)', color=c_text, fontsize=11, fontweight='600')
    ax4.set_ylabel('Distancia de Frenado Final (metros)', color=c_text, fontsize=11, fontweight='600')
    ax4.set_title('4. Distancia de Frenado vs Masa del Carrito', color=c_text, fontsize=13, fontweight='bold', pad=12)
    ax4.tick_params(colors=c_text)
    ax4.set_ylim(0.40, 0.85)
    ax4.legend(loc='upper right', facecolor='#1e293b', edgecolor='none', labelcolor=c_text, fontsize=9.0)

    plt.suptitle('ANÁLISIS DINÁMICO Y CINEMÁTICO: SECUENCIA ACTUALIZADA (BAJADA RECTA -> CURVA 180° SUELO)',
                 color='#ffffff', fontsize=15, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0.02, 1, 0.96])

    os.makedirs('doc', exist_ok=True)
    out_img = os.path.join('doc', 'analisis_comportamiento_carrito.png')
    plt.savefig(out_img, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    print(f"[OK] Gráfica guardada exitosamente en: {out_img}")

    # -------------------------------------------------------------
    # 5. TRAYECTORIA 3D CON MAPA DE CALOR DE VELOCIDAD
    # -------------------------------------------------------------
    fig_3d = plt.figure(figsize=(12, 8), dpi=180)
    fig_3d.patch.set_facecolor('#0f141d')
    ax_3d = fig_3d.add_subplot(111, projection='3d')
    ax_3d.set_facecolor('#0f141d')

    x_coords = []
    y_coords = []
    z_coords = []
    v_3d = []

    # A: Transferencia (x: 0.46 a 0.62, y=0.20, z=0.915)
    for x in np.linspace(0.46, 0.62, 30):
        x_coords.append(x)
        y_coords.append(0.20)
        z_coords.append(0.915)
        v_3d.append(v_post_efectivo)

    # B: Bajada 45 deg (x: 0.62 a 1.14, y=0.20, z: 0.915 a 0.561)
    for s in np.linspace(0, 0.50, 80):
        x = 0.62 + s * math.cos(math.radians(45))
        z = 0.915 - s * math.sin(math.radians(45))
        v = math.sqrt(v_post_efectivo**2 + 2 * a_b * s)
        x_coords.append(x)
        y_coords.append(0.20)
        z_coords.append(z)
        v_3d.append(v)

    # C: Curva 1 (90 deg a +Y, R=0.18, centro en 1.14, 0.38)
    for phi in np.linspace(-math.pi/2, 0, 50):
        x = 1.14 + 0.18 * math.cos(phi)
        y = 0.38 + 0.18 * math.sin(phi)
        x_coords.append(x)
        y_coords.append(y)
        z_coords.append(0.561)
        v_3d.append(v_b_end)

    # D: Subida 30 deg en +Y (y: 0.38 a 0.85, z: 0.561 a 0.796)
    for s in np.linspace(0, 0.47, 80):
        y = 0.38 + s * math.cos(math.radians(30))
        z = 0.561 + s * math.sin(math.radians(30))
        v_sq = v_b_end**2 + 2 * a_d * s
        v = math.sqrt(max(0.01, v_sq))
        x_coords.append(1.32)
        y_coords.append(y)
        z_coords.append(z)
        v_3d.append(v)

    # E: Cresta plana en +Y (y: 0.85 a 0.91, z=0.796)
    for y in np.linspace(0.85, 0.91, 20):
        x_coords.append(1.32)
        y_coords.append(y)
        z_coords.append(0.796)
        v_3d.append(v_d_end)

    # F: NUEVA BAJADA RECTA AL SUELO (x=1.32, y: 0.91 a 1.68, z: 0.796 a 0.020)
    for s in np.linspace(0, L_f, 90):
        y = 0.91 + s * math.cos(math.radians(45))
        z = 0.796 - s * math.sin(math.radians(45))
        v = math.sqrt(v_d_end**2 + 2 * a_f * s)
        x_coords.append(1.32)
        y_coords.append(y)
        z_coords.append(z)
        v_3d.append(v)

    # G: NUEVA CURVA 180° PLANA EN EL SUELO (z=0.020m, R=0.25, centro x=1.07, y=1.68)
    for psi in np.linspace(0, math.pi, 80):
        x = 1.07 + 0.25 * math.cos(psi)
        y = 1.68 + 0.25 * math.sin(psi)
        z = 0.020 # COMPLETAMENTE EN EL SUELO
        v = v_suelo
        x_coords.append(x)
        y_coords.append(y)
        z_coords.append(z)
        v_3d.append(v)

    # H: TRAYECTO FINAL DE FRENADO RECTO EN -Y (x=0.82, y: 1.68 a 1.10, z=0.020)
    for s in np.linspace(0, d_frenado, 50):
        x_coords.append(0.82)
        y_coords.append(1.68 - s)
        z_coords.append(0.020)
        v_sq = v_brake_entry**2 + 2 * a_freno * s
        v_3d.append(math.sqrt(max(0.0, v_sq)))

    p3d = ax_3d.scatter(x_coords, y_coords, z_coords, c=v_3d, cmap='plasma', s=16, alpha=0.9)
    ax_3d.plot(x_coords, y_coords, z_coords, color='#94a3b8', linewidth=1.0, alpha=0.5)

    cbar = fig_3d.colorbar(p3d, ax=ax_3d, shrink=0.6, aspect=18, pad=0.08)
    cbar.set_label('Velocidad del Carrito (m/s)', color=c_text, fontsize=11, fontweight='600')
    cbar.ax.yaxis.set_tick_params(color=c_text)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=c_text)

    ax_3d.set_xlabel('Eje X (m)', color=c_text, fontweight='600', labelpad=8)
    ax_3d.set_ylabel('Eje Y (m)', color=c_text, fontweight='600', labelpad=8)
    ax_3d.set_zlabel('Altura Z (m)', color=c_text, fontweight='600', labelpad=8)
    ax_3d.tick_params(colors=c_text)
    ax_3d.set_title('Trayectoria Espacial 3D (Bajada Recta -> Curva 180° Suelo -> Frenado)', color='#ffffff', fontsize=13, fontweight='bold', pad=15)

    ax_3d.view_init(elev=28, azim=-125)

    out_3d = os.path.join('doc', 'trayectoria_3d_carrito.png')
    plt.savefig(out_3d, dpi=200, facecolor=fig_3d.get_facecolor(), edgecolor='none')
    print(f"[OK] Trayectoria 3D guardada exitosamente en: {out_3d}")

if __name__ == "__main__":
    generar_graficas_carrito()
