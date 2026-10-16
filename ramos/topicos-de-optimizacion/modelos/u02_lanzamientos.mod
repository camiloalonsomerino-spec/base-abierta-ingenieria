// Unidad 2 · caso Estampa Sur: qué productos nuevos lanzar
{string} Productos = ...;
float inversion[Productos] = ...;   // CLP de lanzamiento
float margen[Productos]    = ...;   // CLP de margen anual esperado
float presupuesto          = ...;   // CLP para lanzamientos

dvar boolean lanza[Productos];      // 1 si se lanza el producto p, 0 en otro caso

maximize sum(p in Productos) (margen[p] - inversion[p]) * lanza[p];

subject to {
  Presupuesto: sum(p in Productos) inversion[p] * lanza[p] <= presupuesto;
  Dependencia: lanza["parches"] <= lanza["banderines"];      // parches exige banderines
  Exclusion:   lanza["chaquetas"] + lanza["buzos"] <= 1;     // chaquetas y buzos: no ambos
}

execute {
  for (var p in Productos) writeln("lanza[", p, "] = ", lanza[p]);
}
