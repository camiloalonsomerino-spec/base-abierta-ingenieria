/*********************************************
 * Unidad 11 · Holgura complementaria
 * Mezcla de producción genérica: maximizar el margen con recursos limitados.
 * Se usa con tres archivos de datos:
 *   u11_tostaduria.dat  (ejemplo resuelto)
 *   u11_quesos.dat      (ejercicio 11.5)
 *   u11_ceramica.dat    (ejercicio 11.9, solución degenerada)
 * Imprime holguras, duales y costos reducidos para aplicar holgura complementaria.
 * Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
{string} Productos = ...;
{string} Recursos  = ...;

// PARÁMETROS
float margen[Productos]          = ...;   // CLP por unidad
float uso[Recursos][Productos]   = ...;   // consumo de cada recurso por unidad
float cap[Recursos]              = ...;   // disponibilidad del período

// VARIABLES DE DECISIÓN
dvar float+ x[Productos];

dexpr float Margen = sum(p in Productos) margen[p] * x[p];

maximize Margen;

subject to {
  forall(r in Recursos)
    Capacidad:
      sum(p in Productos) uso[r][p] * x[p] <= cap[r];
}

// SALIDA: una línea «clave = valor» por resultado
execute {
  writeln("margen = ", Margen);
  for (var p in Productos) {
    writeln("x[", p, "] = ", x[p]);
    writeln("costo_reducido[", p, "] = ", x[p].reducedCost);
  }
  for (var r in Recursos) {
    writeln("holgura[", r, "] = ", Capacidad[r].slack);
    writeln("dual[", r, "] = ", Capacidad[r].dual);
  }
}
