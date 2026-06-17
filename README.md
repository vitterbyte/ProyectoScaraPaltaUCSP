# Sistema SCARA Clasificador de Paltas

Este repositorio contiene todo el código fuente y el modelado de una celda de manufactura robótica que diseñamos para automatizar la clasificación de paltas Hass. 

El proyecto integra visión artificial, cinemática espacial y control de hardware en tiempo real. Está pensado como una solución aplicable a la industria agroexportadora Caravelí.

##  Estructura del Sistema

El proyecto funciona conectando tres áreas clave de la mecatrónica:

1. **Visión Artificial (Python + OpenCV):**
   - Utilizamos una cámara IP para monitorear la faja transportadora.
   - El script convierte la imagen a espacio HSV para analizar manchas o defectos en la piel de la palta.
   - Según el porcentaje de daño, toma una decisión y manda una señal por USB al microcontrolador (`S` para Sano, `E` para Descarte).

2. **Control de Hardware (Arduino + CNC Shield):**
   - El Arduino interpreta la señal y ejecuta una secuencia estricta de *Pick and Place*.
   - Programamos una interpolación articular para que los motores a pasos de la base y el codo lleguen al mismo tiempo, haciendo que el movimiento sea fluido y no golpee la fruta.
   - La garra (actuador final) funciona con un motor DC y un puente H L298N, calibrado por milisegundos para dar la fuerza de agarre perfecta.

3. **Análisis y Simulación (MATLAB / Simulink):**
   - **Cinemática:** Scripts con los parámetros de Denavit-Hartenberg (FK) y cálculo por geometría/trigonometría (IK) para pasar de coordenadas espaciales a pasos de motor.
   - **Simulación Dinámica:** Modelo de bloques en Simscape Multibody (`simulacion_scara.slx`) donde validamos físicamente los eslabones y articulaciones antes de armar el robot.

##  Materiales
* Placa Arduino UNO
* CNC Shield V3 + Drivers DRV8825
* 3 Motores NEMA 17
* Puente H L298N y Motor DC (para la garra)
* Smartphone (como cámara IP)
