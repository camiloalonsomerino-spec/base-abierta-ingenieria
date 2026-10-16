/*********************************************
 * Unidad 10 · Ejemplo · chocolatería (el dual)
 * Un comprador quiere quedarse con las horas de templado, las de empaque y el
 * derecho a vender bombones. Busca el pago total mínimo que la chocolatería
 * aceptaría: cada producto tiene que «valer» en recursos al menos su margen.
 *********************************************/
{string} Productos = {"bombones", "tabletas"};
{string} Recursos  = {"templado", "empaque"};
float margen[Productos] = [8600, 4900];
float uso[Recursos][Productos] = [[2, 1], [1, 1]];
float cap[Recursos] = [60, 40];
float topeBombones = 25;

dvar float+ y[Recursos];      // CLP por hora de cada recurso
dvar float+ u;                // CLP por lote de demanda de bombones

minimize sum(r in Recursos) cap[r] * y[r] + topeBombones * u;

subject to {
  ctBombones: sum(r in Recursos) uso[r]["bombones"] * y[r] + u >= margen["bombones"];
  ctTabletas: sum(r in Recursos) uso[r]["tabletas"] * y[r]     >= margen["tabletas"];
}

execute {
  writeln("y_templado = ", y["templado"]);
  writeln("y_empaque = ", y["empaque"]);
  writeln("y_bombones = ", u);
  writeln("x_bombones = ", ctBombones.dual);
  writeln("x_tabletas = ", ctTabletas.dual);
}
