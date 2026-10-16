/*********************************************
 * Unidad 1 - Ejercicio 1.10
 * Cooperativa de pescadores: cuantos kg de cada especie
 * destinar a cada proceso en una semana.
 * Datos en u01_e10_cooperativa.dat
 *********************************************/

{string} Especies = ...;                 // conjunto E
{string} Procesos = ...;                 // conjunto P

float captura[Especies] = ...;           // Q_e: kg de pescado entero disponibles
float capacidad[Procesos] = ...;         // K_p: kg de pescado entero que procesa cada linea
float rend[Especies][Procesos] = ...;    // r_ep: kg de producto por kg de pescado entero
float precio[Especies][Procesos] = ...;  // v_ep: CLP por kg de producto
float costo[Procesos] = ...;             // c_p: CLP por kg de pescado entero procesado

// margen por kg de pescado entero: se calcula, no se digita
dexpr float m[e in Especies][p in Procesos] = precio[e][p] * rend[e][p] - costo[p];

dvar float+ x[Especies][Procesos];       // x_ep: kg de la especie e al proceso p

maximize sum(e in Especies, p in Procesos) m[e][p] * x[e][p];

subject to {
  forall(e in Especies)
    ctCaptura: sum(p in Procesos) x[e][p] <= captura[e];
  forall(p in Procesos)
    ctLinea: sum(e in Especies) x[e][p] <= capacidad[p];
}

execute {
  writeln("z = ", cplex.getObjValue());
  for (var e in Especies) for (var p in Procesos) writeln("x_" + e + "_" + p + " = ", x[e][p]);
  for (var e in Especies) writeln("dual_" + e + " = ", ctCaptura[e].dual);
  for (var p in Procesos) writeln("dual_" + p + " = ", ctLinea[p].dual);
}
