%% ==========================================================================
% PROYECTO: Clasificador Robótico SCARA para Paltas Hass
% INSTITUCIÓN: UCSP - Ingeniería Mecatrónica
% MÓDULO: Análisis de Cinemática Inversa (IK SCARA RPRR)
% ==========================================================================

clear; clc;

%% ====== Parámetros geométricos (DH) ======
L2 = 228;      % a2 (Hombro)
L3 = 57.5;     % |d3| 
L4 = 144;      % a3 (Codo)
L5 = 17.5;     % |d4| 
offset_d1 = 97;

%% ====== Pose Deseada del TCP ======
px  = 334.847;      % mm
py  = 52.7;         % mm
pz  = 122;          % mm
phi = deg2rad(30);  % Orientación en el plano (yaw) en rad

%% ====== Cálculo 2R en el plano XY ======
a2 = L2; 
a3 = L4;
r2 = px^2 + py^2;
c3 = (r2 - a2^2 - a3^2) / (2*a2*a3);

% Manejo de tolerancias numéricas
if c3 > 1,  c3 = 1;  end
if c3 < -1, c3 = -1; end

s3_pos =  sqrt(max(0, 1 - c3^2));   % Codo-abajo
s3_neg = -s3_pos;                   % Codo-arriba

theta3_1 = atan2(s3_pos, c3);
theta3_2 = atan2(s3_neg, c3);

theta1_1 = atan2(py, px) - atan2(a3*sin(theta3_1), a2 + a3*cos(theta3_1));
theta1_2 = atan2(py, px) - atan2(a3*sin(theta3_2), a2 + a3*cos(theta3_2));

% Normalización a [-pi, pi]
normAng = @(ang) mod(ang + pi, 2*pi) - pi;
theta1_1 = normAng(theta1_1);
theta1_2 = normAng(theta1_2);
theta3_1 = normAng(theta3_1);
theta3_2 = normAng(theta3_2);

%% ====== Muñeca ======
theta4_1 = normAng(phi - theta1_1 - theta3_1 + pi);
theta4_2 = normAng(phi - theta1_2 - theta3_2 + pi);

%% ====== Prismática vertical: resolver L1 ======
L1_sol = pz - offset_d1 + L3 + L5;

%% ====== Mostrar resultados en Consola ======
fprintf('=== Solución IK SCARA (dos ramas) ===\n');
fprintf('Entrada objetivo: px=%.3f mm, py=%.3f mm, pz=%.3f mm, phi=%.3f rad\n', px, py, pz, phi);
fprintf('L1 (prismática) = %.3f mm\n\n', L1_sol);

fprintf('--- Rama 1 (codo-abajo) ---\n');
fprintf('theta1 = %+8.5f rad  (%+8.3f deg)\n', theta1_1, rad2deg(theta1_1));
fprintf('theta3 = %+8.5f rad  (%+8.3f deg)\n', theta3_1, rad2deg(theta3_1));

fprintf('\n--- Rama 2 (codo-arriba) ---\n');
fprintf('theta1 = %+8.5f rad  (%+8.3f deg)\n', theta1_2, rad2deg(theta1_2));
fprintf('theta3 = %+8.5f rad  (%+8.3f deg)\n', theta3_2, rad2deg(theta3_2));