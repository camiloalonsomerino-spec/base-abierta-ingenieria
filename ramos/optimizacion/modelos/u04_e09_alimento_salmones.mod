/*********************************************
 * Unidad 4 · Ejercicio 4.9 (pauta) · alimento para salmones
 * Cuatro ingredientes, dos nutrientes y dos alimentos, en forma compacta.
 * Ojo con las unidades: x en toneladas, costo en CLP por kg (por eso el 1000).
 * Datos en u04_e09_alimento_salmones.dat. Base abierta de ingeniería.
 *********************************************/

{string} Ingredientes = ...;
{string} Aceites      = ...;                 // subconjunto de Ingredientes
{string} Nutrientes   = ...;
{string} Alimentos    = ...;

float aporte[Ingredientes][Nutrientes] = ...;   // % del nutriente en el ingrediente
float costo[Ingredientes] = ...;                // CLP por kg
float disp[Ingredientes]  = ...;                // t por semana (10000 = sin tope)
float dem[Alimentos]      = ...;                // t por semana, exactas
float minimo[Alimentos][Nutrientes] = ...;      // % mínimo
float maximo[Alimentos][Nutrientes] = ...;      // % máximo (100 = sin tope)
float omega = ...;                              // fracción mínima de aceite de pescado en el aceite
float harina_min = ...;                         // fracción mínima de harina de pescado en el de inicio

dvar float+ x[Ingredientes][Alimentos];         // toneladas del ingrediente i en el alimento j

dexpr float t[j in Alimentos] = sum(i in Ingredientes) x[i][j];

minimize sum(i in Ingredientes, j in Alimentos) 1000 * costo[i] * x[i][j];   // CLP por semana

subject to {
  forall(j in Alimentos)
    Demanda: t[j] == dem[j];

  forall(j in Alimentos, k in Nutrientes)
    Minimo: sum(i in Ingredientes) aporte[i][k] * x[i][j] >= minimo[j][k] * t[j];

  forall(j in Alimentos, k in Nutrientes: maximo[j][k] < 100)
    Maximo: sum(i in Ingredientes) aporte[i][k] * x[i][j] <= maximo[j][k] * t[j];

  forall(j in Alimentos)
    Omega: x["aceite_pescado"][j] >= omega * sum(i in Aceites) x[i][j];

  HarinaInicio: x["harina_pescado"]["inicio"] >= harina_min * t["inicio"];

  forall(i in Ingredientes: disp[i] < 10000)
    Disponibilidad: sum(j in Alimentos) x[i][j] <= disp[i];
}

execute {
  writeln("costo = ", cplex.getObjValue());
  for (var i in Ingredientes)
    for (var j in Alimentos)
      writeln("x_", i, "_", j, " = ", x[i][j]);
}
