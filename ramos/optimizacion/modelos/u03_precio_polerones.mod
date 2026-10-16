/*********************************************
 * Unidad 3 · Caso integrador · el precio de los polerones
 * Un modelo NO lineal: la utilidad (p - c)(a - b p) es cuadrática y cóncava.
 * CPLEX resuelve programas cuadráticos convexos (minimizar algo convexo o
 * maximizar algo cóncavo); un modelo no lineal cualquiera necesita otro solver.
 * Base abierta de ingeniería.
 *********************************************/

float a     = 1960;    // polerones por semana si el precio fuera 0 (intercepto de la demanda)
float b     = 0.112;   // polerones que se dejan de vender por cada peso de alza
float costo = 6150;    // CLP por polerón (costo variable)

dvar float p in costo..a/b;     // precio en CLP; entre el costo y el precio que deja la demanda en 0

dexpr float q = a - b*p;        // polerones vendidos a ese precio

// (p - costo)(a - b p) desarrollado: -b p^2 + (a + b costo) p - a costo
maximize -b*p^2 + (a + b*costo)*p - a*costo;

subject to {
}

execute {
  writeln("precio = ", p);
  writeln("cantidad = ", q);
  writeln("utilidad = ", (p - costo)*q);
}
