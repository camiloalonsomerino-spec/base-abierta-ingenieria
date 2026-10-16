/*********************************************
 * Unidad 6 · Modelos con varios objetivos (ejemplo resuelto)
 * Huerto familiar: programación por metas. Dos metas (margen mínimo y agua
 * máxima) con variables de desviación; se minimiza la suma ponderada de las
 * desviaciones NO deseadas, cada una dividida por su meta (en términos
 * relativos). Datos en u06_huerto_metas.dat. Base abierta de ingeniería.
 *********************************************/

// PARÁMETROS
float margen[1..2]  = ...;   // $ por m² (tomate, lechuga)
float agua[1..2]    = ...;   // litros por m²
float trabajo[1..2] = ...;   // minutos por m²
float superficie = ...;      // m²
float minutos    = ...;      // minutos de trabajo en la temporada
float tomateMin  = ...;      // m² comprometidos con el restaurante
float lechugaMax = ...;      // m² que la feria alcanza a comprar
float metaMargen = ...;      // $
float metaAgua   = ...;      // litros
float wMargen    = ...;      // peso de la meta de margen
float wAgua      = ...;      // peso de la meta de agua

// VARIABLES
dvar float+ x[1..2];         // m² de tomate (1) y de lechuga (2)
dvar float+ dmMenos;         // cuánto falta para la meta de margen   (no deseada)
dvar float+ dmMas;           // cuánto se pasa de la meta de margen
dvar float+ daMenos;         // cuánta agua queda bajo la meta
dvar float+ daMas;           // cuánta agua se pasa de la meta        (no deseada)

dexpr float Margen = sum(i in 1..2) margen[i] * x[i];
dexpr float Agua   = sum(i in 1..2) agua[i] * x[i];

minimize wMargen * dmMenos / metaMargen + wAgua * daMas / metaAgua;

subject to {
  // restricciones duras (del sistema)
  Superficie: x[1] + x[2] <= superficie;
  Trabajo:    sum(i in 1..2) trabajo[i] * x[i] <= minutos;
  Tomate:     x[1] >= tomateMin;
  Lechuga:    x[2] <= lechugaMax;
  // restricciones blandas (metas)
  MetaMargen: Margen + dmMenos - dmMas == metaMargen;
  MetaAgua:   Agua   + daMenos - daMas == metaAgua;
}

execute {
  writeln("tomate = ", x[1]);
  writeln("lechuga = ", x[2]);
  writeln("margen = ", Margen);
  writeln("agua = ", Agua);
  writeln("falta_margen = ", dmMenos);
  writeln("exceso_agua = ", daMas);
}
