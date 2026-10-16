/*********************************************
 * Unidad 6 · Modelos con varios objetivos (ejercicio 6.6)
 * Mueblería: programación por metas con tres metas (utilidad mínima, horas
 * máximas sin sobretiempo y mesas mínimas para un pedido).
 * Datos en u06_muebles_metas.dat. Base abierta de ingeniería.
 *********************************************/

{string} Muebles = ...;
float utilidad[Muebles] = ...;   // $ por unidad
float horas[Muebles]    = ...;   // horas de taller por unidad
float madera[Muebles]   = ...;   // m² de tablero por unidad
float demMax[Muebles]   = ...;   // unidades que se pueden vender
float horasMax  = ...;           // horas con sobretiempo (tope duro)
float maderaMax = ...;           // m² de tablero de la semana
float metaUtil  = ...;
float metaHoras = ...;
float metaMesas = ...;
float w[1..3]   = ...;           // pesos: utilidad, horas, mesas

dvar float+ x[Muebles];
dvar float+ duMenos;  dvar float+ duMas;    // utilidad bajo / sobre la meta
dvar float+ dhMenos;  dvar float+ dhMas;    // horas bajo / sobre la meta
dvar float+ dmMenos;  dvar float+ dmMas;    // mesas bajo / sobre la meta

dexpr float Util  = sum(m in Muebles) utilidad[m] * x[m];
dexpr float Horas = sum(m in Muebles) horas[m] * x[m];

minimize w[1] * duMenos / metaUtil + w[2] * dhMas / metaHoras + w[3] * dmMenos / metaMesas;

subject to {
  HorasMax:  Horas <= horasMax;
  Madera:    sum(m in Muebles) madera[m] * x[m] <= maderaMax;
  forall(m in Muebles) Demanda: x[m] <= demMax[m];
  MetaUtil:  Util  + duMenos - duMas == metaUtil;
  MetaHoras: Horas + dhMenos - dhMas == metaHoras;
  MetaMesas: x["mesas"] + dmMenos - dmMas == metaMesas;
}

execute {
  for (var m in Muebles) writeln("x[", m, "] = ", x[m]);
  writeln("utilidad = ", Util);
  writeln("horas = ", Horas);
  writeln("falta_utilidad = ", duMenos);
  writeln("exceso_horas = ", dhMas);
  writeln("falta_mesas = ", dmMenos);
}
