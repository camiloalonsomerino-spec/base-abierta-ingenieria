/*********************************************
 * Unidad 7 · Ejemplo resuelto
 * Panadería de barrio: bandejas de pan por semana
 * Datos en u07_panaderia.dat. Base abierta de ingeniería.
 *********************************************/

{string} Panes    = ...;
{string} Recursos = ...;

float margen[Panes]          = ...;   // CLP por bandeja
float uso[Recursos][Panes]   = ...;   // minutos o kg por bandeja
float disp[Recursos]         = ...;   // minutos o kg por semana
float tope[Panes]            = ...;   // bandejas que se venden como máximo

dvar float+ x[Panes];                 // bandejas a hornear en la semana

dexpr float Margen = sum(p in Panes) margen[p] * x[p];
dexpr float usado[r in Recursos] = sum(p in Panes) uso[r][p] * x[p];

maximize Margen;

subject to {
  forall(r in Recursos)
    Recurso:
      usado[r] <= disp[r];
  forall(p in Panes)
    Venta:
      x[p] <= tope[p];
}

execute {
  writeln("margen = ", Margen);
  for (var p in Panes) {
    writeln("x[", p, "] = ", x[p]);
    writeln("costo_reducido[", p, "] = ", x[p].reducedCost);
    writeln("dual_venta[", p, "] = ", Venta[p].dual);
  }
  for (var r in Recursos) {
    writeln("holgura[", r, "] = ", Recurso[r].slack);
    writeln("dual[", r, "] = ", Recurso[r].dual);
  }
}
