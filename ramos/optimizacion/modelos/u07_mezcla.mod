/*********************************************
 * Unidad 7 · Implementación en OPL
 * Estampa Sur: mezcla semanal de cinco prendas (el modelo de la unidad 4)
 * Datos en u07_mezcla.dat. Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
{string} Prendas  = ...;          // lo que se puede producir
{string} Recursos = ...;          // estampado, planchado y tinta

// PARÁMETROS
float margen[Prendas]           = ...;   // CLP por unidad
float uso[Recursos][Prendas]    = ...;   // segundos o gramos por unidad
float cap[Recursos]             = ...;   // segundos o gramos por semana
float demanda[Prendas]          = ...;   // unidades por semana

// VARIABLES DE DECISIÓN
dvar float+ x[Prendas];                  // unidades a producir en la semana

// EXPRESIONES (se calculan, no se deciden)
dexpr float Margen = sum(i in Prendas) margen[i] * x[i];
dexpr float usado[r in Recursos] = sum(i in Prendas) uso[r][i] * x[i];

// OBJETIVO
maximize Margen;

// RESTRICCIONES
subject to {
  forall(r in Recursos)
    Capacidad:
      usado[r] <= cap[r];

  forall(i in Prendas)
    Demanda:
      x[i] <= demanda[i];
}

// SALIDA: una línea «clave = valor» por resultado
execute {
  writeln("margen = ", Margen);
  for (var i in Prendas)
    writeln("x[", i, "] = ", x[i]);
  for (var r in Recursos) {
    writeln("usado[", r, "] = ", usado[r]);
    writeln("holgura[", r, "] = ", Capacidad[r].slack);
    writeln("dual[", r, "] = ", Capacidad[r].dual);
  }
  for (var i in Prendas) {
    writeln("dual_demanda[", i, "] = ", Demanda[i].dual);
    writeln("costo_reducido[", i, "] = ", x[i].reducedCost);
  }
}
