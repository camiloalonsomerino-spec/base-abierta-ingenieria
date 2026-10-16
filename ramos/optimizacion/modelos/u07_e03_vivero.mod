/*********************************************
 * Unidad 7 · Ejercicio 7.3 (pauta: el código ya corregido)
 * Vivero: macetas de lavanda, romero y suculentas por semana
 *********************************************/

{string} Plantas  = ...;
{string} Recursos = ...;

float margen[Plantas]          = ...;   // CLP por maceta
float uso[Recursos][Plantas]   = ...;   // minutos o litros por maceta
float cap[Recursos]            = ...;   // minutos o litros por semana
float demanda[Plantas]         = ...;   // macetas por semana

dvar float+ x[Plantas];

maximize sum(p in Plantas) margen[p] * x[p];

subject to {
  forall(r in Recursos)
    Capacidad:
      sum(p in Plantas) uso[r][p] * x[p] <= cap[r];
  forall(p in Plantas)
    Demanda:
      x[p] <= demanda[p];
}

execute {
  writeln("margen = ", cplex.getObjValue());
  for (var p in Plantas)
    writeln("x[", p, "] = ", x[p]);
  for (var r in Recursos)
    writeln("dual[", r, "] = ", Capacidad[r].dual);
  for (var p in Plantas)
    writeln("dual_demanda[", p, "] = ", Demanda[p].dual);
}
