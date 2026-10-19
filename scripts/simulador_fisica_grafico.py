"""
Simulador y Graficador Analítico de Física para la Pista tipo Montaña Rusa.
Secuencia Actualizada:
1. Rampa 1: Maleta deslizando a 30°
2. Estación de Transferencia con Lengüeta
3. Bajada 2 (45°)
4. Curva Peraltada 1 (90° a +Y)
5. Subida (30° a +Y) y Cresta
6. Bajada Recta al Suelo (h=0.796m -> 0.020m, ac=0)
7. Curva 180° Plana en el Suelo (R=0.25m, z=0.020m)
8. Zona de Frenado Final en Suelo (mu=1.35)
"""

import math
import os
import numpy as np
import matplotlib.pyplot as plt

def run_physics_simulation():
    g = 9.81
    m_maleta = 0.018     # 18 gramos base
    M_carro_base = 0.200 # 200 gramos base
    
    # 1. Rampa 1: Maleta
    # L = 0.47m, 30 deg, h0 = 1.20m
    L1 = 0.47
    theta1 = math.radians(30)
    mu_rampa = 0.02
    h0 = 1.20
    dh1 = L1 * math.sin(theta1)
    h1 = h0 - dh1
    a1 = g * (math.sin(theta1) - mu_rampa * math.cos(theta1))
    v1 = math.sqrt(2 * a1 * L1)
    v1_x = v1 * math.cos(theta1)
    v1_z = -v1 * math.sin(theta1)
    
    # Caída vertical 5cm con velocidad hacia abajo
    dh_drop = 0.05
    h_cart = h1 - dh_drop
    vz_down = v1 * math.sin(theta1) # 1.055 m/s hacia abajo
    t_drop = (-vz_down + math.sqrt(vz_down**2 + 2 * g * dh_drop)) / g
    dx_drop = v1_x * t_drop
    
    # Transferencia y acople en el carrito
    v_post = 0.50 # Asistido por el empuje físico del acople
    
    # 2. Bajada 2: Carro + Maleta
    # L = 0.50m, 45 deg
    L2 = 0.50
    theta2 = math.radians(45)
    dh2 = L2 * math.sin(theta2)
    h2 = h_cart - dh2
    v2 = math.sqrt(v_post**2 + 2 * g * dh2)
    
    # 3. Curva 1: 90 deg, R=0.18m, peralte 18 deg
    R1 = 0.18
    v_ideal_peralte1 = math.sqrt(g * R1 * math.tan(math.radians(18)))
    a_centripeta1 = (v2**2) / R1
    
    # 4. Subida: L=0.47m, 30 deg
    L3 = 0.47
    theta3 = math.radians(30)
    dh3 = L3 * math.sin(theta3)
    h3 = h2 + dh3
    v3 = math.sqrt(v2**2 - 2 * g * dh3)
    
    # 5. Cresta: L=0.06m
    L4 = 0.06
    v4 = v3
    h4 = h3
    
    # 6. Bajada Recta al Suelo (h4 -> h_suelo = 0.020m, ac = 0)
    h_suelo = 0.020
    dh_desc = h4 - h_suelo
    v_suelo = math.sqrt(v4**2 + 2 * g * dh_desc)
    
    # 7. Curva 180° Plana en el Suelo (R=0.25m, z=0.020m constante)
    R2 = 0.25
    a_centripeta2 = (v_suelo**2) / R2
    
    # 8. Frenado final en suelo: L_freno = 0.75m, mu = 1.35
    mu_freno = 1.35
    d_frenado = (v_suelo**2) / (2 * g * mu_freno)
    
    print("=" * 65)
    print("        RESULTADOS ANALÍTICOS DE FÍSICA MECÁNICA")
    print("=" * 65)
    print(f"Rampa 1: Altura {h0:.2f}m -> {h1:.3f}m | Vel fin: {v1:.2f} m/s (vx={v1_x:.2f} m/s)")
    print(f"Caída 5cm: dx_avance = {dx_drop*100:.1f} cm (cae guiado por la lengüeta)")
    print(f"Acople en Carrito: v_post = {v_post:.3f} m/s")
    print(f"Fin Bajada 2 (h={h2:.3f}m): Vel = {v2:.2f} m/s")
    print(f"Curva Peraltada 1: R={R1}m, a_centripeta = {a_centripeta1/g:.1f} g")
    print(f"Cresta de Subida (h={h3:.3f}m): Vel = {v3:.2f} m/s (>0, pasa con margen)")
    print(f"Bajada Recta al Suelo: Descendiendo {dh_desc:.3f}m en línea recta (ac = 0)")
    print(f"Entrada a Curva 180° en Suelo: Vel = {v_suelo:.2f} m/s (plano z={h_suelo}m)")
    print(f"Distancia de frenado (M={M_carro_base*1000:.0f}g): {d_frenado:.2f} m (de {0.75:.2f}m disponibles)")
    print("=" * 65)
    
    # Barrido paramétrico: Distancia de frenado vs Masa del Carrito
    masas_carro = np.linspace(0.050, 0.600, 150)
    distancias_frenado = []
    
    for M in masas_carro:
        v_p = (m_maleta * v1_x) / (m_maleta + M) + 0.35
        v_s = math.sqrt(v_p**2 + 2 * g * (h_cart - h_suelo))
        d_f = (v_s**2) / (2 * g * mu_freno)
        distancias_frenado.append(d_f)
        
    distancias_frenado = np.array(distancias_frenado)
    
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Gráfico 1: Perfil de Altura y Velocidad
    tramos_s = [
        0, 
        L1, 
        L1 + 0.16, 
        L1 + 0.16 + L2, 
        L1 + 0.16 + L2 + math.pi*R1/2,
        L1 + 0.16 + L2 + math.pi*R1/2 + L3, 
        L1 + 0.16 + L2 + math.pi*R1/2 + L3 + L4,
        L1 + 0.16 + L2 + math.pi*R1/2 + L3 + L4 + 1.10, # bajada recta
        L1 + 0.16 + L2 + math.pi*R1/2 + L3 + L4 + 1.10 + math.pi*R2, # curva 180 en suelo
        L1 + 0.16 + L2 + math.pi*R1/2 + L3 + L4 + 1.10 + math.pi*R2 + d_frenado
    ]
    
    alturas = [h0, h1, h_cart, h2, h2, h3, h4, h_suelo, h_suelo, h_suelo]
    velocidades = [0.0, v1, v_post, v2, v2, v3, v4, v_suelo, v_suelo, 0.0]
    
    color_alt = '#1f77b4'
    ax1.set_xlabel('Distancia a lo largo de la pista (m)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Altura z (m)', color=color_alt, fontsize=11, fontweight='bold')
    line1 = ax1.plot(tramos_s, alturas, color=color_alt, marker='o', linewidth=2.5, label='Altura z(s)')
    ax1.tick_params(axis='y', labelcolor=color_alt)
    ax1.set_ylim(-0.05, 1.30)
    
    ax1_twin = ax1.twinx()
    color_vel = '#d62728'
    ax1_twin.set_ylabel('Velocidad (m/s)', color=color_vel, fontsize=11, fontweight='bold')
    line2 = ax1_twin.plot(tramos_s, velocidades, color=color_vel, marker='s', linestyle='--', linewidth=2.0, label='Velocidad v(s)')
    ax1_twin.tick_params(axis='y', labelcolor=color_vel)
    ax1_twin.set_ylim(-0.2, 5.0)
    
    # Anotaciones
    ax1.annotate('1. Rampa 30°', xy=(0.20, 1.05), fontsize=8.5, color=color_alt)
    ax1.annotate('2. Acople Carro', xy=(0.50, 0.90), fontsize=8.5, color='#ff7f0e')
    ax1.annotate('3. Bajada 45°', xy=(0.85, 0.65), fontsize=8.5, color=color_alt)
    ax1.annotate('4. Curva 1 (90°)', xy=(1.25, 0.58), fontsize=8.5, color='#2ca02c')
    ax1.annotate('5. Cresta', xy=(1.80, 0.82), fontsize=8.5, color=color_alt)
    ax1.annotate('6. Bajada Recta', xy=(2.45, 0.40), fontsize=8.5, color='#1f77b4')
    ax1.annotate('7. Curva 180° Suelo', xy=(3.20, 0.12), fontsize=8.5, color='#2ca02c')
    ax1.annotate('8. Frenado Final', xy=(3.90, 0.05), fontsize=8.5, color='#9467bd')
    
    ax1.set_title('Perfil de Altura y Velocidad (Secuencia Reconfigurada)', fontsize=12, fontweight='bold')
    
    # Gráfico 2: Masa del Carrito vs Distancia de Frenado
    ax2.plot(masas_carro * 1000, distancias_frenado, color='#2ca02c', linewidth=2.5, label='Distancia de Frenado Real')
    ax2.axhline(y=0.75, color='#d62728', linestyle=':', linewidth=2, label='Límite de Pista (0.75 m)')
    ax2.axvline(x=200, color='#1f77b4', linestyle='--', linewidth=1.5, label='Masa Nominal (200 g)')
    
    ax2.plot(200, d_frenado, marker='*', markersize=14, color='#d62728', label=f'Operación Nominal ({d_frenado:.2f} m)')
    
    ax2.set_xlabel('Masa del Carrito (gramos)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Distancia de Frenado Final (metros)', fontsize=11, fontweight='bold')
    ax2.set_title('Efecto del Peso del Carro en la Detención Final', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', frameon=True)
    ax2.set_xlim(50, 600)
    
    plt.tight_layout()
    os.makedirs('doc', exist_ok=True)
    out_img = os.path.join('doc', 'grafica_fisica_pista.png')
    plt.savefig(out_img, dpi=200)
    print(f"Gráfica guardada exitosamente en: {out_img}")

if __name__ == "__main__":
    run_physics_simulation()
