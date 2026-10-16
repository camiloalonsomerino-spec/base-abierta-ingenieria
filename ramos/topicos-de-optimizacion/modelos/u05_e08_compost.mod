/*********************************************
 * Unidad 5 · Ejercicio 5.8
 * Planta de compost: turnos completos (enteros) y toneladas compradas (continuas)
 * Base abierta de ingeniería.
 *********************************************/

dvar int+   turnos;      // turnos completos de volteo que se programan en la semana
dvar float+ toneladas;   // toneladas de material verde que se compran en la semana

maximize 120 * turnos + 70 * toneladas;   // miles de pesos

subject to {
  Cargador: 6 * turnos + 2 * toneladas <= 29;   // horas de cargador frontal
  Cancha:   6 * turnos + 8 * toneladas <= 45;   // metros de cancha de secado
}

execute {
  writeln("turnos = ", turnos);
  writeln("toneladas = ", toneladas);
}
