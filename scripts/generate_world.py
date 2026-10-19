"""
Generador del Mundo Webots para la Pista tipo Montaña Rusa de Laboratorio.
Cumple estrictamente con todas las especificaciones:
- Rampa inicial: L=47cm, 30 grados, inicio a h=1.20m.
- Maleta: 7.5 x 5 x 4 cm, masa 18g (con soporte de peso extra).
- Estación de transferencia: 5cm debajo del final de la rampa 1.
- Carrito: 17 x 9 x 4.5 cm, cavidad interior 14 x 6 cm, masa 200g.
- Bajada 2: L=50cm, 45 grados.
- Curva 1: 90 grados, radio 10cm, peralte 30 grados.
- Subida: L=47cm, 30 grados.
- Tramo plano cresta: L=10cm.
- Bajada 3 y Curva 2: 180 grados, radio 18cm, descenso al suelo.
- Tramo final de frenado: L=75cm sobre el suelo con alta fricción.
- Supervisor en Python con telemetría HUD y cálculo de física.
"""

import math
import os

def create_world():
    world_content = []
    world_content.append('#VRML_SIM R2023b utf8\n')
    world_content.append('''
WorldInfo {
  info [
    "Simulacion de Fisica: Pista Montana Rusa con Carrito y Maleta",
    "Proyecto de Fisica Mecanica - Analisis de Energia, Momento y Frenado"
  ]
  title "Pista Montana Rusa - Laboratorio de Fisica"
  ERP 0.6
  basicTimeStep 4
  coordinateSystem "ENU"
  contactProperties [
    ContactProperties {
      material1 "CartWheelMaterial"
      material2 "TrackMaterial"
      coulombFriction [ 0.005 ]
    }
    ContactProperties {
      material1 "CartWheelMaterial"
      material2 "BrakingTrackMaterial"
      coulombFriction [ 1.35 ]
    }
    ContactProperties {
      material1 "SuitcaseMaterial"
      material2 "RampMaterial"
      coulombFriction [ 0.02 ]
    }
    ContactProperties {
      material1 "SuitcaseMaterial"
      material2 "CartInteriorMaterial"
      coulombFriction [ 0.70 ]
      bounce 0.02
    }
    ContactProperties {
      material1 "CartBodyMaterial"
      material2 "TrackMaterial"
      coulombFriction [ 0.01 ]
    }
  ]
}

Viewpoint {
  orientation 0.280985 0.351231 0.893132 4.35
  position 2.50 -1.40 2.20
  near 0.05
}

Background {
  skyColor [
    0.15 0.18 0.25
  ]
}

DirectionalLight {
  ambientIntensity 0.4
  direction -0.4 0.3 -0.8
  intensity 1.4
  castShadows TRUE
}

# Suelo de laboratorio base (plataforma de 2.5m x 2.5m)
Solid {
  translation 0.65 0.45 -0.01
  children [
    Shape {
      appearance PBRAppearance {
        baseColor 0.22 0.24 0.28
        roughness 0.4
        metalness 0.1
      }
      geometry Box {
        size 2.5 2.5 0.02
      }
    }
  ]
  name "suelo_laboratorio"
  boundingObject Box {
    size 2.5 2.5 0.02
  }
}
''')

    # Geometria exacta de la pista
    # Ancho del lecho: 0.11 m
    # Altura guardarrail: 0.035 m
    # Espesor lecho: 0.01 m
    
    # 1. Rampa 1: Maleta
    # Start: (0.10, 0.20, 1.20)
    # L = 0.47m, theta = -30 deg en X
    L1 = 0.47
    theta1 = math.radians(30)
    dx1 = L1 * math.cos(theta1)
    dz1 = L1 * math.sin(theta1)
    x1_start = 0.10
    y1_start = 0.20
    z1_start = 1.20
    x1_end = x1_start + dx1
    y1_end = y1_start
    z1_end = z1_start - dz1
    
    # Centro de la rampa 1
    cx1 = (x1_start + x1_end) / 2.0
    cy1 = y1_start
    cz1 = (z1_start + z1_end) / 2.0
    
    # Rotacion de rampa 1: rotada alrededor de eje Y por +30 grados (baja en +X)
    rot_rampa1 = f"0 1 0 {theta1:.6f}"
    
    world_content.append(f'''
# ========================================================
# SECCION 1: RAMPA INICIAL DE LA MALETA (L=47cm, 30 deg)
# ========================================================
DEF RAMPA_1 Solid {{
  translation {cx1:.5f} {cy1:.5f} {cz1:.5f}
  rotation {rot_rampa1}
  children [
    # Lecho de la rampa
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.85 0.20 0.20
        roughness 0.15
        metalness 0.2
      }}
      geometry DEF BOX_LECHO_R1 Box {{
        size {L1:.4f} 0.10 0.01
      }}
    }}
    # Guardarrail Izquierdo
    Transform {{
      translation 0 0.052 0.02
      children [
        Shape {{
          appearance DEF APP_GUARD PBRAppearance {{
            baseColor 0.9 0.9 0.95
            transparency 0.35
            roughness 0.1
            metalness 0.3
          }}
          geometry DEF BOX_GUARD_R1 Box {{
            size {L1:.4f} 0.005 0.035
          }}
        }}
      ]
    }}
    # Guardarrail Derecho
    Transform {{
      translation 0 -0.052 0.02
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry USE BOX_GUARD_R1
        }}
      ]
    }}
    # Soporte vertical inicio (h=1.20m)
    Transform {{
      translation -{L1/2:.4f} 0 -{cz1/2:.4f}
      rotation 0 1 0 -{theta1:.6f}
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.4 0.45 0.5
            metalness 0.8
            roughness 0.3
          }}
          geometry Cylinder {{
            height {z1_start:.4f}
            radius 0.02
          }}
        }}
      ]
    }}
  ]
  name "rampa_1"
  contactMaterial "RampMaterial"
  boundingObject Group {{
    children [
      USE BOX_LECHO_R1
      Transform {{
        translation 0 0.052 0.02
        children [ USE BOX_GUARD_R1 ]
      }}
      Transform {{
        translation 0 -0.052 0.02
        children [ USE BOX_GUARD_R1 ]
      }}
    ]
  }}
}}
''')

    # 2. ESTACION DE TRANSFERENCIA
    # Ubicada 5cm debajo del final de la rampa 1:
    # z_transf = z1_end - 0.05 = 0.965 - 0.05 = 0.915m
    # Largo de la plataforma = 0.24m (de x=0.507 a x=0.747)
    z_transf = z1_end - 0.05
    L_transf = 0.24
    cx_transf = x1_end + L_transf / 2.0
    cy_transf = y1_start
    cz_transf = z_transf
    
    world_content.append(f'''
# ========================================================
# SECCION 2: ESTACION DE TRANSFERENCIA (Caida 5cm)
# ========================================================
DEF ESTACION_TRANSFERENCIA Solid {{
  translation {cx_transf:.5f} {cy_transf:.5f} {cz_transf:.5f}
  children [
    # Lecho horizontal
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.15 0.45 0.85
        roughness 0.2
        metalness 0.3
      }}
      geometry DEF BOX_LECHO_TRANSF Box {{
        size {L_transf:.4f} 0.11 0.01
      }}
    }}
    # Guardarrail Izquierdo
    Transform {{
      translation 0 0.057 0.02
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry DEF BOX_GUARD_TRANSF Box {{
            size {L_transf:.4f} 0.005 0.035
          }}
        }}
      ]
    }}
    # Guardarrail Derecho
    Transform {{
      translation 0 -0.057 0.02
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry USE BOX_GUARD_TRANSF
        }}
      ]
    }}
    # Tope posterior para el carrito (evita que retroceda)
    Transform {{
      translation -{L_transf/2 - 0.005:.4f} 0 0.025
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.95 0.6 0.1
            roughness 0.3
          }}
          geometry Box {{
            size 0.01 0.11 0.04
          }}
        }}
      ]
    }}
    # Soporte vertical de la estacion
    Transform {{
      translation 0 0 -{cz_transf/2:.4f}
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.4 0.45 0.5
            metalness 0.8
            roughness 0.3
          }}
          geometry Cylinder {{
            height {cz_transf:.4f}
            radius 0.02
          }}
        }}
      ]
    }}
  ]
  name "estacion_transferencia"
  contactMaterial "TrackMaterial"
  boundingObject Group {{
    children [
      USE BOX_LECHO_TRANSF
      Transform {{
        translation 0 0.057 0.02
        children [ USE BOX_GUARD_TRANSF ]
      }}
      Transform {{
        translation 0 -0.057 0.02
        children [ USE BOX_GUARD_TRANSF ]
      }}
      Transform {{
        translation -{L_transf/2 - 0.005:.4f} 0 0.025
        children [
          Box {{ size 0.01 0.11 0.04 }}
        ]
      }}
    ]
  }}
}}
''')

    # 3. BAJADA 2: L=50cm, 45 grados hacia abajo
    L2 = 0.50
    theta2 = math.radians(45)
    dx2 = L2 * math.cos(theta2)
    dz2 = L2 * math.sin(theta2)
    x2_start = x1_end + L_transf
    y2_start = y1_start
    z2_start = z_transf
    x2_end = x2_start + dx2
    y2_end = y2_start
    z2_end = z2_start - dz2
    
    cx2 = (x2_start + x2_end) / 2.0
    cy2 = y2_start
    cz2 = (z2_start + z2_end) / 2.0
    rot_bajada2 = f"0 1 0 {theta2:.6f}"
    
    world_content.append(f'''
# ========================================================
# SECCION 3: BAJADA 2 (L=50cm, 45 deg)
# ========================================================
DEF BAJADA_2 Solid {{
  translation {cx2:.5f} {cy2:.5f} {cz2:.5f}
  rotation {rot_bajada2}
  children [
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.15 0.45 0.85
        roughness 0.2
        metalness 0.3
      }}
      geometry DEF BOX_LECHO_B2 Box {{
        size {L2:.4f} 0.11 0.01
      }}
    }}
    Transform {{
      translation 0 0.057 0.022
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry DEF BOX_GUARD_B2 Box {{
            size {L2:.4f} 0.005 0.04
          }}
        }}
      ]
    }}
    Transform {{
      translation 0 -0.057 0.022
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry DEF BOX_GUARD_B2
        }}
      ]
    }}
  ]
  name "bajada_2"
  contactMaterial "TrackMaterial"
  boundingObject Group {{
    children [
      USE BOX_LECHO_B2
      Transform {{
        translation 0 0.057 0.022
        children [ USE BOX_GUARD_B2 ]
      }}
      Transform {{
        translation 0 -0.057 0.022
        children [ USE BOX_GUARD_B2 ]
      }}
    ]
  }}
}}
''')

    # 4. CURVA PERALTADA 1 (90 deg, R=10cm, peralte=30 deg)
    # Gira de direccion +X a +Y.
    # Centro de giro: (x2_end, y2_end + R1) = (x2_end, y2_start + 0.10)
    R1 = 0.10
    x_c1 = x2_end
    y_c1 = y2_start + R1
    z_c1 = z2_end
    num_seg_c1 = 12
    peralte_rad = math.radians(30)
    
    world_content.append(f'''
# ========================================================
# SECCION 4: CURVA PERALTADA 1 (90 deg, R=10cm, Peralte 30 deg)
# ========================================================
DEF CURVA_1 Solid {{
  children [
''')
    # Generar segmentos discretos de la curva 1
    phi_start = -math.pi / 2.0
    phi_end = 0.0
    d_phi = (phi_end - phi_start) / num_seg_c1
    arc_seg_len = R1 * d_phi * 1.05
    
    curva1_bounds = []
    for i in range(num_seg_c1):
        phi_mid = phi_start + (i + 0.5) * d_phi
        px = x_c1 + R1 * math.cos(phi_mid)
        py = y_c1 + R1 * math.sin(phi_mid)
        pz = z_c1
        tangent_angle = phi_mid + math.pi / 2.0
        
        cos_t = math.cos(tangent_angle)
        sin_t = math.sin(tangent_angle)
        
        cp = math.cos(peralte_rad)
        sp = math.sin(peralte_rad)
        
        tr = cos_t + cos_t * cp + cp
        angle = math.acos(max(-1.0, min(1.0, (tr - 1.0) / 2.0)))
        if math.isclose(angle, 0.0, abs_tol=1e-5):
            axis_x, axis_y, axis_z = 0, 0, 1
        else:
            denom = 2.0 * math.sin(angle)
            axis_x = (sp - (-cos_t * sp)) / denom
            axis_y = (sin_t * sp - 0) / denom
            axis_z = (sin_t - (-sin_t * cp)) / denom
            norm_a = math.sqrt(axis_x**2 + axis_y**2 + axis_z**2)
            axis_x /= norm_a
            axis_y /= norm_a
            axis_z /= norm_a
            
        world_content.append(f'''    Transform {{
      translation {px:.5f} {py:.5f} {pz:.5f}
      rotation {axis_x:.5f} {axis_y:.5f} {axis_z:.5f} {angle:.5f}
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.15 0.45 0.85
            roughness 0.2
            metalness 0.3
          }}
          geometry DEF BOX_C1_{i} Box {{
            size {arc_seg_len:.4f} 0.11 0.01
          }}
        }}
        Transform {{
          translation 0 0.057 0.025
          children [
            Shape {{
              appearance USE APP_GUARD
              geometry DEF BOX_G1_{i} Box {{
                size {arc_seg_len:.4f} 0.005 0.045
              }}
            }}
          ]
        }}
        Transform {{
          translation 0 -0.057 0.025
          children [
            Shape {{
              appearance USE APP_GUARD
              geometry USE BOX_G1_{i}
            }}
          ]
        }}
      ]
    }}
''')
        curva1_bounds.append((px, py, pz, axis_x, axis_y, axis_z, angle, f"BOX_C1_{i}", f"BOX_G1_{i}"))

    world_content.append(f'''  ]
  name "curva_1"
  contactMaterial "TrackMaterial"
  boundingObject Group {{
    children [
''')
    for px, py, pz, ax, ay, az, ang, b_lecho, b_guard in curva1_bounds:
        world_content.append(f'''      Transform {{
        translation {px:.5f} {py:.5f} {pz:.5f}
        rotation {ax:.5f} {ay:.5f} {az:.5f} {ang:.5f}
        children [
          USE {b_lecho}
          Transform {{
            translation 0 0.057 0.025
            children [ USE {b_guard} ]
          }}
          Transform {{
            translation 0 -0.057 0.025
            children [ USE {b_guard} ]
          }}
        ]
      }}
''')
    world_content.append('''    ]
  }
}
''')

    # 5. SUBIDA: L=47cm, 30 deg hacia arriba en direccion +Y
    L3 = 0.47
    theta3 = math.radians(30)
    dy3 = L3 * math.cos(theta3)
    dz3 = L3 * math.sin(theta3)
    x3_start = x_c1 + R1
    y3_start = y_c1
    z3_start = z_c1
    x3_end = x3_start
    y3_end = y3_start + dy3
    z3_end = z3_start + dz3
    
    cx3 = x3_start
    cy3 = (y3_start + y3_end) / 2.0
    cz3 = (z3_start + z3_end) / 2.0
    
    rot_subida = f"1 0 0 -{theta3:.6f}"
    
    world_content.append(f'''
# ========================================================
# SECCION 5: SUBIDA (L=47cm, 30 deg hacia arriba en +Y)
# ========================================================
DEF SUBIDA Solid {{
  translation {cx3:.5f} {cy3:.5f} {cz3:.5f}
  rotation {rot_subida}
  children [
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.15 0.45 0.85
        roughness 0.2
        metalness 0.3
      }}
      geometry DEF BOX_LECHO_S Box {{
        size 0.11 {L3:.4f} 0.01
      }}
    }}
    Transform {{
      translation 0.057 0 0.022
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry DEF BOX_GUARD_S Box {{
            size 0.005 {L3:.4f} 0.04
          }}
        }}
      ]
    }}
    Transform {{
      translation -0.057 0 0.022
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry USE BOX_GUARD_S
        }}
      ]
    }}
    # Soporte central subida
    Transform {{
      translation 0 0 -{cz3/2:.4f}
      rotation 1 0 0 {theta3:.6f}
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.4 0.45 0.5
            metalness 0.8
            roughness 0.3
          }}
          geometry Cylinder {{
            height {cz3:.4f}
            radius 0.02
          }}
        }}
      ]
    }}
  ]
  name "subida"
  contactMaterial "TrackMaterial"
  boundingObject Group {{
    children [
      USE BOX_LECHO_S
      Transform {{
        translation 0.057 0 0.022
        children [ USE BOX_GUARD_S ]
      }}
      Transform {{
        translation -0.057 0 0.022
        children [ USE BOX_GUARD_S ]
      }}
    ]
  }}
}}
''')

    # 6. TRAMO RECTO HORIZONTAL (Cresta) L=10cm
    L4 = 0.10
    x4_start = x3_end
    y4_start = y3_end
    z4_start = z3_end
    x4_end = x4_start
    y4_end = y4_start + L4
    z4_end = z4_start
    
    cx4 = x4_start
    cy4 = (y4_start + y4_end) / 2.0
    cz4 = z4_start
    
    world_content.append(f'''
# ========================================================
# SECCION 6: CRESTA RECTA HORIZONTAL (L=10cm)
# ========================================================
DEF CRESTA Solid {{
  translation {cx4:.5f} {cy4:.5f} {cz4:.5f}
  children [
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.15 0.45 0.85
        roughness 0.2
        metalness 0.3
      }}
      geometry DEF BOX_LECHO_C Box {{
        size 0.11 {L4:.4f} 0.01
      }}
    }}
    Transform {{
      translation 0.057 0 0.022
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry DEF BOX_GUARD_C Box {{
            size 0.005 {L4:.4f} 0.04
          }}
        }}
      ]
    }}
    Transform {{
      translation -0.057 0 0.022
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry USE BOX_GUARD_C
        }}
      ]
    }}
  ]
  name "cresta"
  contactMaterial "TrackMaterial"
  boundingObject Group {{
    children [
      USE BOX_LECHO_C
      Transform {{
        translation 0.057 0 0.022
        children [ USE BOX_GUARD_C ]
      }}
      Transform {{
        translation -0.057 0 0.022
        children [ USE BOX_GUARD_C ]
      }}
    ]
  }}
}}
''')

    # 7. BAJADA 3 Y CURVA 2 (180 deg, R=18cm, descenso al suelo)
    R2 = 0.18
    num_seg_c2 = 24
    x_c2 = x4_end - R2
    y_c2 = y4_end
    z_top = z4_end
    z_bottom = 0.02
    
    world_content.append(f'''
# ========================================================
# SECCION 7: BAJADA Y CURVA 2 (180 deg, R=18cm, Hacia Suelo)
# ========================================================
DEF CURVA_2 Solid {{
  children [
''')
    curva2_bounds = []
    d_psi = math.pi / num_seg_c2
    arc_seg2_len = R2 * d_psi * 1.05
    
    for j in range(num_seg_c2):
        psi_mid = (j + 0.5) * d_psi
        frac = (1.0 - math.cos(psi_mid)) / 2.0
        pz = z_top - frac * (z_top - z_bottom)
        
        px = x_c2 + R2 * math.cos(psi_mid)
        py = y_c2 + R2 * math.sin(psi_mid)
        
        tx = -R2 * math.sin(psi_mid)
        ty = R2 * math.cos(psi_mid)
        tz = -(z_top - z_bottom) * 0.5 * math.sin(psi_mid)
        t_norm = math.sqrt(tx**2 + ty**2 + tz**2)
        tx /= t_norm
        ty /= t_norm
        tz /= t_norm
        
        peralte2 = math.radians(20) * math.sin(psi_mid)
        yaw = math.atan2(ty, tx)
        pitch = -math.asin(tz)
        
        cyaw, syaw = math.cos(yaw), math.sin(yaw)
        cpit, spit = math.cos(pitch), math.sin(pitch)
        crol, srol = math.cos(peralte2), math.sin(peralte2)
        
        r00 = cyaw * cpit
        r10 = syaw * cpit
        r20 = -spit
        
        r01 = -syaw * crol + cyaw * spit * srol
        r11 =  cyaw * crol + syaw * spit * srol
        r21 =  cpit * srol
        
        r02 =  syaw * srol + cyaw * spit * crol
        r12 = -cyaw * srol + syaw * spit * crol
        r22 =  cpit * crol
        
        tr = r00 + r11 + r22
        angle = math.acos(max(-1.0, min(1.0, (tr - 1.0) / 2.0)))
        if math.isclose(angle, 0.0, abs_tol=1e-5):
            ax, ay, az = 0, 0, 1
        else:
            denom = 2.0 * math.sin(angle)
            ax = (r21 - r12) / denom
            ay = (r02 - r20) / denom
            az = (r10 - r01) / denom
            anorm = math.sqrt(ax**2 + ay**2 + az**2)
            ax /= anorm
            ay /= anorm
            az /= anorm

        world_content.append(f'''    Transform {{
      translation {px:.5f} {py:.5f} {pz:.5f}
      rotation {ax:.5f} {ay:.5f} {az:.5f} {angle:.5f}
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.15 0.45 0.85
            roughness 0.2
            metalness 0.3
          }}
          geometry DEF BOX_C2_{j} Box {{
            size {arc_seg2_len:.4f} 0.11 0.01
          }}
        }}
        Transform {{
          translation 0 0.057 0.025
          children [
            Shape {{
              appearance USE APP_GUARD
              geometry DEF BOX_G2_{j} Box {{
                size {arc_seg2_len:.4f} 0.005 0.045
              }}
            }}
          ]
        }}
        Transform {{
          translation 0 -0.057 0.025
          children [
            Shape {{
              appearance USE APP_GUARD
              geometry USE BOX_G2_{j}
            }}
          ]
        }}
      ]
    }}
''')
        curva2_bounds.append((px, py, pz, ax, ay, az, angle, f"BOX_C2_{j}", f"BOX_G2_{j}"))

    world_content.append(f'''  ]
  name "curva_2"
  contactMaterial "TrackMaterial"
  boundingObject Group {{
    children [
''')
    for px, py, pz, ax, ay, az, ang, b_lecho, b_guard in curva2_bounds:
        world_content.append(f'''      Transform {{
        translation {px:.5f} {py:.5f} {pz:.5f}
        rotation {ax:.5f} {ay:.5f} {az:.5f} {ang:.5f}
        children [
          USE {b_lecho}
          Transform {{
            translation 0 0.057 0.025
            children [ USE {b_guard} ]
          }}
          Transform {{
            translation 0 -0.057 0.025
            children [ USE {b_guard} ]
          }}
        ]
      }}
''')
    world_content.append('''    ]
  }
}
''')

    # 8. TRAMO RECTO FINAL DE FRENADO (L=75cm sobre el suelo)
    x_freno = x_c2 - R2
    y_freno_start = y_c2
    L_freno = 0.75
    y_freno_end = y_freno_start - L_freno
    z_freno = 0.02
    
    cy_freno = (y_freno_start + y_freno_end) / 2.0
    
    world_content.append(f'''
# ========================================================
# SECCION 8: TRAMO FINAL DE FRENADO (L=75cm, Suelo h=0)
# ========================================================
DEF ZONA_FRENADO Solid {{
  translation {x_freno:.5f} {cy_freno:.5f} {z_freno:.5f}
  children [
    # Lecho con textura de alto rozamiento
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.90 0.75 0.15
        roughness 0.9
        metalness 0.05
      }}
      geometry DEF BOX_LECHO_FRENO Box {{
        size 0.11 {L_freno:.4f} 0.01
      }}
    }}
    # Guardarrail Izquierdo
    Transform {{
      translation 0.057 0 0.022
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry DEF BOX_GUARD_FRENO Box {{
            size 0.005 {L_freno:.4f} 0.04
          }}
        }}
      ]
    }}
    # Guardarrail Derecho
    Transform {{
      translation -0.057 0 0.022
      children [
        Shape {{
          appearance USE APP_GUARD
          geometry USE BOX_GUARD_FRENO
        }}
      ]
    }}
    # Tope terminal de seguridad al final de la pista
    Transform {{
      translation 0 -{L_freno/2 - 0.01:.4f} 0.03
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.85 0.1 0.1
            roughness 0.5
          }}
          geometry Box {{
            size 0.11 0.02 0.05
          }}
        }}
      ]
    }}
  ]
  name "zona_frenado"
  contactMaterial "BrakingTrackMaterial"
  boundingObject Group {{
    children [
      USE BOX_LECHO_FRENO
      Transform {{
        translation 0.057 0 0.022
        children [ USE BOX_GUARD_FRENO ]
      }}
      Transform {{
        translation -0.057 0 0.022
        children [ USE BOX_GUARD_FRENO ]
      }}
      Transform {{
        translation 0 -{L_freno/2 - 0.01:.4f} 0.03
        children [
          Box {{ size 0.11 0.02 0.05 }}
        ]
      }}
    ]
  }}
}}
''')

    # CARRITO (9 ancho x 17 largo x 4.5 alto, cavidad 6x14 cm, masa 200g)
    cart_init_x = cx_transf - 0.01
    cart_init_y = cy_transf
    cart_init_z = cz_transf + 0.028
    
    world_content.append(f'''
# ========================================================
# CARRITO DE LABORATORIO (M=200g, 17x9x4.5cm, Cavidad 14x6cm)
# ========================================================
DEF CARRITO Solid {{
  translation {cart_init_x:.5f} {cart_init_y:.5f} {cart_init_z:.5f}
  children [
    # Chasis principal del carrito con cavidad interior
    Shape {{
      appearance DEF APP_CAR_BODY PBRAppearance {{
        baseColor 0.05 0.70 0.35
        roughness 0.25
        metalness 0.4
      }}
      geometry DEF BOX_CAR_BASE Box {{
        size 0.17 0.09 0.01
      }}
    }}
    # Pared frontal del receptaculo
    Transform {{
      translation 0.075 0 0.018
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.02 0.09 0.026 }}
        }}
      ]
    }}
    # Pared trasera del receptaculo
    Transform {{
      translation -0.075 0 0.018
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.02 0.09 0.026 }}
        }}
      ]
    }}
    # Pared lateral izquierda
    Transform {{
      translation 0 0.0375 0.018
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.14 0.015 0.026 }}
        }}
      ]
    }}
    # Pared lateral derecha
    Transform {{
      translation 0 -0.0375 0.018
      children [
        Shape {{
          appearance USE APP_CAR_BODY
          geometry Box {{ size 0.14 0.015 0.026 }}
        }}
      ]
    }}
    # Fondo de la cavidad receptora (material de alta amortiguacion)
    Transform {{
      translation 0 0 0.006
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.15 0.15 0.18
            roughness 0.8
          }}
          geometry Box {{ size 0.14 0.06 0.002 }}
        }}
      ]
    }}
    # 4 Ruedas de bajo rozamiento
    Transform {{
      translation 0.055 0.046 -0.008
      rotation 1 0 0 1.5708
      children [
        Shape {{
          appearance DEF APP_WHEEL PBRAppearance {{
            baseColor 0.1 0.1 0.1
            roughness 0.3
            metalness 0.8
          }}
          geometry DEF CYL_WHEEL Cylinder {{
            height 0.008
            radius 0.014
          }}
        }}
      ]
    }}
    Transform {{
      translation 0.055 -0.046 -0.008
      rotation 1 0 0 1.5708
      children [
        Shape {{
          appearance USE APP_WHEEL
          geometry USE CYL_WHEEL
        }}
      ]
    }}
    Transform {{
      translation -0.055 0.046 -0.008
      rotation 1 0 0 1.5708
      children [
        Shape {{
          appearance USE APP_WHEEL
          geometry USE CYL_WHEEL
        }}
      ]
    }}
    Transform {{
      translation -0.055 -0.046 -0.008
      rotation 1 0 0 1.5708
      children [
        Shape {{
          appearance USE APP_WHEEL
          geometry USE CYL_WHEEL
        }}
      ]
    }}
  ]
  name "carrito"
  contactMaterial "CartWheelMaterial"
  boundingObject Group {{
    children [
      USE BOX_CAR_BASE
      Transform {{
        translation 0.075 0 0.018
        children [ Box {{ size 0.02 0.09 0.026 }} ]
      }}
      Transform {{
        translation -0.075 0 0.018
        children [ Box {{ size 0.02 0.09 0.026 }} ]
      }}
      Transform {{
        translation 0 0.0375 0.018
        children [ Box {{ size 0.14 0.015 0.026 }} ]
      }}
      Transform {{
        translation 0 -0.0375 0.018
        children [ Box {{ size 0.14 0.015 0.026 }} ]
      }}
      Transform {{
        translation 0.055 0.046 -0.008
        rotation 1 0 0 1.5708
        children [ USE CYL_WHEEL ]
      }}
      Transform {{
        translation 0.055 -0.046 -0.008
        rotation 1 0 0 1.5708
        children [ USE CYL_WHEEL ]
      }}
      Transform {{
        translation -0.055 0.046 -0.008
        rotation 1 0 0 1.5708
        children [ USE CYL_WHEEL ]
      }}
      Transform {{
        translation -0.055 -0.046 -0.008
        rotation 1 0 0 1.5708
        children [ USE CYL_WHEEL ]
      }}
    ]
  }}
  physics Physics {{
    density -1
    mass 0.200
    centerOfMass [ 0 0 0.005 ]
    damping Damping {{
      linear 0.002
      angular 0.002
    }}
  }}
}}
''')

    # MALETA FISICA (7.5x5x4 cm, masa 18g)
    maleta_init_x = x1_start + 0.04 * math.cos(theta1)
    maleta_init_y = y1_start
    maleta_init_z = z1_start - 0.04 * math.sin(theta1) + 0.025
    
    world_content.append(f'''
# ========================================================
# MALETA (7.5x5x4 cm, Masa 18g + Carga)
# ========================================================
DEF MALETA Solid {{
  translation {maleta_init_x:.5f} {maleta_init_y:.5f} {maleta_init_z:.5f}
  rotation {rot_rampa1}
  children [
    Shape {{
      appearance PBRAppearance {{
        baseColor 0.80 0.45 0.15
        roughness 0.4
        metalness 0.1
      }}
      geometry DEF BOX_MALETA Box {{
        size 0.075 0.05 0.04
      }}
    }}
    Transform {{
      translation 0 0 0.024
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.15 0.15 0.15
            roughness 0.5
          }}
          geometry Box {{
            size 0.04 0.008 0.008
          }}
        }}
      ]
    }}
    Transform {{
      translation 0.02 0 0
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.1 0.1 0.1
            roughness 0.6
          }}
          geometry Box {{
            size 0.008 0.052 0.042
          }}
        }}
      ]
    }}
    Transform {{
      translation -0.02 0 0
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0.1 0.1 0.1
            roughness 0.6
          }}
          geometry Box {{
            size 0.008 0.052 0.042
          }}
        }}
      ]
    }}
  ]
  name "maleta"
  contactMaterial "SuitcaseMaterial"
  boundingObject USE BOX_MALETA
  physics Physics {{
    density -1
    mass 0.018
    centerOfMass [ 0 0 0 ]
    damping Damping {{
      linear 0.001
      angular 0.005
    }}
  }}
}}
''')

    # SUPERVISOR
    world_content.append('''
# ========================================================
# CONTROLADOR SUPERVISOR DE FISICA
# ========================================================
Robot {
  supervisor TRUE
  controller "pista_supervisor"
  name "supervisor_fisica"
}
''')

    os.makedirs("worlds", exist_ok=True)
    output_path = os.path.join("worlds", "pista_montana_rusa.wbt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(world_content)
    print(f"Mundo Webots creado exitosamente en: {output_path}")

if __name__ == "__main__":
    create_world()
