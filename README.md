# Simulación en Webots: Pista de Física tipo Montaña Rusa

Proyecto completo de simulación en **Webots R2023b** para el análisis de mecánica clásica (cinemática, choque inelástico, dinámica en curvas peraltadas y disipación de energía por fricción).

---

## 📁 Estructura del Proyecto

- **`worlds/pista_montana_rusa.wbt`**: Archivo principal del mundo en Webots con todos los tramos, materiales de contacto, carrito, maleta e iluminación PBR.
- **`controllers/pista_supervisor/pista_supervisor.py`**: Controlador Supervisor en Python con telemetría HUD sobre el visor 3D y cálculo en vivo de física teórica vs simulación.
- **`scripts/generate_world.py`**: Script generador del mundo con geometría analítica parametrizada.
- **`scripts/simulador_fisica_grafico.py`**: Simulador independiente en Python con perfiles de velocidad/altura y curvas de barrido paramétrico de masa.
- **`doc/reporte_fisica.md`**: Memoria de cálculo completa con todas las ecuaciones y deducciones paso a paso.
- **`doc/grafica_fisica_pista.png`**: Gráfica de perfil de velocidad, altura y curva de masa del carrito vs distancia de frenado.
- **`abrir_simulacion.bat`**: Acceso directo para abrir Webots con 1 clic.

---

## 🚀 Cómo Ejecutar

1. Haz doble clic en el archivo **`abrir_simulacion.bat`** en este directorio.
2. Webots se abrirá automáticamente con el mundo listo.
3. Haz clic en **Play ▶** en Webots para ver la simulación en acción y el HUD en vivo con los cálculos.
