/*********************************************
 * Unidad 7 · Ejercicio 7.5 (pauta: la versión compacta)
 * Fábrica de mermeladas: lotes por semana
 *********************************************/

{string} Sabores  = ...;
{string} Recursos = ...;

float margen[Sabores]           = ...;   // CLP por lote
float uso[Recursos][Sabores]    = ...;   // minutos o kg por lote
float disp[Recursos]            = ...;   // minutos o kg por semana

dvar float+ lotes[Sabores];

dexpr float usado[r in Recursos] = sum(s in Sabores) uso[r][s] * lotes[s];

maximize sum(s in Sabores) margen[s] * lotes[s];

subject to {
  forall(r in Recursos)
    Disponible:
      usado[r] <= disp[r];
}

execute {
  writeln("margen = ", cplex.getObjValue());
  for (var s in Sabores)
    writeln("lotes[", s, "] = ", lotes[s]);
  for (var r in Recursos)
    writeln("usado[", r, "] = ", usado[r]);
  for (var r in Recursos)
    writeln("dual[", r, "] = ", Disponible[r].dual);
  for (var s in Sabores)
    writeln("costo_reducido[", s, "] = ", lotes[s].reducedCost);
}
