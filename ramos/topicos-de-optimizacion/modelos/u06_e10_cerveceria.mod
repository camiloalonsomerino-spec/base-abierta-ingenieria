/*********************************************
 * Unidad 6 · Ejercicio 6.10
 * Cervecería: habilitar dos líneas con costo fijo; la gran M es un dato
 * Datos en u06_e10_floja.dat o u06_e10_ajustada.dat. Base abierta de ingeniería.
 *********************************************/

{string} Lineas = ...;

float margen[Lineas] = ...;   // miles de pesos por hectolitro
float fijo[Lineas]   = ...;   // miles de pesos por habilitar la línea en el mes
float tope[Lineas]   = ...;   // hectolitros que la línea alcanza a hacer en el mes
float K              = ...;   // hectolitros de mosto disponibles en el mes
float M[Lineas]      = ...;   // gran M del acoplamiento

dvar float+  q[Lineas];       // hectolitros que se hacen en la línea en el mes
dvar boolean y[Lineas];       // 1 si se habilita la línea; 0 en otro caso

maximize sum(l in Lineas) (margen[l] * q[l] - fijo[l] * y[l]);

subject to {
  Mosto:
    sum(l in Lineas) q[l] <= K;
  forall(l in Lineas)
    Tope:
      q[l] <= tope[l];
  forall(l in Lineas)
    Acople:
      q[l] <= M[l] * y[l];
}

execute {
  for (var l in Lineas) {
    writeln("q[", l, "] = ", q[l]);
    writeln("y[", l, "] = ", y[l]);
  }
}
