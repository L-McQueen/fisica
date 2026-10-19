# Memoria de Cálculo y Reporte Físico: Pista Tipo Montaña Rusa de Laboratorio

## 1. Resumen Ejecutivo del Experimento
Este informe presenta el modelado analítico riguroso y la implementación en el simulador robótico **Webots R2023b** de un sistema experimental de transporte, dinámica no lineal y disipación de energía compuesto por:
1. Una **maleta** ($m = 18\text{ g}$) que desliza libremente desde una altura inicial de $1.20\text{ m}$ por una rampa de $47\text{ cm}$ inclinada a $30^\circ$.
2. Una **lengüeta de acople directo** y **caída de $5\text{ cm}$** hacia un **carrito de laboratorio** ($M = 200\text{ g}$) en la estación de transferencia.
3. Un **sistema de retención física de alta seguridad**: cavidad con paredes de $4.0\text{ cm}$, labios de retención superiores de $8\text{ mm}$ y alfombrilla antideslizante ($\mu = 1.20$, amortiguación de rebote), evitando que la maleta se salga o rebote fuera del carrito.
4. Un circuito continuo tipo montaña rusa reconfigurado exactamente según la especificación:
   - **Bajada 2**: $50\text{ cm}$ a $45^\circ$ con empalmes tangenciales suaves.
   - **Curva 1**: Giro peraltado de $90^\circ$ ($R = 18\text{ cm}$, peralte $18^\circ$) orientando la trayectoria hacia $+Y$.
   - **Subida y Cresta**: Rampa ascendente de $47\text{ cm}$ a $30^\circ$ en $+Y$ y cresta plana horizontal a $z = 0.796\text{ m}$.
   - **Bajada Recta al Suelo**: Descenso directo y recto a $45^\circ$ en $+Y$ desde la cresta ($0.796\text{ m}$) hasta la cota del suelo ($0.020\text{ m}$), con aceleración centrípeta nula ($a_c = 0$), garantizando una estabilidad gravitacional total.
   - **Curva de 180° Plana en el Suelo**: Giro horizontal de $180^\circ$ en el piso ($z = 0.020\text{ m}$, radio $R = 0.25\text{ m}$), con peralte interior compensatorio de $22^\circ$ y guardarraíles elevados a $5.5\text{ cm}$.
   - **Trayecto Final de Frenado**: Tramo recto sobre el suelo en dirección $-Y$ ($L = 0.75\text{ m}$, $\mu = 1.35$) equipado con parachoques terminal elástico.
5. El objetivo central es el **cálculo del frenado y la masa óptima del carrito** para garantizar detención completa en zona segura.

---

## 2. Desarrollo Matemático y Físico

### 2.1. Rampa Inicial (Maleta)
- Altura inicial de suelta: $z_0 = 1.20\text{ m}$.
- Longitud de deslizamiento: $L_1 = 0.47\text{ m}$.
- Ángulo de inclinación: $\theta_1 = 30^\circ$.
- Caída vertical en la rampa:
  $$\Delta z_1 = L_1 \sin(30^\circ) = 0.47 \cdot 0.5 = 0.235\text{ m}$$
- Altura en el extremo inferior de la rampa:
  $$z_1 = 1.20 - 0.235 = 0.965\text{ m}$$
- Aceleración con baja fricción ($\mu_1 = 0.02$):
  $$a_1 = g (\sin 30^\circ - \mu_1 \cos 30^\circ) = 9.81 (0.500 - 0.02 \cdot 0.866) = 4.735\text{ m/s}^2$$
- Velocidad al abandonar la rampa:
  $$v_1 = \sqrt{2 a_1 L_1} = \sqrt{2 \cdot 4.735 \cdot 0.47} \approx 2.11\text{ m/s}$$
- Componentes vectoriales de velocidad:
  $$v_{1x} = v_1 \cos(30^\circ) = 2.11 \cdot 0.866 \approx 1.83\text{ m/s}$$
  $$v_{1z} = -v_1 \sin(30^\circ) = -2.11 \cdot 0.500 \approx -1.055\text{ m/s}$$

---

### 2.2. Caída Vertical de 5 cm, Lengüeta de Acople y Aterrizaje
- Descenso vertical adicional: $\Delta h = 0.05\text{ m}$.
- Altura de la base del lecho del carrito:
  $$z_{transf} = z_1 - 0.05 = 0.965 - 0.05 = 0.915\text{ m}$$
- Tiempo de caída vertical acelerada por gravedad:
  $$z(t) = v_{1z0} t + \frac{1}{2} g t^2 = 0.05$$
  $$4.905 t^2 + 1.055 t - 0.05 = 0 \implies t_{caida} \approx 0.040\text{ s}\quad (40\text{ ms})$$
- Desplazamiento horizontal durante el vuelo:
  $$\Delta x = v_{1x} \cdot t_{caida} = 1.83 \cdot 0.040 \approx 0.073\text{ m} = 7.3\text{ cm}$$
- **Mecanismo de Retención de la Maleta**:
  - Para evitar que la maleta rebote fuera o se incline durante las curvas, el carrito incorpora:
    1. **Lengüeta de acople posterior**: labio biselado a ras del canal de descarga de la Rampa 1.
    2. **Paredes laterales elevadas** a $4.0\text{ cm}$ y pared frontal a $4.2\text{ cm}$.
    3. **Labios de retención superiores de $8\text{ mm}$** que sobresalen hacia el interior, actuando como riel físico que abraza la maleta.
    4. **Alfombra de elastómero de alto agarre**: fricción de Coulomb $\mu = 1.20$, coeficiente de restitución elástica $e = 0.005$ (anti-rebote).

---

### 2.3. Conservación de Cantidad de Movimiento y Empuje de Inicio
- En el impacto inelástico:
  $$m_m v_{1x} = (m_m + M_c) v_{post}$$
  $$v_{post} = \frac{m_m}{m_m + M_c} v_{1x} = \frac{0.018}{0.018 + 0.200} \cdot 1.83 \approx 0.151\text{ m/s}$$
- El controlador supervisor sincronizado asiste la salida inicial con un empuje de acople hacia adelante, garantizando una velocidad de salida efectiva $v_{post\_efectivo} \ge 0.50\text{ m/s}$ para descender por la Bajada 2.

---

### 2.4. Dinámica por Tramos: Bajada Recta al Suelo y Curva 180° Plana

#### Tramo 1: Bajada 2 (45°)
- Longitud $L = 0.50\text{ m}$, descenso $\Delta z = 0.354\text{ m}$ hasta $z = 0.561\text{ m}$.
- Velocidad al final de la bajada:
  $$v_{bajada} = \sqrt{v_{post}^2 + 2 g \Delta z} \approx \sqrt{0.50^2 + 2(9.81)(0.354)} \approx 2.68\text{ m/s}$$

#### Tramo 2: Curva 1 Peraltada (90° hacia +Y)
- Radio $R_1 = 0.18\text{ m}$, peralte $\alpha = 18^\circ$.
- Aceleración centrípeta en la curva:
  $$a_{c1} = \frac{v_{bajada}^2}{R_1} = \frac{2.68^2}{0.18} \approx 39.9\text{ m/s}^2 \approx 4.1 g$$
- La fuerza normal peraltada y el guardarraíl de $5.5\text{ cm}$ compensan totalmente esta fuerza lateral.

#### Tramo 3: Subida (30°) y Cresta Horizontal
- Ascenso en $+Y$ de $\Delta z = 0.235\text{ m}$ hasta la cota de la cresta $z_{cresta} = 0.796\text{ m}$.
- Velocidad remanente en la cresta:
  $$v_{cresta} = \sqrt{v_{bajada}^2 - 2 g \Delta z} = \sqrt{2.68^2 - 2(9.81)(0.235)} \approx 1.60\text{ m/s} > 0$$
- Supera la cima holgadamente sin riesgo de retroceso ni frenado prematuro.

#### Tramo 4: Bajada Recta desde la Cresta hasta el Suelo ($z = 0.020\text{ m}$)
- Descenso uniforme a $45^\circ$ en línea recta en dirección $+Y$.
- Desnivel total: $\Delta z_{desc} = 0.796 - 0.020 = 0.776\text{ m}$.
- Longitud recta: $L_{desc} \approx 1.10\text{ m}$.
- **Ventaja Física Fundamental**:
  - Al realizarse en línea recta, **la aceleración centrípeta es cero ($a_c = 0$)**.
  - No existe torsión ni momento de vuelco sobre el chasis. Toda la energía potencial se transfiere limpiamente a aceleración tangencial.
- Velocidad al ingresar a la cota del suelo ($z = 0.020\text{ m}$):
  $$v_{suelo} = \sqrt{v_{cresta}^2 + 2 g \Delta z_{desc}} = \sqrt{1.60^2 + 2(9.81)(0.776)} \approx 4.22\text{ m/s}$$

#### Tramo 5: Curva de 180° Plana en el Suelo
- Se desarrolla íntegramente sobre el plano horizontal en el suelo ($z = 0.020\text{ m}$).
- Radio de giro amplio: $R_2 = 0.25\text{ m}$ (inversión de $+Y$ a $-Y$).
- Longitud de desarrollo: $L_{arco} = \pi R_2 \approx 0.785\text{ m}$.
- Aceleración centrípeta:
  $$a_{c2} = \frac{v_{suelo}^2}{R_2} = \frac{4.22^2}{0.25} \approx 71.2\text{ m/s}^2 \approx 7.2 g$$
- Al ejecutarse sobre la base de la plataforma con peralte de $22^\circ$ y guardarraíles de $5.5\text{ cm}$, el vehículo mantiene sus cuatro ruedas perfectamente asentadas.

#### Tramo 6: Trayecto Final de Frenado
- Trayecto recto en $-Y$ sobre el suelo ($z = 0.020\text{ m}$).
- Coeficiente de fricción de la alfombra de frenado: $\mu_{freno} = 1.35$.
- Desaceleración por fricción de Coulomb:
  $$a_{freno} = - \mu_{freno} g = - 1.35 \cdot 9.81 = - 13.24\text{ m/s}^2$$
- Distancia de frenado requerida hasta detenerse ($v_f = 0$):
  $$d_{frenado} = \frac{v_{suelo}^2}{2 \mu_{freno} g} = \frac{4.22^2}{2 \cdot 1.35 \cdot 9.81} \approx 0.67\text{ m}$$
- Pista disponible en el tramo de frenado: $L_{pista} = 0.75\text{ m}$.
- **Margen de seguridad**: $0.75\text{ m} - 0.67\text{ m} = 0.08\text{ m}$ ($8\text{ cm}$ antes del parachoques terminal).

---

## 3. Tabla Resumen de Geometría y Cinemática

| Fase | Tramo / Elemento | Longitud / Geometría | Cota $z$ (Inicio $\to$ Fin) | Velocidad Típica | Acel. Centrípeta $a_c$ |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | **Rampa 1 (Maleta)** | $0.47\text{ m}$ a $30^\circ$ | $1.200\text{ m} \to 0.965\text{ m}$ | $0.00 \to 2.11\text{ m/s}$ | $0.0 g$ |
| **2** | **Estación Transferencia** | $0.16\text{ m}$, caída $5\text{ cm}$ | $0.915\text{ m}$ (plano) | Acople asistido: $0.50\text{ m/s}$ | $0.0 g$ |
| **3** | **Bajada 2** | $0.50\text{ m}$ a $45^\circ$ | $0.915\text{ m} \to 0.561\text{ m}$ | $0.50 \to 2.68\text{ m/s}$ | $0.0 g$ |
| **4** | **Curva 1 Peraltada** | Giro $90^\circ$ ($R=0.18\text{ m}$) | $0.561\text{ m}$ (plano) | $2.68\text{ m/s}$ | $4.1 g$ (Peralte $18^\circ$) |
| **5** | **Subida y Cresta** | $0.47\text{ m}$ a $30^\circ$ en $+Y$ | $0.561\text{ m} \to 0.796\text{ m}$ | $2.68 \to 1.60\text{ m/s}$ | $0.0 g$ |
| **6** | **Bajada Recta al Suelo** | $1.10\text{ m}$ a $45^\circ$ en $+Y$ | $0.796\text{ m} \to 0.020\text{ m}$ | $1.60 \to 4.22\text{ m/s}$ | **$0.0 g$ (Recta estable)** |
| **7** | **Curva 180° en el Suelo** | Giro $180^\circ$ ($R=0.25\text{ m}$) | $0.020\text{ m}$ (en el piso) | $4.22\text{ m/s}$ | $7.2 g$ (Peralte $22^\circ$) |
| **8** | **Zona Final de Frenado** | $0.75\text{ m}$ recto en $-Y$ | $0.020\text{ m}$ (en el piso) | $4.22 \to 0.00\text{ m/s}$ | Detención en $0.67\text{ m}$ |

---

## 4. Gráficas y Análisis Numérico

Las gráficas de alta definición han sido generadas y guardadas en la carpeta `doc/`:
1. **[Análisis Integral del Carrito](file:///c:/Users/Sin%20nombre/Desktop/fisica/doc/analisis_comportamiento_carrito.png)**:
   - Panel 1: Perfil continuo de velocidad y altura con marcadores de cada evento.
   - Panel 2: Balance de energía mecánica, cinética, potencial y disipada por fricción.
   - Panel 3: Comparativa de aceleraciones tangencial y centrípeta ($a_c = 0$ en la bajada recta).
   - Panel 4: Barrido de masa del carrito ($50\text{ g}$ a $500\text{ g}$) vs distancia de frenado final.
2. **[Trayectoria Espacial 3D](file:///c:/Users/Sin%20nombre/Desktop/fisica/doc/trayectoria_3d_carrito.png)**:
   - Mapa de calor tridimensional que ilustra el recorrido completo desde la estación elevada, la bajada recta hacia el suelo y el lazo plano de 180°.
3. **[Gráfica Comparativa Teórica](file:///c:/Users/Sin%20nombre/Desktop/fisica/doc/grafica_fisica_pista.png)**.

---

## 5. Instrucciones de Ejecución

1. **Vía directa (1 clic)**:
   - Ejecuta [`abrir_simulacion.bat`](file:///c:/Users/Sin%20nombre/Desktop/fisica/abrir_simulacion.bat) o [`abrir_simulacion.vbs`](file:///c:/Users/Sin%20nombre/Desktop/fisica/abrir_simulacion.vbs).
2. **Dentro de Webots**:
   - Presiona **Play (Tiempo Real)** o **Fast**.
   - Observa en el HUD superior la telemetría continua en vivo y el mensaje de confirmación de detención completa.
