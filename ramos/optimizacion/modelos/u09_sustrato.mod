/*********************************************
 * Unidad 9 · Ejemplo · sustrato de un vivero
 * Mezcla de tierra de hoja y compost al menor costo, por saco de 60 litros.
 * Tiene una restricción =, una >= y una <=: a mano necesita dos artificiales.
 *********************************************/
{string} Insumos = {"tierra", "compost"};
float costo[Insumos]     = [180, 310];     // CLP por litro
float nitrogeno[Insumos] = [1, 4];         // gramos de nitrógeno por litro
float volumen = 60;                        // litros por saco
float nitrogenoMin = 150;                  // gramos de nitrógeno por saco
float compostMax = 40;                     // litros de compost como máximo

dvar float+ x[Insumos];                    // litros de cada insumo en el saco

minimize sum(i in Insumos) costo[i] * x[i];

subject to {
  ctVolumen:   sum(i in Insumos) x[i] == volumen;
  ctNitrogeno: sum(i in Insumos) nitrogeno[i] * x[i] >= nitrogenoMin;
  ctCompost:   x["compost"] <= compostMax;
}

execute {
  writeln("x_tierra = ", x["tierra"]);
  writeln("x_compost = ", x["compost"]);
  writeln("dual_volumen = ", ctVolumen.dual);
  writeln("dual_nitrogeno = ", ctNitrogeno.dual);
  writeln("dual_compost = ", ctCompost.dual);
}
