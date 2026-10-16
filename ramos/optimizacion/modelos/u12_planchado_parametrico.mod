/*********************************************
 * Unidad 12 · Análisis de sensibilidad
 * Estampa Sur: el «código extra» para ver hasta dónde vale el precio
 * sombra del planchado. Resuelve la mezcla con 18, 19, ..., 24 horas de
 * planchado y escribe el margen y el precio sombra en cada caso.
 * Se corre con u12_estampa.dat.
 *********************************************/
include "u12_mezcla_topes.mod";

main {
  thisOplModel.generate();
  var def   = thisOplModel.modelDefinition;
  var datos = thisOplModel.dataElements;
  for (var h = 18; h <= 24; h++) {
    var m = new IloOplModel(def, cplex);
    datos.cap["planchado"] = h * 3600;
    m.addDataSource(datos);
    m.generate();
    cplex.solve();
    writeln("margen_", h, "h = ", cplex.getObjValue());
    writeln("dual_planchado_", h, "h = ", m.Capacidad["planchado"].dual);
    m.end();
  }
}
