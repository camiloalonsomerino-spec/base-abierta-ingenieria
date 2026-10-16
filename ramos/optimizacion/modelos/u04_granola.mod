/*********************************************
 * Unidad 4 · Ejemplo resuelto · mezcla de granola
 * Tres ingredientes se mezclan en dos granolas con exigencias de proteína y azúcar.
 * Variable con dos índices: x[i][j] = kg del ingrediente i que van a la granola j.
 * Datos en u04_granola.dat. Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
{string} Ingredientes = ...;
{string} Productos    = ...;
{string} Atributos    = ...;                 // proteína y azúcar

// PARÁMETROS
float contenido[Ingredientes][Atributos] = ...;   // % del atributo en el ingrediente
float costo[Ingredientes]   = ...;                // CLP por kg
float disp[Ingredientes]    = ...;                // kg por semana
float precio[Productos]     = ...;                // CLP por kg de granola
float demanda[Productos]    = ...;                // kg por semana, máximo
float minimo[Productos][Atributos] = ...;         // % mínimo en la granola
float maximo[Productos][Atributos] = ...;         // % máximo (100 = sin tope)

// VARIABLES
dvar float+ x[Ingredientes][Productos];

// EXPRESIONES
dexpr float kilos[j in Productos] = sum(i in Ingredientes) x[i][j];
dexpr float Margen = sum(j in Productos) precio[j] * kilos[j]
                   - sum(i in Ingredientes, j in Productos) costo[i] * x[i][j];

maximize Margen;

subject to {
  forall(i in Ingredientes)
    Disponibilidad: sum(j in Productos) x[i][j] <= disp[i];

  forall(j in Productos)
    Demanda: kilos[j] <= demanda[j];

  // proporción: se multiplica por kilos[j] en vez de dividir (así queda lineal)
  forall(j in Productos, a in Atributos)
    Minimo: sum(i in Ingredientes) contenido[i][a] * x[i][j] >= minimo[j][a] * kilos[j];

  forall(j in Productos, a in Atributos: maximo[j][a] < 100)
    Maximo: sum(i in Ingredientes) contenido[i][a] * x[i][j] <= maximo[j][a] * kilos[j];
}

execute {
  writeln("margen = ", Margen);
  for (var i in Ingredientes)
    for (var j in Productos)
      writeln("x_", i, "_", j, " = ", x[i][j]);
  for (var i in Ingredientes)
    writeln("dual_disp_", i, " = ", Disponibilidad[i].dual);
  for (var j in Productos)
    writeln("dual_demanda_", j, " = ", Demanda[j].dual);
}
