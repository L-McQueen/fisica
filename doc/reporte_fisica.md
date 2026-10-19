# Memoria de Cálculo y Reporte Físico: Pista Tipo Montaña Rusa

## 1. Resumen Ejecutivo del Experimento
Este informe presenta el modelado analítico y la implementación en el simulador robótico **Webots R2023b** de un sistema de transporte y disipación de energía compuesto por:
1. Una **maleta** que desliza libremente desde una altura inicial de $1.20\text{ m}$ por una rampa de $47\text{ cm}$ inclinada a $30^\circ$.
2. Una **caída libre de $5\text{ cm}$** hacia un **carrito** en reposo ubicado en la estación de transferencia.
3. Un **choque perfectamente inelástico** donde la cantidad de movimiento horizontal se transfiere al carrito.
4. El conjunto recorre una montaña rusa experimental compuesta por:
   - Bajada de $50\text{ cm}$ a $45^\circ$.
   - Curva peraltada de $90^\circ$ ($R = 10\text{ cm}$, peralte $30^\circ$).
   - Subida de $47\text{ cm}$ a $30^\circ$.
   - Cresta horizontal de $10\text{ cm}$.
   - Curva descendente de $180^\circ$ ($R = 18\text{ cm}$) hasta el suelo ($h = 0$).
   - Tramo recto final de frenado de $75\text{ cm}$ con material de alta fricción.
5. El objetivo central es **calcular la masa/peso del carrito** para que el sistema se detenga completamente antes de concluir la pista.

---

## 2. Desarrollo Matemático y Físico

### 2.1. Rampa Inicial (Maleta)
- Altura inicial: $z_0 = 1.20\text{ m}$.
- Longitud: $L_1 = 0.47\text{ m}$.
- Ángulo: $\theta_1 = 30^\circ$.
- Caída vertical: $\Delta z_1 = L_1 \sin(30^\circ) = 0.47 \cdot 0.5 = 0.235\text{ m}$.
- Altura al final de rampa: $z_1 = 1.20 - 0.235 = 0.965\text{ m}$.
- Aceleración con fricción baja $\mu_1 = 0.02$:
  $$a_1 = g (\sin 30^\circ - \mu_1 \cos 30^\circ) = 9.81 (0.5 - 0.02 \cdot 0.866) = 4.735\text{ m/s}^2$$
- Velocidad al abandonar la rampa:
  $$v_1 = \sqrt{2 a_1 L_1} = \sqrt{2 \cdot 4.735 \cdot 0.47} \approx 2.11\text{ m/s}$$
- Componentes de velocidad:
  $$v_{1x} = v_1 \cos(30^\circ) = 2.11 \cdot 0.866 = 1.83\text{ m/s}$$
  $$v_{1z} = -v_1 \sin(30^\circ) = -2.11 \cdot 0.5 = -1.055\text{ m/s}$$

---

### 2.2. Caída Vertical de 5 cm y Aterrizaje
- Descenso vertical: $\Delta h = 0.05\text{ m}$.
- La altura de la plataforma del carrito es:
  $$z_{transf} = z_1 - 0.05 = 0.965 - 0.05 = 0.915\text{ m}$$
- Cinemática de caída:
  $$z(t) = v_{1z0} t + \frac{1}{2} g t^2 = 0.05$$
  $$4.905 t^2 + 1.055 t - 0.05 = 0$$
  $$t_{caida} = \frac{-1.055 + \sqrt{1.055^2 + 4(4.905)(0.05)}}{9.81} \approx 0.040\text{ s}\quad (40\text{ ms})$$
- Desplazamiento horizontal durante la caída:
  $$\Delta x = v_{1x} \cdot t_{caida} = 1.83 \cdot 0.040 \approx 0.073\text{ m} = 7.3\text{ cm}$$
- **Validación geométrica**: La cavidad receptora del carrito mide $14\text{ cm}$ de longitud. Un avance de $7.3\text{ cm}$ sitúa la maleta de $7.5\text{ cm}$ exactamente en el centro de la cavidad, asegurando el acople físico.

---

### 2.3. Conservación de Cantidad de Movimiento (Choque Inelástico)
- En el eje horizontal, la componente de la cantidad de movimiento se conserva durante el impacto:
  $$m_m v_{1x} = (m_m + M_c) v_{post}$$
  $$v_{post} = \frac{m_m}{m_m + M_c} v_{1x}$$
- Para los valores nominales ($m_m = 18\text{ g} = 0.018\text{ kg}$, $M_c = 200\text{ g} = 0.200\text{ kg}$):
  $$v_{post} = \frac{0.018}{0.018 + 0.200} \cdot 1.83 = \frac{0.018}{0.218} \cdot 1.83 \approx 0.151\text{ m/s}$$

---

### 2.4. Conservación de Energía Mecánica en la Pista
- Energía mecánica del conjunto al inicio del recorrido ($z_{transf} = 0.915\text{ m}$):
  $$E_{mec} = \frac{1}{2} (m_m + M_c) v_{post}^2 + (m_m + M_c) g z_{transf}$$
- Al llegar al suelo ($z = 0\text{ m}$), toda la energía potencial se convierte en cinética:
  $$\frac{1}{2} (m_m + M_c) v_{suelo}^2 = \frac{1}{2} (m_m + M_c) v_{post}^2 + (m_m + M_c) g z_{transf}$$
  $$v_{suelo} = \sqrt{v_{post}^2 + 2 g z_{transf}}$$
- Sustituyendo los valores:
  $$v_{suelo} = \sqrt{(0.151)^2 + 2 \cdot 9.81 \cdot 0.915} = \sqrt{0.0228 + 17.952} \approx 4.24\text{ m/s}$$

---

### 2.5. Teorema de Trabajo y Energía en la Zona de Frenado
- Sobre el suelo horizontal, la única fuerza neta horizontal es la fuerza de fricción $F_r = \mu_{freno} N = \mu_{freno} (m_m + M_c) g$.
- El trabajo realizado por la fricción hasta detener el carro ($v_{final} = 0$):
  $$W_{freno} = - F_r \cdot d = - \mu_{freno} (m_m + M_c) g d$$
- Por el teorema de las fuerzas vivas:
  $$\Delta E_k = 0 - \frac{1}{2} (m_m + M_c) v_{suelo}^2 = - W_{freno}$$
  $$d = \frac{v_{suelo}^2}{2 g \mu_{freno}} = \frac{v_{post}^2 + 2 g z_{transf}}{2 g \mu_{freno}} = \frac{z_{transf}}{\mu_{freno}} + \frac{v_{post}^2}{2 g \mu_{freno}}$$
- Para $\mu_{freno} = 1.35$:
  $$d = \frac{0.915}{1.35} + \frac{(0.151)^2}{2 \cdot 9.81 \cdot 1.35} = 0.6778 + 0.0009 \approx 0.68\text{ m}$$
- **Conclusión de frenado**: El carrito se detiene completamente a **$0.68\text{ m}$**, exactamente **$7\text{ cm}$ antes del tope de seguridad** de $0.75\text{ m}$.

---

### 2.6. Fórmula Inversa para la Masa del Carrito $M_c$
Si se desea fijar una distancia de frenado exacta $d_{obj}$ (por ejemplo, con cargas mayores en la maleta):
$$\left( \frac{m_m}{m_m + M_c} v_{1x} \right)^2 = 2 g (\mu_{freno} d_{obj} - z_{transf})$$
$$M_c = m_m \left( \frac{v_{1x}}{\sqrt{2 g (\mu_{freno} d_{obj} - z_{transf})}} - 1 \right)$$

---

## 3. Resumen de Parámetros Físicos

| Tramo | Longitud | Inclinación / Radio | Altura Inicio $\to$ Fin | Velocidad Típica |
| :--- | :---: | :---: | :---: | :---: |
| **Rampa 1 (Maleta)** | $0.47\text{ m}$ | $-30^\circ$ | $1.200\text{ m} \to 0.965\text{ m}$ | $0.00 \to 2.11\text{ m/s}$ |
| **Estación Transferencia** | $0.24\text{ m}$ | $0^\circ$ (horizontal) | $0.915\text{ m}$ (caída $5\text{ cm}$) | Impacto: $v_{post}=0.15\text{ m/s}$ |
| **Bajada 2** | $0.50\text{ m}$ | $-45^\circ$ | $0.915\text{ m} \to 0.561\text{ m}$ | $0.15 \to 2.64\text{ m/s}$ |
| **Curva 1 Peraltada** | Giro $90^\circ$ | $R=0.10\text{ m}$, peralte $30^\circ$ | $0.561\text{ m}$ | $2.64\text{ m/s}$ ($a_c \approx 7.1g$) |
| **Subida** | $0.47\text{ m}$ | $+30^\circ$ | $0.561\text{ m} \to 0.796\text{ m}$ | $2.64 \to 1.53\text{ m/s}$ |
| **Cresta Horizontal** | $0.10\text{ m}$ | $0^\circ$ | $0.796\text{ m}$ | $1.53\text{ m/s}$ |
| **Curva 2 Descendente** | Giro $180^\circ$ | $R=0.18\text{ m}$ hacia suelo | $0.796\text{ m} \to 0.020\text{ m}$ | $1.53 \to 4.24\text{ m/s}$ |
| **Zona Frenado** | $0.75\text{ m}$ | $0^\circ$ (suelo) | $0.020\text{ m}$ | $4.24 \to 0.00\text{ m/s}$ en $0.68\text{ m}$ |

---

## 4. Instrucciones para Ejecutar la Simulación

1. **Vía directa (1 clic)**:
   - Haz doble clic en el archivo [`abrir_simulacion.bat`](file:///c:/Users/Sin%20nombre/Desktop/fisica/abrir_simulacion.bat).
   - Se abrirá Webots R2023b con la pista, el carrito y la maleta ya cargados.
2. **Dentro de Webots**:
   - Presiona el botón **Play (Reproducir en tiempo real)** o **Fast (Rápido)** en la barra superior.
   - Observa la maleta deslizarse, caer dentro del carrito, el tránsito por la curva peraltada a 30°, la subida por la colina y el frenado progresivo en el suelo.
   - En la esquina superior izquierda de la pantalla 3D verás la telemetría en vivo: velocidad, altura, energías cinética y potencial, y la comparación analítica teórica vs simulada.
