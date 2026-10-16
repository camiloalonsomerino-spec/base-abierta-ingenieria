/*********************************************
 * Unidad 4 · Ejercicio 4.6
 * Corte de piezas por patrones: cuántas tablas cortar con cada patrón.
 * Los patrones maximales están enumerados en u04_e06_corte.dat.
 *********************************************/

{string} Piezas   = ...;
{string} Patrones = ...;

int a[Patrones][Piezas] = ...;     // piezas de cada tipo que salen con un patrón
int pide[Piezas]        = ...;     // piezas pedidas

dvar int+ x[Patrones];             // tablas que se cortan con el patrón p

dexpr int Tablas = sum(p in Patrones) x[p];

minimize Tablas;

subject to {
  forall(i in Piezas)
    Pedido:
      sum(p in Patrones) a[p][i] * x[p] >= pide[i];
}

execute {
  writeln("tablas = ", Tablas);
  for (var p in Patrones)
    if (x[p] > 0) writeln("x[", p, "] = ", x[p]);
}
