// Unidad 1 · caso Estampa Sur: la mezcla de la unidad 4 de Optimización, en cajas de 24
{string} Prendas  = ...;
{string} Recursos = ...;

int   caja                   = ...;   // prendas por caja
float margen[Prendas]        = ...;   // CLP por prenda
float uso[Recursos][Prendas] = ...;   // segundos o gramos por prenda
float cap[Recursos]          = ...;   // segundos o gramos por semana
float demanda[Prendas]       = ...;   // prendas por semana, máximo

dvar int+ cajas[Prendas];             // cajas de 24 prendas que se producen en la semana

dexpr float Margen = sum(i in Prendas) caja * margen[i] * cajas[i];
maximize Margen;

subject to {
  forall(r in Recursos)
    Capacidad: sum(i in Prendas) caja * uso[r][i] * cajas[i] <= cap[r];
  forall(i in Prendas)
    Demanda: caja * cajas[i] <= demanda[i];
}

execute {
  writeln("margen = ", Margen);
  for (var i in Prendas) writeln("cajas[", i, "] = ", cajas[i]);
}
