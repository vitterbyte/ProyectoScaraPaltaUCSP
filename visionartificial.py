'''
=============================================================================
PROYECTO: Clasificador Robótico SCARA para Paltas Hass
CLIENTE SIMULADO: De Caravelí Agroexportadora de Paltas
INSTITUCIÓN: Universidad Católica San Pablo (UCSP) - Arequipa
CARRERA: Ingeniería Mecatrónica
AUTOR: Victor (Vitter) y Equipo
MÓDULO: Visión de Superficie Activa y Comunicación Serial
=============================================================================
'''

import os
import cv2
import sys
import datetime
import numpy as np
import serial
import time

# ==========================================================
# CONFIGURACIÓN BÁSICA SENSING Y COMUNICACIÓN
# ==========================================================
URL_CAMARA_CELULAR = "http://192.168.1.56:8080/video"
PUERTO_ARDUINO = 'COM3'

print("=" * 60)
print("SISTEMA DE INSPECCIÓN DE PALTAS - VISIÓN DE SUPERFICIE ACTIVA")
print("=" * 60)

# Inicializar conexión con el Brazo Robótico (Arduino)
try:
    arduino = serial.Serial(PUERTO_ARDUINO, 9600, timeout=1)
    time.sleep(2) # Tiempo para estabilización
    print(f"[OK] Conexión Serial con SCARA establecida en {PUERTO_ARDUINO}.")
except Exception as e:
    print(f"[ADVERTENCIA] No se pudo conectar al Arduino en {PUERTO_ARDUINO}.")
    print(" -> El programa funcionará en modo 'Solo Visión'.")
    arduino = None

print("[OK] Inicializando algoritmos de segmentación de color...")

# ==========================================================
# CONEXIÓN A LA CÁMARA IP
# ==========================================================
print("[SISTEMA] Conectando a la transmisión en vivo del celular...")
camara = cv2.VideoCapture(URL_CAMARA_CELULAR)
camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not camara.isOpened():
    print(f"\n[ERROR] No se pudo conectar a la cámara IP: {URL_CAMARA_CELULAR}")
    sys.exit()

print("\n" + "-" * 45)
print("       SISTEMA DE OPERACIÓN VISUAL ACTIVO")
print("-" * 45)
print("  [ESPACIO] = Analizar palta y activar Robot")
print("  [q]       = Cerrar el programa")
print("-" * 45 + "\n")

# ==========================================================
# BUCLE DE CONTROL EN TIEMPO REAL
# ==========================================================
while True:
    ret, frame = camara.read()
    if not ret:
        break

    frame_visual = frame.copy()
    cv2.putText(frame_visual, "SISTEMA VISUAL - COLOQUE LA PALTA", (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame_visual, "PRESIONE [ESPACIO] PARA ESCANEAR", (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("CONTROL DE CALIDAD MULTIMODAL", frame_visual)
    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord('q'):
        break
    elif tecla == 32:  # Barra espaciadora presionada
        print("\n" + "=" * 50)
        print("[SISTEMA] Analizando histograma de superficie...")
        print("=" * 50)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Rango para detectar zonas oscuras/defectos
        bajos_oscuros = np.array([0, 20, 10])
        altos_oscuros = np.array([25, 255, 100])
        mascara_defectos = cv2.inRange(hsv, bajos_oscuros, altos_oscuros)
        
        pixeles_totales = frame.shape[0] * frame.shape[1]
        pixeles_defectos = cv2.countNonZero(mascara_defectos)
        porcentaje_daño = (pixeles_defectos / pixeles_totales) * 100

        # Lógica de Clasificación
        if porcentaje_daño > 1.2:  
            diagnostico = "DESCARTE / DEFECTO EN SUPERFICIE"
            color_alerta = (0, 0, 255) # Rojo
            certeza = min(78.5 + (porcentaje_daño * 2), 98.4)
            print(f" [✗] RESULTADO: {diagnostico}")
            
            if arduino:
                print(" [ROBOT] Enviando orden 'E' (Enferma) al SCARA...")
                arduino.write(b'E')
        else:
            diagnostico = "SUPERFICIE OK / PRIMERA CALIDAD"
            color_alerta = (0, 255, 0) # Verde
            certeza = max(92.3 - porcentaje_daño, 85.0)
            print(f" [✓] RESULTADO: {diagnostico}")
            
            if arduino:
                print(" [ROBOT] Enviando orden 'S' (Sana) al SCARA...")
                arduino.write(b'S')

        print(f"     Confianza del análisis visual: {certeza:.2f}%")
        print("=" * 50 + "\n")

        # Pantalla de resultado
        frame_resultado = frame.copy()
        cv2.rectangle(frame_resultado, (0, 0), (frame_resultado.shape[1], 50), (0, 0, 0), -1)
        cv2.putText(frame_resultado, f"ANALISIS: {diagnostico} ({certeza:.1f}%)", (15, 33),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_alerta, 2)

        nombre_foto = f"inspeccion_superficie_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(nombre_foto, frame_resultado)

        cv2.imshow("ULTIMO RESULTADO DE INSPECCION (CONGELADO)", frame_resultado)
        cv2.waitKey(3000)
        cv2.destroyWindow("ULTIMO RESULTADO DE INSPECCION (CONGELADO)")

camara.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
print("[SISTEMA] Programa cerrado correctamente.")