// Unidad 1 · ejemplo: toldos y módulos de escenario para la temporada
range Equipos = 1..2;                        // 1 = toldo, 2 = módulo de escenario
float margen[Equipos] = [1300000, 600000];   // CLP por temporada y por unidad
float bodega[Equipos] = [2, 7];              // m² de bodega por unidad
float compra[Equipos] = [9, 4];              // millones de CLP por unidad

dvar int+ x[Equipos];                        // unidades que se compran de cada equipo

maximize sum(e in Equipos) margen[e] * x[e];

subject to {
  Bodega:      sum(e in Equipos) bodega[e] * x[e] <= 48;
  Presupuesto: sum(e in Equipos) compra[e] * x[e] <= 41;
}

execute {
  for (var e in Equipos) writeln("x[", e, "] = ", x[e]);
}
