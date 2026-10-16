/*********************************************
 * Unidad 7 · Ejercicio 7.6 (pauta)
 * Empanadas congeladas: cajas por semana en cuatro semanas, con inventario
 *********************************************/

int T = ...;
range Semanas = 1..T;

float demanda[Semanas] = ...;   // cajas por semana
float inv0             = ...;   // cajas en la cámara de frío al empezar
float cap_regular      = ...;   // cajas por semana en turno normal
float cap_extra        = ...;   // cajas por semana en turno extra
float c_regular        = ...;   // CLP por caja
float c_extra          = ...;   // CLP por caja
float c_inv            = ...;   // CLP por caja guardada una semana

dvar float+ r[Semanas];         // producción en turno normal
dvar float+ e[Semanas];         // producción en turno extra
dvar float+ I[Semanas];         // inventario al cierre de la semana

minimize sum(t in Semanas) (c_regular*r[t] + c_extra*e[t] + c_inv*I[t]);

subject to {
  forall(t in Semanas: t == 1)
    Balance1:
      inv0 + r[t] + e[t] - I[t] == demanda[t];
  forall(t in Semanas: t > 1)
    Balance:
      I[t-1] + r[t] + e[t] - I[t] == demanda[t];
  forall(t in Semanas) {
    Regular: r[t] <= cap_regular;
    Extra:   e[t] <= cap_extra;
  }
}

execute {
  writeln("costo = ", cplex.getObjValue());
  for (var t in Semanas) {
    writeln("r[", t, "] = ", r[t]);
    writeln("e[", t, "] = ", e[t]);
    writeln("I[", t, "] = ", I[t]);
  }
  writeln("dual_balance[1] = ", Balance1[1].dual);
  for (var t = 2; t <= T; t++)
    writeln("dual_balance[", t, "] = ", Balance[t].dual);
}
