/*********************************************
 * Unidad 12 · Análisis de sensibilidad
 * Mezcla de producción con topes de demanda (la forma de la unidad 4).
 * Se usa con:
 *   u12_estampa.dat        (caso integrador: Estampa Sur, una semana)
 *   u12_chocolateria.dat   (ejercicio 12.7: con una caja nueva)
 * Con «oplrun -e modelo.lp» se exporta el modelo y el optimizador
 * interactivo de CPLEX entrega los rangos («display sensitivity»).
 * Base abierta de ingeniería.
 *********************************************/

{string} Productos = ...;
{string} Recursos  = ...;

float margen[Productos]         = ...;   // CLP por unidad
float uso[Recursos][Productos]  = ...;   // consumo por unidad
float cap[Recursos]             = ...;   // disponible en el período
float demanda[Productos]        = ...;   // tope de venta

dvar float+ x[Productos];

dexpr float Margen = sum(p in Productos) margen[p] * x[p];

maximize Margen;

subject to {
  forall(r in Recursos)
    Capacidad:
      sum(p in Productos) uso[r][p] * x[p] <= cap[r];
  forall(p in Productos)
    Demanda:
      x[p] <= demanda[p];
}

execute {
  writeln("margen = ", Margen);
  for (var p in Productos) {
    writeln("x[", p, "] = ", x[p]);
    writeln("costo_reducido[", p, "] = ", x[p].reducedCost);
    writeln("dual_demanda[", p, "] = ", Demanda[p].dual);
  }
  for (var r in Recursos) {
    writeln("holgura[", r, "] = ", Capacidad[r].slack);
    writeln("dual[", r, "] = ", Capacidad[r].dual);
  }
}
