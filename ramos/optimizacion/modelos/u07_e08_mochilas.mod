/*********************************************
 * Unidad 7 · Ejercicio 7.8 (pauta)
 * Taller de mochilas: la planilla de Solver llevada a OPL
 *********************************************/

{string} Modelos  = ...;
{string} Procesos = ...;

float margen[Modelos]          = ...;   // CLP por mochila
float horas[Procesos][Modelos] = ...;   // h por mochila
float disp[Procesos]           = ...;   // h por mes
float tope_trekking            = ...;   // mochilas de trekking que se venden

dvar float+ x[Modelos];                 // «no negativas», como en Solver

dexpr float Margen = sum(m in Modelos) margen[m] * x[m];                   // la celda objetivo
dexpr float usado[p in Procesos] = sum(m in Modelos) horas[p][m] * x[m];   // SUMAPRODUCTO

maximize Margen;

subject to {
  forall(p in Procesos)
    Horas:
      usado[p] <= disp[p];
  Trekking:
    x["trekking"] <= tope_trekking;
}

execute {
  writeln("margen = ", Margen);
  for (var m in Modelos) {
    writeln("x[", m, "] = ", x[m]);
    writeln("costo_reducido[", m, "] = ", x[m].reducedCost);
  }
  for (var p in Procesos) {
    writeln("usado[", p, "] = ", usado[p]);
    writeln("dual[", p, "] = ", Horas[p].dual);
  }
  writeln("holgura_trekking = ", Trekking.slack);
}
