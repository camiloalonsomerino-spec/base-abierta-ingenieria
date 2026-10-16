/*********************************************
 * Unidad 1 - Ejercicio 1.8, modelo corregido
 * Agricola: canastas chica y grande con verduras y minutos de armado
 *********************************************/

{string} Canastas = {"chica", "grande"};

float margen[Canastas]  = [3100, 6400];   // CLP por canasta
float kg[Canastas]      = [4, 9];         // kg de verduras por canasta
float minutos[Canastas] = [6, 10];        // minutos de armado por canasta

float verduras = 1800;                    // kg por semana (dato, no variable)
float armado   = 38 * 60;                 // 38 h pasadas a minutos

dvar float+ x[Canastas];                  // canastas de cada tipo (no negativas)

maximize sum(i in Canastas) margen[i] * x[i];

subject to {
  ctVerduras: sum(i in Canastas) kg[i] * x[i] <= verduras;
  ctArmado:   sum(i in Canastas) minutos[i] * x[i] <= armado;
}

execute {
  writeln("z = ", cplex.getObjValue());
  for (var i in Canastas) writeln("x_" + i + " = ", x[i]);
  writeln("dual_verduras = ", ctVerduras.dual);
  writeln("dual_armado = ", ctArmado.dual);
}
