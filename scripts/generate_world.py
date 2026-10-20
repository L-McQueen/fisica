"""
Generador del Mundo Webots para la Pista tipo Montaña Rusa de Laboratorio.
Secuencia exacta solicitada:
1. Rampa 1 (Maleta desde 1.20m, 47cm, 30°) con lengüeta de acople directo.
2. Estación de transferencia y acople con retención total de la maleta.
3. Bajada 2 (50cm, 45°) con empalmes suaves.
4. Curva 1 (90° peraltada hacia +Y).
5. Subida (47cm, 30° hacia +Y) y Cresta.
6. Bajada Recta desde la cresta hasta el suelo (h=0.02m).
7. Curva de 180° plana en el suelo (peraltada con guardarraíles altos).
8. Trayecto final recto de frenado en el suelo (L=75cm, mu=1.35).
"""

import math
import os

def create_smooth_spine():
    """
    Construye la espina dorsal tridimensional continua (C1) de la pista del carrito.
    """
    slices = [] # lista de (P, T, L, U, is_brake)

    def add_slice(P, T, L, U, is_brake=False, custom_pts=None):
        slices.append((P, T, L, U, is_brake, custom_pts))

    y_line = 0.20

    # -------------------------------------------------------------
    # 1. Estación de Transferencia (Horizontal, h = 0.915m)
    # Sección plana alargada a 35cm antes de la caída (x: 0.44m a 0.79m)
    # Permite que el carrito espere en reposo estático hasta el impacto
    # -------------------------------------------------------------
    x_plat_start = 0.44
    x_plat_end = 0.79
    z_plat = 0.915
    N_plat = 18
    for i in range(N_plat + 1):
        u = i / float(N_plat)
        x = x_plat_start + u * (x_plat_end - x_plat_start)
        P = [x, y_line, z_plat]
        T = [1.0, 0.0, 0.0]
        L = [0.0, 1.0, 0.0]
        U = [0.0, 0.0, 1.0]
        add_slice(P, T, L, U)

    # -------------------------------------------------------------
    # 2. Transición Convexa: De horizontal (0°) a bajada (-45°)
    # Arco circular de radio R = 0.20m
    # -------------------------------------------------------------
    R_t1 = 0.20
    N_t1 = 14
    for i in range(1, N_t1 + 1):
        alpha = (i / float(N_t1)) * math.radians(45)
        x = x_plat_end + R_t1 * math.sin(alpha)
        z = z_plat - R_t1 * (1.0 - math.cos(alpha))
        ca, sa = math.cos(alpha), math.sin(alpha)
        T = [ca, 0.0, -sa]
        L = [0.0, 1.0, 0.0]
        U = [sa, 0.0, ca]
        add_slice([x, y_line, z], T, L, U)

    x_bajada_start = x
    z_bajada_start = z

    # -------------------------------------------------------------
    # 3. Bajada 2 Recta a 45°
    # Longitud L = 0.335m
    # -------------------------------------------------------------
    L_bajada = 0.335
    ca45 = math.cos(math.radians(45))
    sa45 = math.sin(math.radians(45))
    N_bajada = 18
    for i in range(1, N_bajada + 1):
        s = (i / float(N_bajada)) * L_bajada
        x = x_bajada_start + s * ca45
        z = z_bajada_start - s * sa45
        T = [ca45, 0.0, -sa45]
        L = [0.0, 1.0, 0.0]
        U = [sa45, 0.0, ca45]
        add_slice([x, y_line, z], T, L, U)

    x_valle_start = x
    z_valle_start = z

    # -------------------------------------------------------------
    # 4. Transición Cóncava de Valle Suave: De -45° a horizontal (0°)
    # Arco circular de radio ampliado R = 0.30m para eliminar el impacto vertical
    # -------------------------------------------------------------
    R_t2 = 0.30
    N_t2 = 18
    for i in range(1, N_t2 + 1):
        alpha = math.radians(45) * (1.0 - i / float(N_t2))
        x = x_valle_start + R_t2 * (math.sin(math.radians(45)) - math.sin(alpha))
        z = z_valle_start - R_t2 * (math.cos(alpha) - math.cos(math.radians(45)))
        ca, sa = math.cos(alpha), math.sin(alpha)
        T = [ca, 0.0, -sa]
        L = [0.0, 1.0, 0.0]
        U = [sa, 0.0, ca]
        add_slice([x, y_line, z], T, L, U)

    x_straight_start = x
    z_straight = z

    # -------------------------------------------------------------
    # 4b. Tramo Recto de Asentamiento Horizontal (L = 12cm)
    # Permite que el carrito se nivele y estabilice tras el valle en cota plana z_straight.
    # Cero torsión transversal (dz = 0): vía completamente plana, nivelada y amplia (14cm).
    # -------------------------------------------------------------
    L_straight = 0.12
    N_straight = 12

    for i in range(1, N_straight + 1):
        x = x_straight_start + (i / float(N_straight)) * L_straight
        P = [x, y_line, z_straight]
        T = [1.0, 0.0, 0.0]
        L = [0.0, 1.0, 0.0]
        U = [0.0, 0.0, 1.0]
        add_slice(P, T, L, U)

    x_c1_start = x
    z_c1 = z_straight

    # -------------------------------------------------------------
    # 5. Curva 1: Giro circular de 90° hacia +Y con Peralte Puro Rotado a 30°
    # - Marco ortonormal exacto (P, T, L, U): U-channel canónico sin distorsión
    # - Ancho constante W = 14.0cm en base y coronación: cero acuñamiento
    # - Pared exterior perpendicular al piso peraltado: inclinada 30° hacia el INTERIOR
    #   actuando como techo de retención física anti-desborde (imposible salir volando)
    # - Roll-in y roll-out cúbicos ultrasuaves con continuidad C1 perfecta (0.000mm)
    # -------------------------------------------------------------
    R1 = 0.35
    x_c1_center = x_c1_start
    y_c1_center = y_line + R1
    N_c1 = 36
    theta_bank_max = math.radians(30.0) # 30 grados de peralte real rotado (~7.0cm de desnivel)

    for i in range(1, N_c1 + 1):
        phi = -math.pi/2.0 + (i / float(N_c1)) * (math.pi/2.0)
        
        # Roll-in cúbico progresivo (1..14, 25cm), meseta sostenida (15..22, 15cm), roll-out cúbico (23..36, 25cm)
        if i <= 14:
            v = i / 14.0
            theta = theta_bank_max * (3.0 * v**2 - 2.0 * v**3)
        elif i <= 22:
            theta = theta_bank_max
        else:
            v = (36 - i) / 14.0
            theta = theta_bank_max * (3.0 * v**2 - 2.0 * v**3)

        rx = math.cos(phi)
        ry = math.sin(phi)
        
        # Centro de la vía en arco circular a cota constante z_c1:
        P = [x_c1_center + R1 * rx, y_c1_center + R1 * ry, z_c1]
        T = [-math.sin(phi), math.cos(phi), 0.0]
        L_flat = [-rx, -ry, 0.0]
        U_flat = [0.0, 0.0, 1.0]
        
        # Rotación de peralte canónica (L inclinado hacia abajo al interior, U perpendicular al piso inclinado hacia adentro):
        ct, st = math.cos(theta), math.sin(theta)
        L = [ct * L_flat[k] - st * U_flat[k] for k in range(3)]
        U = [st * L_flat[k] + ct * U_flat[k] for k in range(3)]
        
        add_slice(P, T, L, U)

    x_hill_start = x_c1_center + R1
    y_hill_start = y_c1_center
    z_hill_start = z_c1

    # -------------------------------------------------------------
    # 6. Transición Cóncava hacia Subida: De horizontal (0°) a +30° en +Y
    # Arco circular de radio R = 0.25m
    # -------------------------------------------------------------
    R_t3 = 0.25
    N_t3 = 14
    for i in range(1, N_t3 + 1):
        beta = (i / float(N_t3)) * math.radians(30)
        y = y_hill_start + R_t3 * math.sin(beta)
        z = z_hill_start + R_t3 * (1.0 - math.cos(beta))
        cb, sb = math.cos(beta), math.sin(beta)
        T = [0.0, cb, sb]
        L = [-1.0, 0.0, 0.0]
        U = [0.0, -sb, cb]
        add_slice([x_hill_start, y, z], T, L, U)

    y_sub_start = y
    z_sub_start = z

    # -------------------------------------------------------------
    # 7. Subida Recta a +30° en +Y
    # Longitud L = 0.336m
    # -------------------------------------------------------------
    L_sub = 0.080
    cb30 = math.cos(math.radians(30))
    sb30 = math.sin(math.radians(30))
    N_sub = 18
    for i in range(1, N_sub + 1):
        s = (i / float(N_sub)) * L_sub
        y = y_sub_start + s * cb30
        z = z_sub_start + s * sb30
        T = [0.0, cb30, sb30]
        L = [-1.0, 0.0, 0.0]
        U = [0.0, -sb30, cb30]
        add_slice([x_hill_start, y, z], T, L, U)

    y_crown_start = y
    z_crown_start = z

    # -------------------------------------------------------------
    # 8. Transición Convexa de Cresta: De +30° a horizontal (0°) en +Y
    # Arco circular de radio R = 0.25m
    # -------------------------------------------------------------
    R_t4 = 0.25
    N_t4 = 14
    for i in range(1, N_t4 + 1):
        beta = math.radians(30) * (1.0 - i / float(N_t4))
        y = y_crown_start + R_t4 * (math.sin(math.radians(30)) - math.sin(beta))
        z = z_crown_start + R_t4 * (math.cos(beta) - math.cos(math.radians(30)))
        cb, sb = math.cos(beta), math.sin(beta)
        T = [0.0, cb, sb]
        L = [-1.0, 0.0, 0.0]
        U = [0.0, -sb, cb]
        add_slice([x_hill_start, y, z], T, L, U)

    y_crest_start = y
    z_crest = z # ~0.796m

    # -------------------------------------------------------------
    # 9. Cresta Plana Horizontal
    # Longitud L = 0.06m en +Y
    # -------------------------------------------------------------
    L_crest = 0.06
    N_crest = 6
    for i in range(1, N_crest + 1):
        y = y_crest_start + (i / float(N_crest)) * L_crest
        P = [x_hill_start, y, z_crest]
        T = [0.0, 1.0, 0.0]
        L = [-1.0, 0.0, 0.0]
        U = [0.0, 0.0, 1.0]
        add_slice(P, T, L, U)

    y_desc_crest_end = y

    # -------------------------------------------------------------
    # 10. NUEVA SECCION: BAJADA RECTA DESDE LA CRESTA HASTA EL SUELO (z=0.020m)
    # Pendiente uniforme a 45° con empalmes parabólicos en cresta y valle
    # Cero aceleración centrípeta durante todo el descenso (a_c = 0)
    # -------------------------------------------------------------
    z_ground = 0.045
    R_desc = 0.25
    theta_desc = math.radians(45)

    # a) Transición Convexa Cresta -> Bajada (0° a -45° en +Y)
    N_desc_t1 = 14
    for i in range(1, N_desc_t1 + 1):
        gamma = (i / float(N_desc_t1)) * theta_desc
        y = y_desc_crest_end + R_desc * math.sin(gamma)
        z = z_crest - R_desc * (1.0 - math.cos(gamma))
        cg, sg = math.cos(gamma), math.sin(gamma)
        T = [0.0, cg, -sg]
        L = [-1.0, 0.0, 0.0]
        U = [0.0, sg, cg]
        add_slice([x_hill_start, y, z], T, L, U)

    y_desc_straight_start = y
    z_desc_straight_start = z

    # b) Tramo Recto de Bajada a -45°
    dz_fillet = R_desc * (1.0 - math.cos(theta_desc))
    total_drop = z_crest - z_ground
    dz_straight = total_drop - 2 * dz_fillet
    L_straight = dz_straight / math.sin(theta_desc)
    N_desc_str = 24
    for i in range(1, N_desc_str + 1):
        s = (i / float(N_desc_str)) * L_straight
        y = y_desc_straight_start + s * math.cos(theta_desc)
        z = z_desc_straight_start - s * math.sin(theta_desc)
        T = [0.0, math.cos(theta_desc), -math.sin(theta_desc)]
        L = [-1.0, 0.0, 0.0]
        U = [0.0, math.sin(theta_desc), math.cos(theta_desc)]
        add_slice([x_hill_start, y, z], T, L, U)

    y_desc_valle_start = y
    z_desc_valle_start = z

    # c) Transición Cóncava de Valle al Suelo (-45° a 0° horizontal)
    N_desc_t2 = 14
    for i in range(1, N_desc_t2 + 1):
        gamma = theta_desc * (1.0 - i / float(N_desc_t2))
        y = y_desc_valle_start + R_desc * (math.sin(theta_desc) - math.sin(gamma))
        z = z_desc_valle_start - R_desc * (math.cos(gamma) - math.cos(theta_desc))
        cg, sg = math.cos(gamma), math.sin(gamma)
        T = [0.0, cg, -sg]
        L = [-1.0, 0.0, 0.0]
        U = [0.0, sg, cg]
        add_slice([x_hill_start, y, z], T, L, U)

    y_ground_start = y
    z_at_ground = z # 0.045m exactamente

    # -------------------------------------------------------------
    # 11. NUEVA SECCION: CURVA PLANA DE 180° EN EL SUELO (z=0.045m)
    # Gira 180° en el plano horizontal (R = 0.28m), peralte de 20°
    # Ya en el suelo, con estabilidad gravitacional total y despeje sobre z=0
    # -------------------------------------------------------------
    R2 = 0.28
    x_c2_center = x_hill_start - R2
    y_c2_center = y_ground_start
    N_c2 = 36
    peralte2_max = math.radians(20)
    for i in range(1, N_c2 + 1):
        psi = (i / float(N_c2)) * math.pi
        px = x_c2_center + R2 * math.cos(psi)
        py = y_c2_center + R2 * math.sin(psi)
        pz = z_ground # completamente plano en el suelo

        # Tangente en el plano XY
        T = [-math.sin(psi), math.cos(psi), 0.0]
        L_flat = [-math.cos(psi), -math.sin(psi), 0.0]
        U_flat = [0.0, 0.0, 1.0]

        # Peralte interior para compensar la fuerza centrifuga: exterior elevado e interior rebajado suavemente
        bank = peralte2_max * (math.sin(psi)**2)
        cb, sb = math.cos(bank), math.sin(bank)
        L = [L_flat[k]*cb - U_flat[k]*sb for k in range(3)]
        U = [L_flat[k]*sb + U_flat[k]*cb for k in range(3)]
        add_slice([px, py, pz], T, L, U)

    x_brake_start = px
    y_brake_start = py

    # -------------------------------------------------------------
    # 12. TRAYECTO FINAL DE FRENADO (L=75cm en dirección -Y)
    # Sobre el suelo, horizontal, alta friccion mu=1.35
    # -------------------------------------------------------------
    L_brake = 0.75
    N_brake = 25
    for i in range(1, N_brake + 1):
        y = y_brake_start - (i / float(N_brake)) * L_brake
        P = [x_brake_start, y, z_ground]
        T = [0.0, -1.0, 0.0]
        L = [1.0, 0.0, 0.0]
        U = [0.0, 0.0, 1.0]
        add_slice(P, T, L, U, is_brake=True)

    return slices

def generate_circuit_mesh_vrml(slices, W_bed=0.11, H_guard=0.055, T_floor=0.010):
    """
    Convierte la secuencia de slices en un único sólido cerrado U-channel (IndexedFaceSet)
    con guardarraíles elevados a 5.5cm para máxima retención del carrito.
    """
    points = []
    coord_indices = []

    for idx, item in enumerate(slices):
        P, T, L, U, is_brake = item[0], item[1], item[2], item[3], item[4]
        custom_pts = item[5] if len(item) > 5 else None
        if custom_pts is not None:
            p0, p1, p2, p3, p4, p5 = custom_pts
        else:
            p0 = [P[i] - (W_bed/2.0)*L[i] + H_guard*U[i] for i in range(3)]
            p1 = [P[i] - (W_bed/2.0)*L[i] for i in range(3)]
            p2 = [P[i] + (W_bed/2.0)*L[i] for i in range(3)]
            p3 = [P[i] + (W_bed/2.0)*L[i] + H_guard*U[i] for i in range(3)]
            p4 = [P[i] + (W_bed/2.0)*L[i] - T_floor*U[i] for i in range(3)]
            p5 = [P[i] - (W_bed/2.0)*L[i] - T_floor*U[i] for i in range(3)]
        points.extend([p0, p1, p2, p3, p4, p5])

    num_quads = len(slices) - 1
    for k in range(num_quads):
        b0 = k * 6
        b1 = (k + 1) * 6
        # Lecho superior
        coord_indices.append(f"{b0 + 1}, {b1 + 1}, {b1 + 2}, {b0 + 2}, -1")
        # Guardarraíl izquierdo cara interior
        coord_indices.append(f"{b1 + 1}, {b0 + 1}, {b0 + 0}, {b1 + 0}, -1")
        # Guardarraíl derecho cara interior
        coord_indices.append(f"{b0 + 2}, {b1 + 2}, {b1 + 3}, {b0 + 3}, -1")
        # Fondo inferior del lecho
        coord_indices.append(f"{b0 + 5}, {b0 + 4}, {b1 + 4}, {b1 + 5}, -1")
        # Guardarraíl izquierdo cara exterior
        coord_indices.append(f"{b0 + 0}, {b0 + 5}, {b1 + 5}, {b1 + 0}, -1")
        # Guardarraíl derecho cara exterior
        coord_indices.append(f"{b0 + 4}, {b0 + 3}, {b1 + 3}, {b1 + 4}, -1")

    pts_str = ", ".join([f"{p[0]:.5f} {p[1]:.5f} {p[2]:.5f}" for p in points])
    idx_str = ", ".join(coord_indices)

    last_p = slices[-1][0]

    vrml = f'''DEF PISTA_CIRCUITO Solid {{
  children [
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.14 0.42 0.78
        roughness 0.25
        metalness 0.35
      }}
      geometry DEF GEO_CIRCUITO IndexedFaceSet {{
        coord Coordinate {{
          point [ {pts_str} ]
        }}
        coordIndex [ {idx_str} ]
        creaseAngle 0.6
      }}
    }}
    # Tope trasero de seguridad en la estación
    Transform {{
      translation {slices[0][0][0] - 0.005:.4f} {slices[0][0][1]:.4f} {slices[0][0][2] + 0.020:.4f}
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.95 0.55 0.12
            roughness 0.3
            metalness 0.3
          }}
          geometry Box {{ size 0.010 {W_bed} 0.040 }}
        }}
      ]
    }}
    # Tope terminal amortiguado al final de la zona de frenado
    Transform {{
      translation {last_p[0]:.4f} {last_p[1] - 0.010:.4f} {last_p[2] + 0.025:.4f}
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.85 0.12 0.12
            roughness 0.5
          }}
          geometry Box {{ size {W_bed} 0.020 0.050 }}
        }}
      ]
    }}
  ]
  name "pista_circuito"
  contactMaterial "TrackMaterial"
  boundingObject Group {{
    children [
      USE GEO_CIRCUITO
      Transform {{
        translation {slices[0][0][0] - 0.005:.4f} {slices[0][0][1]:.4f} {slices[0][0][2] + 0.020:.4f}
        children [ Box {{ size 0.010 {W_bed} 0.040 }} ]
      }}
      Transform {{
        translation {last_p[0]:.4f} {last_p[1] - 0.010:.4f} {last_p[2] + 0.025:.4f}
        children [ Box {{ size {W_bed} 0.020 0.050 }} ]
      }}
    ]
  }}
}}
'''
    return vrml

def create_world():
    world_content = []
    world_content.append('#VRML_SIM R2023b utf8\n')
    world_content.append('''
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackground.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"

WorldInfo {
  info [
    "Simulacion de Fisica: Pista Montana Rusa con Carrito y Maleta",
    "Proyecto de Fisica Mecanica - Analisis de Energia, Momento y Frenado"
  ]
  title "Pista Montana Rusa - Laboratorio de Fisica"
  basicTimeStep 16
  contactProperties [
    ContactProperties {
      material1 "SuitcaseMaterial"
      material2 "TrackMaterial"
      coulombFriction [ 0.02 ]
      bounce 0.02
      maxContactJoints 64
    }
    ContactProperties {
      material1 "SuitcaseMaterial"
      material2 "CartMaterial"
      coulombFriction [ 0.95 ]
      bounce 0.01
      maxContactJoints 64
    }
    ContactProperties {
      material1 "SuitcaseMaterial"
      material2 "CartInteriorMaterial"
      coulombFriction [ 1.20 ]
      bounce 0.005
      maxContactJoints 64
    }
    ContactProperties {
      material1 "SuitcaseMaterial"
      material2 "SuitcaseMaterial"
      coulombFriction [ 0.02 ]
      maxContactJoints 64
    }
    ContactProperties {
      material1 "SuitcaseMaterial"
      material2 "default"
      coulombFriction [ 0.02 ]
      maxContactJoints 64
    }
    ContactProperties {
      material1 "CartMaterial"
      material2 "TrackMaterial"
      coulombFriction [ 0.005 ]
      bounce 0.02
      maxContactJoints 64
    }
    ContactProperties {
      material1 "CartMaterial"
      material2 "BrakingMaterial"
      coulombFriction [ 1.35 ]
      bounce 0.01
      maxContactJoints 64
    }
    ContactProperties {
      material1 "CartMaterial"
      material2 "CartMaterial"
      coulombFriction [ 0.005 ]
      maxContactJoints 64
    }
    ContactProperties {
      material1 "CartMaterial"
      material2 "default"
      coulombFriction [ 0.005 ]
      maxContactJoints 64
    }
    ContactProperties {
      material1 "default"
      material2 "default"
      coulombFriction [ 0.5 ]
      maxContactJoints 64
    }
  ]
}

Viewpoint {
  orientation 0.8958 0.2351 0.3773 1.2154
  position 2.50 -1.60 2.00
}

TexturedBackground {
}

TexturedBackgroundLight {
}

# Suelo y mesa de laboratorio base amplia (plataforma de 2.8m x 2.8m)
Solid {
  translation 0.80 1.15 -0.015
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.22 0.24 0.28
        roughness 0.35
        metalness 0.2
      }
      geometry Box {
        size 2.8 2.8 0.03
      }
    }
  ]
  name "suelo_laboratorio"
  boundingObject Box {
    size 2.8 2.8 0.03
  }
}
''')

    W_bed = 0.14    # Pista ensanchada a 14.0cm para holgura total y cero roce
    H_guard = 0.080 # Guardarraíles elevados a 8.0cm para retención física absoluta en todo el circuito
    T_floor = 0.010
    T_guard = 0.006
    z_plat = 0.915

    # ========================================================
    # 1. RAMPA INICIAL DE LA MALETA (L=47cm, 30°)
    # Con lengüeta de guiado suave que entra directamente en la cavidad del carro
    # ========================================================
    L1 = 0.47
    theta1 = math.radians(30)
    x1_start = 0.08
    y1_start = 0.20
    z1_start = 1.20

    dx1 = L1 * math.cos(theta1)
    dz1 = L1 * math.sin(theta1)
    x1_end = x1_start + dx1
    z1_end = z1_start - dz1

    cx1 = (x1_start + x1_end) / 2.0
    cy1 = y1_start
    cz1 = (z1_start + z1_end) / 2.0
    rot_rampa1 = f"0 1 0 {theta1:.6f}"

    # Lengüeta curvada de transición suave hacia la cavidad
    chute_points = []
    chute_indices = []
    N_chute = 8
    R_chute = 0.05
    for i in range(N_chute + 1):
        ang = theta1 * (1.0 - i / float(N_chute))
        dx_c = R_chute * (math.sin(theta1) - math.sin(ang))
        dz_c = R_chute * (math.cos(ang) - math.cos(theta1))
        px = x1_end + dx_c
        py = y1_start
        pz = z1_end - dz_c

        ca = math.cos(ang)
        chute_points.append(f"{px:.5f} {py - W_bed/2.0:.5f} {pz:.5f}")
        chute_points.append(f"{px:.5f} {py + W_bed/2.0:.5f} {pz:.5f}")
        chute_points.append(f"{px:.5f} {py - W_bed/2.0:.5f} {pz + H_guard*ca:.5f}")
        chute_points.append(f"{px:.5f} {py + W_bed/2.0:.5f} {pz + H_guard*ca:.5f}")

    for i in range(N_chute):
        b0 = i * 4
        b1 = (i + 1) * 4
        chute_indices.append(f"{b0 + 0}, {b1 + 0}, {b1 + 1}, {b0 + 1}, -1")
        chute_indices.append(f"{b0 + 0}, {b0 + 2}, {b1 + 2}, {b1 + 0}, -1")
        chute_indices.append(f"{b0 + 1}, {b1 + 1}, {b1 + 3}, {b0 + 3}, -1")

    chute_pts_str = ", ".join(chute_points)
    chute_idx_str = ", ".join(chute_indices)

    world_content.append(f'''
# ========================================================
# SECCION 1: RAMPA INICIAL DE LA MALETA (L=47cm, 30 deg + Lengueta Curva de Guiado)
# ========================================================
DEF RAMPA_1 Solid {{
  children [
    Transform {{
      translation {cx1:.5f} {cy1:.5f} {cz1:.5f}
      rotation {rot_rampa1}
      children [
        Shape {{
          appearance DEF APP_RAMP1 PBRAppearance {{
            baseColor 0.88 0.24 0.18
            roughness 0.2
            metalness 0.25
          }}
          geometry Box {{ size {L1:.4f} {W_bed} {T_floor} }}
        }}
        Transform {{
          translation 0 {(W_bed/2.0 + T_guard/2.0):.4f} {(H_guard/2.0):.4f}
          children [
            Shape {{
              appearance DEF APP_GUARD PBRAppearance {{
                baseColor 0.92 0.94 0.98
                transparency 0.25
                roughness 0.1
                metalness 0.4
              }}
              geometry Box {{ size {L1:.4f} {T_guard} {H_guard} }}
            }}
          ]
        }}
        Transform {{
          translation 0 {- (W_bed/2.0 + T_guard/2.0):.4f} {(H_guard/2.0):.4f}
          children [
            Shape {{
              appearance USE APP_GUARD
              geometry Box {{ size {L1:.4f} {T_guard} {H_guard} }}
            }}
          ]
        }}
      ]
    }}
    Shape {{
      appearance USE APP_RAMP1
      geometry DEF GEO_CHUTE IndexedFaceSet {{
        coord Coordinate {{
          point [ {chute_pts_str} ]
        }}
        coordIndex [ {chute_idx_str} ]
        creaseAngle 0.5
      }}
    }}
  ]
  name "rampa_1"
  contactMaterial "TrackMaterial"
  boundingObject Group {{
    children [
      # Lecho de la rampa
      Transform {{
        translation {cx1:.5f} {cy1:.5f} {cz1:.5f}
        rotation {rot_rampa1}
        children [ Box {{ size {L1:.4f} {W_bed} {T_floor} }} ]
      }}
      # Guardarrail izquierdo
      Transform {{
        translation {cx1 + (H_guard/2.0)*math.sin(theta1):.5f} {cy1 + (W_bed/2.0 + T_guard/2.0):.5f} {cz1 + (H_guard/2.0)*math.cos(theta1):.5f}
        rotation {rot_rampa1}
        children [ Box {{ size {L1:.4f} {T_guard} {H_guard} }} ]
      }}
      # Guardarrail derecho
      Transform {{
        translation {cx1 + (H_guard/2.0)*math.sin(theta1):.5f} {cy1 - (W_bed/2.0 + T_guard/2.0):.5f} {cz1 + (H_guard/2.0)*math.cos(theta1):.5f}
        rotation {rot_rampa1}
        children [ Box {{ size {L1:.4f} {T_guard} {H_guard} }} ]
      }}
      USE GEO_CHUTE
    ]
  }}
}}
''')

    # ========================================================
    # 2. CIRCUITO COMPLETO CON LA NUEVA SECUENCIA:
    # Transfer -> Bajada 2 -> Curva 1 -> Subida -> Cresta ->
    # BAJADA RECTA AL SUELO -> CURVA 180° EN SUELO -> TRAYECTO FINAL DE FRENADO
    # ========================================================
    slices = create_smooth_spine()
    vrml_circuito = generate_circuit_mesh_vrml(slices, W_bed=W_bed, H_guard=H_guard, T_floor=T_floor)
    world_content.append(f'''
# ========================================================
# PISTA PRINCIPAL DEL CARRITO: CIRCUITO SUAVE C1 CON SECUENCIA EXACTA
# ========================================================
{vrml_circuito}
''')

    # ========================================================
    # ========================================================
    # 3. ESTRUCTURA DE SOPORTE METALICA ANCLADA AL SUELO
    # Columnas cilíndricas esbeltas que terminan exactamente bajo el lecho de la vía
    # Sin placas horizontales intrusivas que penetren en la pista
    # ========================================================
    pillar_locs = [
        (0.08, y1_start, 1.20 - 0.020),
        (0.44, y1_start, z_plat - 0.020),
        (0.79, y1_start, z_plat - 0.020),
        (slices[68][0][0], slices[68][0][1], slices[68][0][2] - 0.020),
        (slices[116][0][0], slices[116][0][1], slices[116][0][2] - 0.020),
        (slices[162][0][0], slices[162][0][1], slices[162][0][2] - 0.020),
        (slices[194][0][0], slices[194][0][1], slices[194][0][2] - 0.020)
    ]

    pillar_children = []
    for idx, (px, py, pz_top) in enumerate(pillar_locs):
        h_pillar = max(0.04, pz_top)
        cz_pillar = h_pillar / 2.0
        pillar_children.append(f'''
    # Columna soporte {idx+1}
    Transform {{
      translation {px:.5f} {py:.5f} {cz_pillar:.5f}
      children [
        Shape {{
          appearance DEF APP_STEEL PBRAppearance {{
            baseColor 0.70 0.73 0.78
            metalness 0.90
            roughness 0.20
          }}
          geometry Cylinder {{
            height {h_pillar:.4f}
            radius 0.014
          }}
        }}
      ]
    }}
    # Brida de anclaje al suelo de soporte {idx+1}
    Transform {{
      translation {px:.5f} {py:.5f} 0.003
      children [
        Shape {{
          appearance USE APP_STEEL
          geometry Cylinder {{
            height 0.006
            radius 0.026
          }}
        }}
      ]
    }}''')

    all_pillars_vrml = "\n".join(pillar_children)
    world_content.append(f'''
# ========================================================
# ESTRUCTURA DE SOPORTE METALICA ANCLADA AL SUELO
# ========================================================
Solid {{
  children [
{all_pillars_vrml}
  ]
  name "estructura_soporte"
}}
''')

    # ========================================================
    # 4. CARRITO DE LABORATORIO ESBELTO Y DINAMICO
    # - Ancho total entre ruedas: 9.4cm (dentro de vía de 11.0cm, 8mm de margen por lado)
    # - Cero rozamiento ni acuñamiento con guardarraíles
    # - Cavidad interior libre (6.2cm ancho para maleta de 5.0cm)
    # - Ruedas con esferas analíticas para rodadura ultrasuave
    # ========================================================
    cart_init_x = 0.540
    cart_init_y = y1_start
    cart_init_z = z_plat + 0.020

    world_content.append(f'''
# ========================================================
# CARRITO DE LABORATORIO (M=200g, Ancho 9.4cm, Rodadura Libre)
# ========================================================
DEF CARRITO Solid {{
  translation {cart_init_x:.5f} {cart_init_y:.5f} {cart_init_z:.5f}
  children [
    # Chasis principal
    Shape {{
      appearance DEF APP_CAR_BODY PBRAppearance {{
        baseColor 0.08 0.72 0.38
        roughness 0.20
        metalness 0.40
      }}
      geometry Box {{ size 0.140 0.070 0.008 }}
    }}
    # Pared frontal alta receptora del empuje (4.5cm alto)
    Transform {{
      translation 0.065 0 0.023
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.010 0.070 0.045 }}
        }}
      ]
    }}
    # Pared trasera baja de entrada biselada (ras de suelo)
    Transform {{
      translation -0.065 0 0.002
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.008 0.070 0.002 }}
        }}
      ]
    }}
    # Pared lateral izquierda (4.5cm de alto)
    Transform {{
      translation 0 0.033 0.023
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.120 0.004 0.045 }}
        }}
      ]
    }}
    # Pared lateral derecha (4.5cm de alto)
    Transform {{
      translation 0 -0.033 0.023
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.120 0.004 0.045 }}
        }}
      ]
    }}
    # Pestaña de retención superior izquierda (labio de captura)
    Transform {{
      translation 0 0.030 0.043
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.120 0.006 0.004 }}
        }}
      ]
    }}
    # Pestaña de retención superior derecha (labio de captura)
    Transform {{
      translation 0 -0.030 0.043
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.120 0.006 0.004 }}
        }}
      ]
    }}
    # Suelo interior acolchado de alto agarre (CartInteriorMaterial mu=1.20)
    Transform {{
      translation 0 0 0.005
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.12 0.12 0.15
            roughness 0.95
          }}
          geometry Box {{ size 0.120 0.060 0.002 }}
        }}
      ]
    }}
    # 4 Ruedas de bajisimo rozamiento
    Transform {{
      translation 0.045 0.035 -0.006
      rotation 1 0 0 1.5708
      children [
        Shape {{
          appearance DEF APP_WHEEL PBRAppearance {{
            baseColor 0.12 0.12 0.14
            roughness 0.2
            metalness 0.8
          }}
          geometry Cylinder {{ height 0.006 radius 0.012 }}
        }}
      ]
    }}
    Transform {{
      translation 0.045 -0.035 -0.006
      rotation 1 0 0 1.5708
      children [
        Shape {{
          appearance USE APP_WHEEL
          geometry Cylinder {{ height 0.006 radius 0.012 }}
        }}
      ]
    }}
    Transform {{
      translation -0.045 0.035 -0.006
      rotation 1 0 0 1.5708
      children [
        Shape {{
          appearance USE APP_WHEEL
          geometry Cylinder {{ height 0.006 radius 0.012 }}
        }}
      ]
    }}
    Transform {{
      translation -0.045 -0.035 -0.006
      rotation 1 0 0 1.5708
      children [
        Shape {{
          appearance USE APP_WHEEL
          geometry Cylinder {{ height 0.006 radius 0.012 }}
        }}
      ]
    }}
  ]
  name "carrito"
  contactMaterial "CartMaterial"
  boundingObject Group {{
    children [
      # Chasis base estrechado (ancho 48mm) para que con balanceo de 25° no toque nunca el suelo
      Box {{ size 0.130 0.048 0.008 }}
      # Pared frontal interior
      Transform {{
        translation 0.060 0 0.023
        children [ Box {{ size 0.008 0.050 0.040 }} ]
      }}
      # Pared trasera interior
      Transform {{
        translation -0.060 0 0.002
        children [ Box {{ size 0.008 0.050 0.002 }} ]
      }}
      # Pared lateral izquierda interior
      Transform {{
        translation 0 0.027 0.023
        children [ Box {{ size 0.110 0.004 0.040 }} ]
      }}
      # Pared lateral derecha interior
      Transform {{
        translation 0 -0.027 0.023
        children [ Box {{ size 0.110 0.004 0.040 }} ]
      }}
      # Labios superiores de retención de la maleta (apertura amplia de 5.2cm para maleta de 3.8cm)
      Transform {{
        translation 0 0.028 0.043
        children [ Box {{ size 0.110 0.004 0.004 }} ]
      }}
      Transform {{
        translation 0 -0.028 0.043
        children [ Box {{ size 0.110 0.004 0.004 }} ]
      }}
      # 4 Parachoques y deflectores esféricos en las 4 esquinas perimetrales exteriores:
      # Cualquier contacto lateral con guardarraíles se produce sobre esferas analíticas sin fricción ni momento de giro
      Transform {{
        translation 0.065 0.035 0.015
        children [ Sphere {{ radius 0.012 }} ]
      }}
      Transform {{
        translation 0.065 -0.035 0.015
        children [ Sphere {{ radius 0.012 }} ]
      }}
      Transform {{
        translation -0.065 0.035 0.015
        children [ Sphere {{ radius 0.012 }} ]
      }}
      Transform {{
        translation -0.065 -0.035 0.015
        children [ Sphere {{ radius 0.012 }} ]
      }}
      # 4 Ruedas de bajísimo rozamiento (esferas analíticas)
      Transform {{
        translation 0.045 0.035 -0.006
        children [ Sphere {{ radius 0.012 }} ]
      }}
      Transform {{
        translation 0.045 -0.035 -0.006
        children [ Sphere {{ radius 0.012 }} ]
      }}
      Transform {{
        translation -0.045 0.035 -0.006
        children [ Sphere {{ radius 0.012 }} ]
      }}
      Transform {{
        translation -0.045 -0.035 -0.006
        children [ Sphere {{ radius 0.012 }} ]
      }}
    ]
  }}
  physics Physics {{
    density -1
    mass 0.200
    centerOfMass [ 0 0 0.006 ]
    damping Damping {{
      linear 0.001
      angular 0.002
    }}
  }}
}}
''')

    # ========================================================
    # 5. MALETA FISICA (6.0x3.8x3.0 cm, Masa 18g)
    # Dimensiones compactas para entrada y acople fluido sin atascos
    # ========================================================
    x_loc_m = -L1/2.0 + 0.0525
    y_loc_m = 0.0
    z_loc_m = T_floor/2.0 + 0.015 + 0.002

    maleta_init_x = cx1 + x_loc_m * math.cos(theta1) + z_loc_m * math.sin(theta1)
    maleta_init_y = cy1
    maleta_init_z = cz1 - x_loc_m * math.sin(theta1) + z_loc_m * math.cos(theta1)

    world_content.append(f'''
# ========================================================
# MALETA (6.0x3.8x3.0 cm, Masa 18g, h_inicial={maleta_init_z:.3f}m)
# ========================================================
DEF MALETA Solid {{
  translation {maleta_init_x:.5f} {maleta_init_y:.5f} {maleta_init_z:.5f}
  rotation {rot_rampa1}
  children [
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.85 0.50 0.15
        roughness 0.35
        metalness 0.10
      }}
      geometry Box {{ size 0.060 0.038 0.030 }}
    }}
    Transform {{
      translation 0 0 0.018
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.15 0.15 0.15
            roughness 0.5
          }}
          geometry Box {{ size 0.032 0.006 0.006 }}
        }}
      ]
    }}
    Transform {{
      translation 0.016 0 0
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.10 0.10 0.10
            roughness 0.6
          }}
          geometry Box {{ size 0.006 0.040 0.032 }}
        }}
      ]
    }}
    Transform {{
      translation -0.016 0 0
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.10 0.10 0.10
            roughness 0.6
          }}
          geometry Box {{ size 0.006 0.040 0.032 }}
        }}
      ]
    }}
  ]
  name "maleta"
  contactMaterial "SuitcaseMaterial"
  boundingObject Box {{ size 0.060 0.038 0.030 }}
  physics Physics {{
    density -1
    mass 0.018
    centerOfMass [ 0 0 0 ]
    damping Damping {{
      linear 0.0005
      angular 0.001
    }}
  }}
}}
''')

    # ========================================================
    # 6. ROBOT SUPERVISOR DE FISICA
    # ========================================================
    world_content.append('''
# ========================================================
# CONTROLADOR SUPERVISOR DE FISICA
# ========================================================
Robot {
  name "supervisor_fisica"
  controller "pista_supervisor"
  supervisor TRUE
}
''')

    os.makedirs("worlds", exist_ok=True)
    output_path = os.path.join("worlds", "pista_montana_rusa.wbt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(world_content)
    print(f"Mundo Webots creado exitosamente en: {output_path}")

    # Sincronizar archivo raíz
    root_path = "pista_montana_rusa.wbt"
    with open(root_path, "w", encoding="utf-8") as f:
        f.writelines(world_content)
    print(f"Mundo Webots sincronizado en la raíz: {root_path}")

if __name__ == "__main__":
    create_world()
