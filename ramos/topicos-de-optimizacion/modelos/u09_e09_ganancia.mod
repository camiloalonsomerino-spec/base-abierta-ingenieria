/*********************************************
 * Unidad 9 · Ejercicio 9.9 (pauta)
 * Transporte que maximiza la ganancia: cada planta recibe exactamente lo que pide.
 * Datos en u09_e09_ganancia.dat. Base abierta de ingeniería.
 *********************************************/

{string} Orig = ...;
{string} Dest = ...;
tuple Ruta { string o; string d; }
{Ruta} Prohibidas = ...;

int   oferta[Orig]        = ...;        // toneladas disponibles en cada huerto
int   pedido[Dest]        = ...;        // toneladas que compra cada planta
float ganancia[Orig][Dest] = ...;       // miles de CLP por tonelada

dvar float+ x[Orig][Dest];              // toneladas del huerto o a la planta d (0 si no se usa)

maximize sum(o in Orig, d in Dest) ganancia[o][d] * x[o][d];

subject to {
  forall(o in Orig)
    Oferta:    sum(d in Dest) x[o][d] <= oferta[o];
  forall(d in Dest)
    Pedido:    sum(o in Orig) x[o][d] == pedido[d];
  forall(<o, d> in Prohibidas)
    Prohibida: x[o][d] == 0;
}

execute {
  writeln("ganancia = ", cplex.getObjValue());
  for (var o in Orig) for (var d in Dest) if (x[o][d] > 0) writeln("x[", o, "][", d, "] = ", x[o][d]);
  for (var o in Orig) writeln("dual_oferta[", o, "] = ", Oferta[o].dual);
  for (var d in Dest) writeln("dual_pedido[", d, "] = ", Pedido[d].dual);
  for (var o in Orig) for (var d in Dest) if (x[o][d] == 0) writeln("cr[", o, "][", d, "] = ", x[o][d].reducedCost);
}
