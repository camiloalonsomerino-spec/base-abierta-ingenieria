/*********************************************
 * Unidad 10 · Ejemplo · chocolatería (el primal)
 * Lotes de bombones y de tabletas con horas de templado y de empaque y un tope
 * de lotes de bombones. El .dual de cada restricción es el precio sombra del recurso.
 *********************************************/
{string} Productos = {"bombones", "tabletas"};
{string} Recursos  = {"templado", "empaque"};
float margen[Productos] = [8600, 4900];            // CLP por lote
float uso[Recursos][Productos] = [[2, 1], [1, 1]]; // horas por lote
float cap[Recursos] = [60, 40];                    // horas por semana
float topeBombones = 25;                           // lotes de bombones que se venden como máximo

dvar float+ x[Productos];

maximize sum(p in Productos) margen[p] * x[p];

subject to {
  forall(r in Recursos)
    ctCap: sum(p in Productos) uso[r][p] * x[p] <= cap[r];
  ctBombones: x["bombones"] <= topeBombones;
}

execute {
  writeln("x_bombones = ", x["bombones"]);
  writeln("x_tabletas = ", x["tabletas"]);
  writeln("y_templado = ", ctCap["templado"].dual);
  writeln("y_empaque = ", ctCap["empaque"].dual);
  writeln("y_bombones = ", ctBombones.dual);
}
