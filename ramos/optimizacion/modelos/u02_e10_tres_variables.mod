/*********************************************
 * Unidad 2 - Ejercicio 2.10
 * Tres conservas, tres lineas de 24 horas: el optimo que el
 * recorrido de vertices encuentra a mano, ahora con el solver.
 *********************************************/

range Productos = 1..3;
range Lineas = 1..3;

float c[Productos] = [5, 4, 6];
float a[Lineas][Productos] = [[1, 1, 2],
                              [2, 1, 1],
                              [1, 2, 1]];
float b[Lineas] = [24, 24, 24];

dvar float+ x[Productos];

maximize sum(j in Productos) c[j] * x[j];

subject to {
  forall(i in Lineas)
    ctLinea: sum(j in Productos) a[i][j] * x[j] <= b[i];
}

execute {
  writeln("z = ", cplex.getObjValue());
  for (var j in Productos) writeln("x_" + j + " = ", x[j]);
  for (var i in Lineas) writeln("dual_" + i + " = ", ctLinea[i].dual);
}
