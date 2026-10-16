/*********************************************
 * Unidad 8 · Ejercicio 8.10
 * Ruta más rápida con un tope de gasto en peajes.
 * Datos en u08_e10_presupuesto.dat. Base abierta de ingeniería.
 *********************************************/

tuple Arco { string i; string j; int tiempo; int peaje; }
{string} Nodos  = ...;
{Arco} Arcos    = ...;                  // minutos y peaje (pesos) de cada tramo
string origen   = ...;
string destino  = ...;
int presupuesto = ...;                  // pesos disponibles para peajes

int b[n in Nodos] = (n == origen) ? 1 : ((n == destino) ? -1 : 0);

dvar boolean x[Arcos];                  // 1 si la ruta usa el tramo; 0 en otro caso

dexpr int Minutos = sum(a in Arcos) a.tiempo * x[a];

minimize Minutos;

subject to {
  forall(n in Nodos)
    Balance:
      sum(a in Arcos: a.i == n) x[a] - sum(a in Arcos: a.j == n) x[a] == b[n];
  Peajes:                               // la restricción que Dijkstra no sabe manejar
    sum(a in Arcos) a.peaje * x[a] <= presupuesto;
}

execute {
  writeln("minutos = ", Minutos);
  for (var a in Arcos)
    if (x[a] > 0.5)
      writeln("x[", a.i, ",", a.j, "] = ", x[a]);
}
