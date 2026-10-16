/*********************************************
 * Unidad 2 - Jugos prensados en frio (ejemplo resuelto)
 * Litros diarios de jugo verde (V) y de naranja-zanahoria (N)
 *********************************************/

{string} Jugos = {"verde", "naranja"};

float margen[Jugos] = [1740, 1450];   // CLP por litro
float prensa[Jugos] = [3, 2];         // minutos de prensa por litro
float fruta[Jugos]  = [1.2, 1.8];     // kg de fruta y verdura por litro

float prensaDisp  = 385;              // minutos de prensa al dia
float frutaDisp   = 207;              // kg que llegan cada manana
float topeVerde   = 103;              // litros de jugo verde que se venden
float botellas    = 178;              // botellas limpias al dia

dvar float+ x[Jugos];

maximize sum(j in Jugos) margen[j] * x[j];

subject to {
  ctPrensa:   sum(j in Jugos) prensa[j] * x[j] <= prensaDisp;
  ctFruta:    sum(j in Jugos) fruta[j] * x[j]  <= frutaDisp;
  ctVerde:    x["verde"] <= topeVerde;
  ctBotellas: sum(j in Jugos) x[j] <= botellas;
}

execute {
  writeln("z = ", cplex.getObjValue());
  for (var j in Jugos) writeln("x_" + j + " = ", x[j]);
  writeln("holgura_prensa = ", ctPrensa.slack);
  writeln("holgura_fruta = ", ctFruta.slack);
  writeln("holgura_verde = ", ctVerde.slack);
  writeln("holgura_botellas = ", ctBotellas.slack);
  writeln("dual_prensa = ", ctPrensa.dual);
  writeln("dual_fruta = ", ctFruta.dual);
}
