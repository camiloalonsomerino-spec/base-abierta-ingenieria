/*********************************************
 * Unidad 7 · Ejercicio 7.4 (la salida que se lee)
 * Carpintería: muebles por mes
 *********************************************/

{string} Muebles  = ...;
{string} Procesos = ...;

float margen[Muebles]          = ...;   // CLP por mueble
float uso[Procesos][Muebles]   = ...;   // horas o litros por mueble
float cap[Procesos]            = ...;   // horas o litros por mes
float tope_sillas              = ...;   // sillas que se venden como máximo

dvar float+ x[Muebles];

maximize sum(m in Muebles) margen[m] * x[m];

subject to {
  forall(p in Procesos)
    Capacidad:
      sum(m in Muebles) uso[p][m] * x[m] <= cap[p];
  Sillas:
    x["silla"] <= tope_sillas;
}

execute {
  writeln("margen = ", cplex.getObjValue());
  for (var m in Muebles)
    writeln("x[", m, "] = ", x[m]);
  for (var m in Muebles)
    writeln("costo_reducido[", m, "] = ", x[m].reducedCost);
  for (var p in Procesos)
    writeln("holgura[", p, "] = ", Capacidad[p].slack);
  for (var p in Procesos)
    writeln("dual[", p, "] = ", Capacidad[p].dual);
  writeln("dual_sillas = ", Sillas.dual);
}
