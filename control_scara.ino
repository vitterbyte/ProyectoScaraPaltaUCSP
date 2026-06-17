/*
=============================================================================
PROYECTO: Clasificador Robótico SCARA para Paltas Hass
INSTITUCIÓN: Universidad Católica San Pablo (UCSP)
MÓDULO: Control de Motores (CNC Shield V3 + L298N) e Interpolación Articular
AUTOR: Victor (Vitter) y Equipo
=============================================================================
*/

#include <AccelStepper.h>

// ==== Pines CNC Shield V3 ====
#define EN_PIN     8
#define X_STEP_PIN 2
#define X_DIR_PIN  5
#define Y_STEP_PIN 3
#define Y_DIR_PIN  6
#define Z_STEP_PIN 4
#define Z_DIR_PIN  7

// ==== Pines Puente H (Motor DC Garra) ====
#define GARRA_IN3 A0 
#define GARRA_IN4 A1

AccelStepper joint1(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper joint2(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper joint3(1, Z_STEP_PIN, Z_DIR_PIN);

// =================================================================
// ⚙️ ZONA DE CALIBRACIÓN Y CINEMÁTICA
// =================================================================
long Z_BAJA_FAJA   = -1800; 
long Z_BAJA_CAJA_S = -1800; 
long Z_BAJA_CAJA_E = -1800; 

long pasos_sano_X = 800;   
long pasos_sano_Y = -400;  
long pasos_enfermo_X = -800; 
long pasos_enfermo_Y = 400;  

int tiempo_cierre = 3000;   // ms para asegurar el torque de sujeción
int tiempo_apertura = 1900; // ms para liberación del producto

// =================================================================

void setup() {
  Serial.begin(9600);
  
  pinMode(EN_PIN, OUTPUT); 
  digitalWrite(EN_PIN, LOW); 
  
  pinMode(GARRA_IN3, OUTPUT); 
  pinMode(GARRA_IN4, OUTPUT);
  detenerGarra();

  joint1.setMaxSpeed(1500.0); joint1.setAcceleration(800.0);
  joint2.setMaxSpeed(1500.0); joint2.setAcceleration(800.0);
  joint3.setMaxSpeed(400.0);  joint3.setAcceleration(200.0);

  joint1.setCurrentPosition(0);
  joint2.setCurrentPosition(0);
  joint3.setCurrentPosition(0);
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();
    if (comando == 'S') {
      ejecutarSecuencia(pasos_sano_X, pasos_sano_Y, Z_BAJA_CAJA_S);
    } 
    else if (comando == 'E') {
      ejecutarSecuencia(pasos_enfermo_X, pasos_enfermo_Y, Z_BAJA_CAJA_E);
    }
  }
}

// ==== Control Actuador Final ====
void cerrarGarra() { digitalWrite(GARRA_IN3, HIGH); digitalWrite(GARRA_IN4, LOW); delay(tiempo_cierre); detenerGarra(); }
void abrirGarra()  { digitalWrite(GARRA_IN3, LOW); digitalWrite(GARRA_IN4, HIGH); delay(tiempo_apertura); detenerGarra(); }
void detenerGarra() { digitalWrite(GARRA_IN3, LOW); digitalWrite(GARRA_IN4, LOW); }

// ==== Rutina Maestra ====
void ejecutarSecuencia(long targetX, long targetY, long pasosBajarCaja) {
  moverZ(Z_BAJA_FAJA);                   // 1. BAJA
  cerrarGarra();                         // 2. CIERRA garra
  moverZ(-Z_BAJA_FAJA);                  // 3. SUBE
  moverCoordinadoXY(targetX, targetY);   // 4. VIAJA
  moverZ(pasosBajarCaja);                // 5. BAJA
  abrirGarra();                          // 6. ABRE
  moverZ(-pasosBajarCaja);               // 7. SUBE
  moverCoordinadoXY(0, 0);               // 8. RETORNA
  
  Serial.println("R");                   // 9. AVISA fin de ciclo
}

void moverZ(long pasos) {
  joint3.move(pasos);
  joint3.runToPosition();
}

void moverCoordinadoXY(long targetX, long targetY) {
  long distX = abs(targetX - joint1.currentPosition());
  long distY = abs(targetY - joint2.currentPosition());
  float maxSpeed = 1500.0;
  
  if (distX >= distY && distX != 0) {
    joint1.setMaxSpeed(maxSpeed); joint2.setMaxSpeed(maxSpeed * ((float)distY / (float)distX));
  } else if (distY > distX && distY != 0) {
    joint2.setMaxSpeed(maxSpeed); joint1.setMaxSpeed(maxSpeed * ((float)distX / (float)distY));
  }
  
  joint1.moveTo(targetX); joint2.moveTo(targetY);
  while(joint1.distanceToGo() != 0 || joint2.distanceToGo() != 0) { joint1.run(); joint2.run(); }
  
  joint1.setMaxSpeed(maxSpeed); joint2.setMaxSpeed(maxSpeed);
}