/*********************************************
 * Unidad 1 - Heladeria Nieve del Sur (ejemplo resuelto)
 * Cuantos litros de cada helado producir en una semana
 * para ganar el mayor margen posible.
 * Datos en u01_heladeria.dat
 *********************************************/

{string} Helados = ...;            // conjunto I: los helados
{string} Recursos = ...;           // conjunto R: pasteurizacion y envasado

float margen[Helados] = ...;       // c_i: CLP por litro
float uso[Recursos][Helados] = ...;// a_ri: minutos del recurso r por litro de i
float cap[Recursos] = ...;         // b_r: minutos disponibles en la semana

{string} ConMinimo = ...;          // helados con un contrato que cumplir
float minimo[ConMinimo] = ...;     // litros comprometidos
{string} ConTope = ...;            // helados con demanda limitada
float tope[ConTope] = ...;         // litros que se pueden vender

dvar float+ x[Helados];            // x_i: litros del helado i (no negativos)

maximize sum(i in Helados) margen[i] * x[i];

subject to {
  forall(r in Recursos)
    ctRecurso: sum(i in Helados) uso[r][i] * x[i] <= cap[r];
  forall(i in ConMinimo)
    ctMinimo: x[i] >= minimo[i];
  forall(i in ConTope)
    ctTope: x[i] <= tope[i];
}

execute {
  writeln("z = ", cplex.getObjValue());
  for (var i in Helados) writeln("x_" + i + " = ", x[i]);
  for (var r in Recursos) writeln("holgura_" + r + " = ", ctRecurso[r].slack);
  for (var r in Recursos) writeln("dual_" + r + " = ", ctRecurso[r].dual);
}
