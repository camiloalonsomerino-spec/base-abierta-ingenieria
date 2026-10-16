/*********************************************
 * Unidad 7 · Ejercicio 7.7 (pauta)
 * Lavandería industrial: qué lavadoras encender esta semana
 * Modelo entero mixto: hay variables boolean.
 *********************************************/

{string} Lavadoras = ...;

float cap[Lavadoras]   = ...;   // kg por semana si está encendida
float fijo[Lavadoras]  = ...;   // CLP por encenderla la semana
float cvar[Lavadoras]  = ...;   // CLP por kg lavado
float D                = ...;   // kg que hay que lavar

dvar float+ kg[Lavadoras];      // kg que lava cada máquina
dvar boolean y[Lavadoras];      // 1 si se enciende

minimize sum(l in Lavadoras) (fijo[l]*y[l] + cvar[l]*kg[l]);

subject to {
  Pedido:
    sum(l in Lavadoras) kg[l] >= D;
  forall(l in Lavadoras)
    Encendida:
      kg[l] <= cap[l] * y[l];
}

execute {
  writeln("costo = ", cplex.getObjValue());
  for (var l in Lavadoras) {
    writeln("y[", l, "] = ", y[l]);
    writeln("kg[", l, "] = ", kg[l]);
  }
}
