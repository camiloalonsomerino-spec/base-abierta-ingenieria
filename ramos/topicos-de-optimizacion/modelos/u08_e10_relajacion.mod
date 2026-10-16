/*********************************************
 * Unidad 8 · Ejercicio 8.10 · relajación lineal
 * El mismo modelo de u08_e10_presupuesto.mod con x continua entre 0 y 1.
 * Datos en u08_e10_presupuesto.dat. Base abierta de ingeniería.
 *********************************************/

tuple Arco { string i; string j; int tiempo; int peaje; }
{string} Nodos  = ...;
{Arco} Arcos    = ...;
string origen   = ...;
string destino  = ...;
int presupuesto = ...;

int b[n in Nodos] = (n == origen) ? 1 : ((n == destino) ? -1 : 0);

dvar float x[Arcos] in 0..1;            // la única línea que cambia

dexpr float Minutos = sum(a in Arcos) a.tiempo * x[a];
dexpr float Peaje   = sum(a in Arcos) a.peaje * x[a];

minimize Minutos;

subject to {
  forall(n in Nodos)
    Balance:
      sum(a in Arcos: a.i == n) x[a] - sum(a in Arcos: a.j == n) x[a] == b[n];
  Peajes:
    Peaje <= presupuesto;
}

execute {
  writeln("minutos = ", Minutos);
  writeln("peaje = ", Peaje);
  for (var a in Arcos)
    if (x[a] > 0.000001)
      writeln("x[", a.i, ",", a.j, "] = ", x[a]);
}
