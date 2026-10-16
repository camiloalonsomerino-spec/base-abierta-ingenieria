/*********************************************
 * Unidad 8 · Flujo máximo
 * Cuánto se puede mandar de la fuente al sumidero sin pasar la capacidad de ningún arco.
 * Datos en u08_flujo_maximo.dat (caso) o u08_festival.dat (ejemplo).
 * Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS Y PARÁMETROS
tuple Arco { string i; string j; int cap; }
{string} Nodos = ...;
{Arco} Arcos   = ...;                   // arcos dirigidos con su capacidad
string fuente   = ...;
string sumidero = ...;

// VARIABLES DE DECISIÓN
dvar float+ x[Arcos];                   // flujo que pasa por el arco (i, j)
dvar float+ F;                          // flujo total de la fuente al sumidero

// OBJETIVO
maximize F;

// RESTRICCIONES
subject to {
  forall(a in Arcos)
    Capacidad:
      x[a] <= a.cap;
  forall(n in Nodos: n == fuente)
    Fuente:
      sum(a in Arcos: a.i == n) x[a] - sum(a in Arcos: a.j == n) x[a] == F;
  forall(n in Nodos: n != fuente && n != sumidero)
    Conservacion:                       // en un nodo intermedio entra lo mismo que sale
      sum(a in Arcos: a.i == n) x[a] - sum(a in Arcos: a.j == n) x[a] == 0;
  forall(n in Nodos: n == sumidero)
    Sumidero:
      sum(a in Arcos: a.i == n) x[a] - sum(a in Arcos: a.j == n) x[a] == -F;
}

// SALIDA: flujo y precio sombra de la capacidad de cada arco
execute {
  writeln("flujo = ", F);
  for (var a in Arcos) {
    writeln("x[", a.i, ",", a.j, "] = ", x[a]);
    writeln("dual[", a.i, ",", a.j, "] = ", Capacidad[a].dual);
  }
}
