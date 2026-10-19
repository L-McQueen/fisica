"""
Controlador Supervisor en Python para la Simulación de Física de Webots.
Monitorea en tiempo real la cinemática y dinámica de la maleta y el carrito,
despliega un HUD interactivo en el visor 3D y realiza el cálculo teórico
comparativo del peso/masa del carrito y la distancia de frenado.
"""

import sys
import math
from controller import Supervisor

def main():
    supervisor = Supervisor()
    time_step = int(supervisor.getBasicTimeStep())
    if time_step <= 0:
        time_step = 16

    # Referencias a nodos en el mundo Webots
    node_maleta = supervisor.getFromDef("MALETA")
    node_carrito = supervisor.getFromDef("CARRITO")

    if not node_maleta or not node_carrito:
        print("[ERROR] No se encontraron los nodos MALETA o CARRITO por DEF.")
        return

    field_mass_maleta = node_maleta.getField("physics").getSFNode().getField("mass")
    field_mass_carrito = node_carrito.getField("physics").getSFNode().getField("mass")

    m_maleta = field_mass_maleta.getSFFloat()
    M_carrito = field_mass_carrito.getSFFloat()

    # Parametros geometricos y fisicos
    g = 9.81
    h_inicio_maleta = 1.20
    L_rampa1 = 0.47
    theta1_deg = 30.0
    theta1_rad = math.radians(theta1_deg)
    h_fin_rampa1 = h_inicio_maleta - L_rampa1 * math.sin(theta1_rad)
    h_transf = h_fin_rampa1 - 0.05
    L_freno_total = 0.75
    mu_freno_nominal = 1.35

    # Calculos teoricos a priori
    # 1. Velocidad fin rampa 1 (suponiendo mu muy bajo ~0.02)
    mu_rampa1 = 0.02
    a1_teorica = g * (math.sin(theta1_rad) - mu_rampa1 * math.cos(theta1_rad))
    v1_teorica = math.sqrt(2 * a1_teorica * L_rampa1)
    v1x_teorica = v1_teorica * math.cos(theta1_rad)
    vz_down = v1_teorica * math.sin(theta1_rad)
    t_drop = (-vz_down + math.sqrt(vz_down**2 + 2 * g * 0.05)) / g
    dx_drop = v1x_teorica * t_drop

    # 2. Caida vertical de 5cm e impacto
    v_post_teorica = (m_maleta / (m_maleta + M_carrito)) * v1x_teorica

    # 3. Velocidad al llegar al suelo (h=0) desde h_transf
    v_suelo_teorica = math.sqrt(v_post_teorica**2 + 2 * g * h_transf)

    # 4. Distancia de frenado teorica con la masa actual
    d_freno_teorica = (v_suelo_teorica**2) / (2 * g * mu_freno_nominal)

    # 5. Formula inversa: ¿Que masa M_req deberia tener el carrito para frenar exactamente en L_obj = 0.50m?
    L_obj = 0.50
    # 2 * g * mu * L_obj = v_post^2 + 2 * g * h_transf
    # v_post_req^2 = 2 * g * (mu * L_obj - h_transf)
    term_diff = mu_freno_nominal * L_obj - h_transf
    if term_diff > 0:
        v_post_req = math.sqrt(2 * g * term_diff)
        if v1x_teorica > v_post_req:
            M_req_teorica = m_maleta * (v1x_teorica / v_post_req - 1.0)
        else:
            M_req_teorica = 0.200
    else:
        M_req_teorica = 0.200

    print("=" * 65)
    print("      LABORATORIO DE FISICA: PISTA TIPO MONTAÑA RUSA       ")
    print("=" * 65)
    print(f" * Masa Maleta (m):           {m_maleta*1000:.1f} g")
    print(f" * Masa Carrito (M):          {M_carrito*1000:.1f} g")
    print(f" * Altura inicial:            {h_inicio_maleta:.2f} m")
    print(f" * Rampa 1:                   L={L_rampa1:.2f} m, angulo={theta1_deg:.0f}°")
    print(f" * Caida vertical estacion:   5.0 cm (h={h_transf:.3f} m)")
    print(f" * Bajada 2:                  L=0.50 m, angulo=45°")
    print(f" * Curva 1:                   R=0.10 m, peralte=30°")
    print(f" * Subida y Cresta:           L=0.47 m (30°), cresta=0.10 m")
    print(f" * Bajada y Curva 2 (180°):   R=0.18 m hasta el suelo (h=0)")
    print(f" * Tramo de Frenado:          L=0.75 m, mu={mu_freno_nominal:.2f}")
    print("-" * 65)
    print(" --- PREDICCIONES TEORICAS ---")
    print(f" > Vel. maleta fin rampa 1:    {v1_teorica:.2f} m/s (vx = {v1x_teorica:.2f} m/s)")
    print(f" > Vel. post-impacto carrito:  {v_post_teorica:.2f} m/s")
    print(f" > Vel. entrada al suelo:      {v_suelo_teorica:.2f} m/s")
    print(f" > Distancia frenado prevista: {d_freno_teorica:.2f} m")
    print(f" > Masa Carrito requerida para frenar en {L_obj:.2f}m: {M_req_teorica*1000:.1f} g")
    print("=" * 65)

    # Variables de telemetria
    fase = 0
    nombre_fases = [
        "1. Maleta deslizandose por Rampa 1 (h=1.20m, 30°)",
        "2. Caida 5cm e Impacto en Carrito (Transferencia)",
        "3. Carrito en Bajada 2 (50cm, 45°)",
        "4. Carrito en Curva Peraltada 1 (90°, R=10cm, 30°)",
        "5. Carrito en Subida (47cm, 30°) hacia Cresta",
        "6. Carrito en Curva 2 (180°) descendiendo al suelo",
        "7. Carrito en Zona de Frenado Final",
        "8. DETENIDO COMPLETAMENTE"
    ]

    v1_medida = 0.0
    v_post_medida = 0.0
    v_suelo_medida = 0.0
    y_freno_inicio = None
    distancia_frenado_real = 0.0
    tiempo_inicio = supervisor.getTime()

    step_count = 0

    while supervisor.step(time_step) != -1:
        step_count += 1
        t_sim = supervisor.getTime() - tiempo_inicio

        # Posicion y velocidad en tiempo real
        pos_m = node_maleta.getPosition()
        vel_m = node_maleta.getVelocity()
        speed_m = math.sqrt(vel_m[0]**2 + vel_m[1]**2 + vel_m[2]**2)

        pos_c = node_carrito.getPosition()
        vel_c = node_carrito.getVelocity()
        speed_c = math.sqrt(vel_c[0]**2 + vel_c[1]**2 + vel_c[2]**2)

        # Transiciones de fase
        if fase == 0:
            if pos_m[2] < 0.970:
                fase = 1
                v1_medida = speed_m
                print(f"[{t_sim:.2f}s] Maleta llega al final de Rampa 1. Vel = {v1_medida:.2f} m/s")
        elif fase == 1:
            # Impacto: carrito comienza a moverse
            if speed_c > 0.08:
                fase = 2
                v_post_medida = speed_c
                print(f"[{t_sim:.2f}s] ¡Impacto inelastico! Vel. Carrito = {v_post_medida:.2f} m/s")
        elif fase == 2:
            # Bajada 2: x avanza hacia 1.05
            if pos_c[0] > 1.00:
                fase = 3
        elif fase == 3:
            # Curva 1: y avanza hacia 0.30
            if pos_c[1] > 0.28:
                fase = 4
        elif fase == 4:
            # Subida y cresta: z sube y y pasa de 0.70
            if pos_c[1] > 0.75:
                fase = 5
        elif fase == 5:
            # Curva 180 hacia suelo: z baja cerca de 0.05
            if pos_c[2] < 0.08:
                fase = 6
                v_suelo_medida = speed_c
                y_freno_inicio = pos_c[1]
                print(f"[{t_sim:.2f}s] Entrando a Zona de Frenado. Vel = {v_suelo_medida:.2f} m/s")
        elif fase == 6:
            # En zona de frenado
            if y_freno_inicio is not None:
                distancia_frenado_real = abs(pos_c[1] - y_freno_inicio)
            if speed_c < 0.02 and t_sim > 1.0:
                fase = 7
                print(f"[{t_sim:.2f}s] ¡Carrito DETENIDO! Distancia de frenado = {distancia_frenado_real:.2f} m")

        # Energia mecanica del sistema
        m_tot = m_maleta + M_carrito
        E_cin = 0.5 * m_tot * (speed_c**2)
        E_pot = m_tot * g * max(0.0, pos_c[2])

        # Actualizar HUD en el visor 3D de Webots cada 4 pasos
        if step_count % 4 == 0:
            # Titulo principal
            supervisor.setLabel(0, "SIMULADOR DE FISICA: PISTA DE LABORATORIO", 0.02, 0.02, 0.08, 0x00FFCC, 0.0, "Arial")
            
            # Estado actual
            color_fase = 0xFFFF00 if fase < 7 else 0x00FF00
            supervisor.setLabel(1, f"Fase: {nombre_fases[fase]}", 0.02, 0.06, 0.06, color_fase, 0.0, "Arial")

            # Telemetria en vivo
            txt_telemetria = (f"Tiempo: {t_sim:.2f}s | Vel Carro: {speed_c:.2f} m/s | "
                              f"Alt: {pos_c[2]:.2f}m | E_cin: {E_cin*1000:.1f} mJ | E_pot: {E_pot*1000:.1f} mJ")
            supervisor.setLabel(2, txt_telemetria, 0.02, 0.10, 0.055, 0xFFFFFF, 0.0, "Lucida Console")

            # Comparativa Teoria vs Simulacion
            txt_comp1 = f"Vel Maleta Impacto: Sim={v1_medida:.2f} m/s (Teor={v1_teorica:.2f} m/s)"
            txt_comp2 = f"Vel Post-Impacto:   Sim={v_post_medida:.2f} m/s (Teor={v_post_teorica:.2f} m/s)"
            supervisor.setLabel(3, txt_comp1, 0.02, 0.14, 0.05, 0xE0E0E0, 0.0, "Lucida Console")
            supervisor.setLabel(4, txt_comp2, 0.02, 0.17, 0.05, 0xE0E0E0, 0.0, "Lucida Console")

            # Analisis de Frenado
            if fase >= 6:
                txt_freno = (f"Frenado: Dist Real={distancia_frenado_real:.2f}m | Prevista={d_freno_teorica:.2f}m | "
                             f"Masa Carro={M_carrito*1000:.0f}g (Req p/0.50m: {M_req_teorica*1000:.0f}g)")
                supervisor.setLabel(5, txt_freno, 0.02, 0.20, 0.055, 0x33FF99, 0.0, "Arial")
            else:
                txt_freno = f"Zona Frenado: L={L_freno_total}m | Masa Carro={M_carrito*1000:.0f}g | Masa Optima={M_req_teorica*1000:.0f}g"
                supervisor.setLabel(5, txt_freno, 0.02, 0.20, 0.05, 0xAAAAAA, 0.0, "Arial")

if __name__ == "__main__":
    main()
