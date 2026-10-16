/*********************************************
 * Unidad 11 · Ejemplo resuelto · la ruta exacta de la panadería
 * Vendedor viajero con restricciones MTZ (sin subrutas).
 * x[i][j] = 1 si el furgón va directo de i a j; 0 en otro caso.
 * u[i]    = posición del almacén i en la ruta (la base no lleva u).
 * Datos en u11_reparto_exacto.dat. Base abierta de ingeniería.
 *********************************************/

{string} Nodos = ...;
string Base = ...;
float d[Nodos][Nodos] = ...;            // km entre cada par de puntos
int n = card(Nodos);

dvar boolean x[Nodos][Nodos];           // 1 si va directo de i a j
dvar int+ u[Nodos];                     // posición de i en la ruta

minimize sum(i in Nodos, j in Nodos: i != j) d[i][j] * x[i][j];

subject to {
  forall(i in Nodos)
    SinLazo: x[i][i] == 0;
  forall(j in Nodos)
    Llega: sum(i in Nodos: i != j) x[i][j] == 1;
  forall(i in Nodos)
    Sale: sum(j in Nodos: j != i) x[i][j] == 1;
  forall(i in Nodos: i != Base)
    PosMin: u[i] >= 1;
  forall(i in Nodos: i != Base)
    PosMax: u[i] <= n - 1;
  forall(i in Nodos, j in Nodos: i != j && i != Base && j != Base)
    SinSubrutas: u[i] - u[j] + n * x[i][j] <= n - 1;
}

execute {
  var km = 0;
  for (var i in Nodos) for (var j in Nodos) km = km + d[i][j] * x[i][j];
  writeln("km = ", km);
  for (var i in Nodos) for (var j in Nodos) if (x[i][j] == 1) writeln("arco_", i, "_", j, " = 1");
}
