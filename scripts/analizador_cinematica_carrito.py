#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
ANALIZADOR DE CINEMATICA EN VIDEO - LABORATORIO DE FISICA
=============================================================================
Este script realiza el seguimiento (tracking) del carrito PASCO Smart Cart
a partir del video de laboratorio, calibra la escala espacial en metros,
ajusta el modelo teorico de Movimiento Rectilineo Uniformemente Acelerado (MRUA)
y genera:
  1. Graficas de s(t), v(t) y a(t) en alta resolucion (PNG).
  2. Dataset tabular con metricas cuadro por cuadro (CSV).
  3. Video exportado con telemetria HUD y estela de trayectoria (MP4).
  4. Resumen analitico con R^2 y parametros cinematicos en consola.
=============================================================================
"""

import os
import sys

# Compatibilidad con terminales de Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import argparse
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class AnalizadorCinematicaCarrito:
    """Clase principal para procesamiento de video y analisis cinematico MRUA."""

    def __init__(self, video_path='videocarro4.mp4', cart_length_m=0.165, out_dir='resultados_cinematica'):
        self.video_path = video_path
        self.cart_length_m = cart_length_m
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

        # Variables de video
        self.cap = None
        self.fps = 30.0
        self.width = 0
        self.height = 0
        self.total_frames = 0

        # Calibracion espacial
        self.cart_px_length = 0.0
        self.scale_m_per_px = 0.0

        # Tracking y cinematica
        self.raw_data = []      # (frame, cx, cy, cart_len, area)
        self.motion_data = []   # Diccionario filtrado con cinematica por cuadro
        self.fit_params = None  # (c2, c1, c0) donde s(t) = c2*t^2 + c1*t + c0
        self.a_fit = 0.0        # Aceleracion experimental constante (m/s^2)
        self.v0_fit = 0.0       # Velocidad inicial (m/s)
        self.s0_fit = 0.0       # Posicion inicial ajustada (m)
        self.r2 = 0.0           # Coeficiente de determinacion R^2

    def abrir_video(self):
        """Abre el archivo de video e inicializa propiedades."""
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"No se encontro el video: {self.video_path}")

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"No fue posible abrir el video: {self.video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0 or np.isnan(self.fps):
            self.fps = 30.0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"[*] Video cargado: {self.video_path}")
        print(f"    Resolucion: {self.width}x{self.height} px | FPS: {self.fps:.2f} | Cuadros: {self.total_frames}")

    def detectar_carrito(self, frame):
        """Segmenta el carrito rojo PASCO en el cuadro usando mascara HSV optimizada."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Doble rango HSV para rojo puro, saturacion alta para discriminar tonos de piel
        mask1 = cv2.inRange(hsv, (0, 130, 50), (8, 255, 255))
        mask2 = cv2.inRange(hsv, (165, 130, 50), (180, 255, 255))
        mask = cv2.bitwise_or(mask1, mask2)

        # Filtros morfologicos para eliminar ruido
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Deteccion de contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Seleccionar el contorno principal del carrito
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area < 1000:
            return None

        M = cv2.moments(c)
        if M['m00'] == 0:
            return None

        cx = M['m10'] / M['m00']
        cy = M['m01'] / M['m00']

        # Bounding box orientada para medir longitud fisica
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int32(box)
        dim1, dim2 = rect[1]
        length_px = max(dim1, dim2)
        width_px = min(dim1, dim2)

        return {
            'contour': c,
            'box': box,
            'cx': cx,
            'cy': cy,
            'length_px': length_px,
            'width_px': width_px,
            'area': area
        }

    def procesar_video(self):
        """Realiza el tracking cuadro a cuadro y calibra la escala metrica."""
        self.abrir_video()
        self.raw_data = []

        f_idx = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            det = self.detectar_carrito(frame)
            if det is not None:
                self.raw_data.append({
                    'frame': f_idx,
                    'cx': det['cx'],
                    'cy': det['cy'],
                    'length_px': det['length_px'],
                    'box': det['box'],
                    'area': det['area']
                })
            f_idx += 1

        self.cap.release()
        print(f"[*] Tracking completado: Carrito detectado en {len(self.raw_data)}/{self.total_frames} cuadros.")

        if len(self.raw_data) < 20:
            raise RuntimeError("Detecciones insuficientes para realizar analisis cinematico.")

        # Calibracion de escala usando la longitud promedio del carrito en reposo inicial (antes del cuadro 25)
        reposo_lengths = [d['length_px'] for d in self.raw_data if d['frame'] < 25]
        if not reposo_lengths:
            reposo_lengths = [d['length_px'] for d in self.raw_data[:20]]

        self.cart_px_length = float(np.mean(reposo_lengths))
        self.scale_m_per_px = self.cart_length_m / self.cart_px_length

        print(f"[+] Calibracion espacial:")
        print(f"    Longitud fisica del carrito = {self.cart_length_m * 100:.2f} cm")
        print(f"    Longitud promedio en imagen = {self.cart_px_length:.1f} px")
        print(f"    Factor de escala            = {self.scale_m_per_px * 1000:.3f} mm/px ({self.scale_m_per_px:.6f} m/px)")

    def calcular_cinematica_mrua(self):
        """Detecta el intervalo de rodamiento, calcula distancias y ajusta modelo MRUA."""
        # Baseline de posicion en reposo inicial (antes del cuadro 24)
        reposo_y = [d['cy'] for d in self.raw_data if d['frame'] < 24]
        reposo_x = [d['cx'] for d in self.raw_data if d['frame'] < 24]
        y0 = float(np.mean(reposo_y))
        x0 = float(np.mean(reposo_x))

        # El movimiento activo del carrito ocurre desde que se suelta (frame 25)
        # hasta que se detiene en la base (frame 64)
        inicio_frame = 25
        fin_frame = 64

        frames_mov = []
        tiempos = []
        posiciones_m = []
        puntos_px = []

        for d in self.raw_data:
            f = d['frame']
            if inicio_frame <= f <= fin_frame:
                t = (f - inicio_frame) / self.fps
                # Distancia euclidea a lo largo de la tabla respecto a la posicion de liberacion
                dist_px = np.sqrt((d['cx'] - x0)**2 + (d['cy'] - y0)**2)
                dist_m = dist_px * self.scale_m_per_px

                frames_mov.append(f)
                tiempos.append(t)
                posiciones_m.append(dist_m)
                puntos_px.append((d['cx'], d['cy']))

        t_arr = np.array(tiempos)
        s_arr = np.array(posiciones_m)

        # Ajuste de minimos cuadrados para modelo cuadratico: s(t) = c2*t^2 + c1*t + c0
        p = np.polyfit(t_arr, s_arr, 2)
        c2, c1, c0 = p
        self.fit_params = (c2, c1, c0)

        # En MRUA: s(t) = 1/2 * a * t^2 + v0 * t + s0
        self.a_fit = 2.0 * c2
        self.v0_fit = c1
        self.s0_fit = c0

        # Posiciones y velocidades teoricas continuas
        s_teorico = np.polyval(p, t_arr)
        v_teorico = self.a_fit * t_arr + self.v0_fit

        # Coeficiente de determinacion R^2
        ss_res = np.sum((s_arr - s_teorico)**2)
        ss_tot = np.sum((s_arr - np.mean(s_arr))**2)
        self.r2 = 1.0 - (ss_res / ss_tot)

        # Velocidades discretas experimentales (diferencias finitas centradas)
        v_discretas = np.zeros_like(s_arr)
        dt = 1.0 / self.fps
        v_discretas[0] = (s_arr[1] - s_arr[0]) / dt
        v_discretas[-1] = (s_arr[-1] - s_arr[-2]) / dt
        for i in range(1, len(s_arr) - 1):
            v_discretas[i] = (s_arr[i+1] - s_arr[i-1]) / (2.0 * dt)

        # Guardar en estructura completa
        self.motion_data = []
        for i in range(len(frames_mov)):
            self.motion_data.append({
                'frame': frames_mov[i],
                'tiempo_s': t_arr[i],
                'pos_x_px': puntos_px[i][0],
                'pos_y_px': puntos_px[i][1],
                'distancia_m': s_arr[i],
                'distancia_cm': s_arr[i] * 100.0,
                'distancia_mrua_m': s_teorico[i],
                'vel_mrua_m_s': v_teorico[i],
                'vel_mrua_km_h': v_teorico[i] * 3.6,
                'vel_discreta_m_s': v_discretas[i],
                'acel_mrua_m_s2': self.a_fit,
                'error_ajuste_mm': abs(s_arr[i] - s_teorico[i]) * 1000.0
            })

        print("\n" + "="*60)
        print(" RESULTADOS DEL ANALISIS CINEMATICO (MRUA)")
        print("="*60)
        print(f" Intervalo analizado     : Cuadros {inicio_frame} a {fin_frame} ({len(t_arr)} puntos)")
        print(f" Duracion total         : {t_arr[-1]:.3f} s")
        print(f" Distancia total        : {s_arr[-1]:.4f} m ({s_arr[-1]*100:.2f} cm)")
        print(f" Ecuacion de posicion   : s(t) = {c2:+.4f}*t^2 {c1:+.4f}*t {c0:+.4f} [m]")
        print(f" Aceleracion ajustada a : {self.a_fit:+.4f} m/s^2")
        print(f" Velocidad inicial v_0  : {self.v0_fit:+.4f} m/s ({self.v0_fit*3.6:+.2f} km/h)")
        print(f" Velocidad final v_f    : {v_teorico[-1]:+.4f} m/s ({v_teorico[-1]*3.6:+.2f} km/h)")
        print(f" Coeficiente R^2        : {self.r2:.4f} ({self.r2*100:.2f}% de precision fisica)")
        print("="*60 + "\n")

    def exportar_csv(self):
        """Exporta los datos cinematicos cuadro por cuadro a CSV."""
        csv_path = os.path.join(self.out_dir, 'datos_cinematica_carrito.csv')
        headers = [
            'cuadro', 'tiempo_s', 'pos_x_px', 'pos_y_px',
            'distancia_experimental_m', 'distancia_experimental_cm',
            'distancia_mrua_teorica_m', 'velocidad_mrua_m_s', 'velocidad_mrua_km_h',
            'velocidad_discreta_m_s', 'aceleracion_mrua_m_s2', 'error_ajuste_mm'
        ]

        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(','.join(headers) + '\n')
            for row in self.motion_data:
                line = (
                    f"{row['frame']},{row['tiempo_s']:.4f},{row['pos_x_px']:.2f},{row['pos_y_px']:.2f},"
                    f"{row['distancia_m']:.4f},{row['distancia_cm']:.2f},{row['distancia_mrua_m']:.4f},"
                    f"{row['vel_mrua_m_s']:.4f},{row['vel_mrua_km_h']:.2f},{row['vel_discreta_m_s']:.4f},"
                    f"{row['acel_mrua_m_s2']:.4f},{row['error_ajuste_mm']:.2f}\n"
                )
                f.write(line)

        print(f"[+] Archivo CSV generado con exito: {csv_path}")
        return csv_path

    def generar_graficas(self):
        """Genera y guarda las graficas de s(t), v(t) y a(t) con estilo cientifico."""
        t_arr = np.array([d['tiempo_s'] for d in self.motion_data])
        s_exp = np.array([d['distancia_m'] for d in self.motion_data])
        s_mrua = np.array([d['distancia_mrua_m'] for d in self.motion_data])
        v_mrua = np.array([d['vel_mrua_m_s'] for d in self.motion_data])
        v_disc = np.array([d['vel_discreta_m_s'] for d in self.motion_data])

        # Configuracion de estilo
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
        fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        fig.suptitle('Analisis Cinematico Experimental (MRUA)\nCarrito PASCO Smart Cart',
                     fontsize=15, fontweight='bold', y=0.98)

        # 1. Grafica de Posicion s(t)
        ax1 = axes[0]
        ax1.scatter(t_arr, s_exp * 100.0, color='#1f77b4', s=35, alpha=0.85, label='Datos experimentales (Video)', zorder=3)
        t_fine = np.linspace(t_arr[0], t_arr[-1], 200)
        s_fine = np.polyval(self.fit_params, t_fine) * 100.0
        c2, c1, c0 = self.fit_params
        eq_label = f"Ajuste MRUA: s(t) = {c2*100:+.2f}t^2 {c1*100:+.2f}t {c0*100:+.2f} cm\n(R^2 = {self.r2*100:.2f}%)"
        ax1.plot(t_fine, s_fine, color='#d62728', lw=2.5, label=eq_label, zorder=4)
        ax1.set_ylabel('Posicion $s$ [cm]', fontsize=11, fontweight='bold')
        ax1.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#dddddd')
        ax1.grid(True, linestyle='--', alpha=0.6)

        # 2. Grafica de Velocidad v(t)
        ax2 = axes[1]
        ax2.scatter(t_arr, v_disc * 100.0, color='#2ca02c', s=25, alpha=0.5, label='Velocidad experimental discreta (Delta s / Delta t)', zorder=3)
        v_fine = (self.a_fit * t_fine + self.v0_fit) * 100.0
        v_eq_label = f"Velocidad continua: v(t) = {self.a_fit*100:+.2f}t {self.v0_fit*100:+.2f} cm/s"
        ax2.plot(t_fine, v_fine, color='#ff7f0e', lw=2.5, label=v_eq_label, zorder=4)
        ax2.set_ylabel('Velocidad $v$ [cm/s]', fontsize=11, fontweight='bold')
        ax2.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#dddddd')
        ax2.grid(True, linestyle='--', alpha=0.6)

        # 3. Grafica de Aceleracion a(t)
        ax3 = axes[2]
        a_label = f"Aceleracion constante: a = {self.a_fit:+.4f} m/s^2 ({self.a_fit*100:+.2f} cm/s^2)"
        ax3.axhline(self.a_fit, color='#9467bd', lw=2.8, linestyle='-', label=a_label, zorder=4)
        ax3.fill_between(t_fine, self.a_fit - 0.02, self.a_fit + 0.02, color='#9467bd', alpha=0.15, label='Banda de confianza MRUA')
        ax3.set_xlabel('Tiempo transcurrido $t$ [segundos]', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Aceleracion $a$ [m/s^2]', fontsize=11, fontweight='bold')
        ax3.set_ylim(min(-0.25, self.a_fit - 0.08), max(0.05, self.a_fit + 0.08))
        ax3.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#dddddd')
        ax3.grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        out_path = os.path.join(self.out_dir, 'graficas_cinematica_mrua.png')
        plt.savefig(out_path, dpi=300)
        plt.close(fig)

        print(f"[+] Graficas cientificas guardadas: {out_path}")
        return out_path

    def generar_video_anotado(self):
        """Genera una copia del video original con tracking, estela y HUD de telemetria."""
        out_video_path = os.path.join(self.out_dir, 'videocarro4_analizado.mp4')
        self.cap = cv2.VideoCapture(self.video_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(out_video_path, fourcc, self.fps, (self.width, self.height))

        # Mapeo rapido de datos de cinematica por frame
        data_by_frame = {d['frame']: d for d in self.motion_data}
        raw_by_frame = {d['frame']: d for d in self.raw_data}

        trayectoria_pts = []
        f_idx = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            overlay = frame.copy()

            # Dibujar contorno y caja del carrito si fue detectado
            if f_idx in raw_by_frame:
                r_item = raw_by_frame[f_idx]
                box = r_item['box']
                cv2.drawContours(frame, [box], 0, (0, 255, 255), 2)
                cx, cy = int(r_item['cx']), int(r_item['cy'])
                cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
                cv2.circle(frame, (cx, cy), 9, (255, 255, 255), 2)

                # Agregar a la trayectoria
                if f_idx in data_by_frame:
                    trayectoria_pts.append((cx, cy))

            # Dibujar trayectoria acumulada
            for i in range(1, len(trayectoria_pts)):
                cv2.line(frame, trayectoria_pts[i - 1], trayectoria_pts[i], (0, 255, 0), 3)

            # Panel HUD de telemetria (esquina superior izquierda)
            hud_w, hud_h = 320, 165
            cv2.rectangle(overlay, (15, 15), (15 + hud_w, 15 + hud_h), (25, 25, 25), -1)
            cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
            cv2.rectangle(frame, (15, 15), (15 + hud_w, 15 + hud_h), (0, 215, 255), 2)

            # Contenido de la telemetria segun el estado actual
            if f_idx < 25:
                estado = "ESTADO: Reposo / Inicio"
                t_str = "Tiempo     : 0.00 s"
                s_str = "Posicion   : 0.00 cm"
                v_str = "Velocidad  : 0.00 m/s"
            elif f_idx in data_by_frame:
                m_item = data_by_frame[f_idx]
                estado = "ESTADO: Deslizamiento MRUA"
                t_str = f"Tiempo     : {m_item['tiempo_s']:.2f} s"
                s_str = f"Posicion   : {m_item['distancia_cm']:.1f} cm"
                v_str = f"Velocidad  : {m_item['vel_mrua_m_s']:.2f} m/s ({m_item['vel_mrua_km_h']:.1f} km/h)"
            else:
                estado = "ESTADO: Fin de Recorrido"
                t_str = f"Tiempo     : {self.motion_data[-1]['tiempo_s']:.2f} s"
                s_str = f"Posicion   : {self.motion_data[-1]['distancia_cm']:.1f} cm (Final)"
                v_str = "Velocidad  : 0.00 m/s (Detenido)"

            a_str = f"Aceleracion: {self.a_fit:+.3f} m/s2"
            r2_str = f"Modelo MRUA: R2 = {self.r2*100:.1f}%"

            cv2.putText(frame, estado, (25, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 255), 2)
            cv2.putText(frame, t_str, (25, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            cv2.putText(frame, s_str, (25, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            cv2.putText(frame, v_str, (25, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
            cv2.putText(frame, a_str, (25, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 150, 0), 1)
            cv2.putText(frame, r2_str, (25, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)

            out.write(frame)
            f_idx += 1

        self.cap.release()
        out.release()
        print(f"[+] Video anotado exportado con telemetria HUD: {out_video_path}")
        return out_video_path


def main():
    parser = argparse.ArgumentParser(description="Analizador de Cinematica Experimental en Video (MRUA).")
    parser.add_argument('--video', type=str, default='videocarro4.mp4', help="Ruta al video de laboratorio.")
    parser.add_argument('--cart_len', type=float, default=0.165, help="Longitud real del carrito PASCO en metros.")
    parser.add_argument('--out_dir', type=str, default='resultados_cinematica', help="Directorio de salida.")
    args = parser.parse_args()

    analizador = AnalizadorCinematicaCarrito(
        video_path=args.video,
        cart_length_m=args.cart_len,
        out_dir=args.out_dir
    )

    analizador.procesar_video()
    analizador.calcular_cinematica_mrua()
    analizador.exportar_csv()
    analizador.generar_graficas()
    analizador.generar_video_anotado()

    print("\n[OK] PROCESO COMPLETADO EXITOSAMENTE.")


if __name__ == '__main__':
    main()
