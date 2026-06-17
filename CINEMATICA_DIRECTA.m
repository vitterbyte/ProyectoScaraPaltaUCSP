%% ==========================================================================
% PROYECTO: Clasificador Robótico SCARA para Paltas Hass
% INSTITUCIÓN: UCSP - Ingeniería Mecatrónica
% MÓDULO: Análisis de Cinemática Directa (FK SCARA RPRR)
% ==========================================================================

clc; clear;

%% ===== Parámetros DH - Numéricos =====
L2 = 228; 
L3 = 57.5; 
L4 = 144; 
L5 = 17.5;
offset_d1 = 97;

% ----- Conjunto articular de ENTRADA (Simulado) -----
th1_in = deg2rad(30); % Ejemplo de ángulo ingresado
th2_in = deg2rad(45);
th3_in = deg2rad(15);
L1_in  = 50;          % Posición prismática Z

% Tabla DH: [theta  d          a    alpha]
DH = [ th1_in   L1_in+offset_d1  0     0;
       0        0                L2    0;
       th2_in  -L3               L4    0;
       th3_in  -L5               0     pi]; 

%% ===== Utilidades de Matriz de Transformación Homogénea =====
dh = @(th,d,a,al) [cos(th) -sin(th)*cos(al)  sin(th)*sin(al)  a*cos(th);
                   sin(th)  cos(th)*cos(al) -cos(th)*sin(al)  a*sin(th);
                   0        sin(al)          cos(al)          d;
                   0        0                0                1];

%% ===== CINEMÁTICA DIRECTA =====
A1 = dh(DH(1,1),DH(1,2),DH(1,3),DH(1,4));
A2 = dh(DH(2,1),DH(2,2),DH(2,3),DH(2,4));
A3 = dh(DH(3,1),DH(3,2),DH(3,3),DH(3,4));
A4 = dh(DH(4,1),DH(4,2),DH(4,3),DH(4,4));

T  = A1*A2*A3*A4;
px = T(1,4);  py = T(2,4);  pz = T(3,4);
phi = atan2(T(2,1), T(1,1));    % yaw (plano XY)

%% ===== Resultados FK =====
fprintf('======= FK (Matriz de Transformación Homogénea) =======\n');
disp(T);
fprintf('px=%.3f mm | py=%.3f mm | pz=%.3f mm | phi=%.6f rad (%.2f°)\n\n', ...
        px, py, pz, phi, rad2deg(phi));