/*********************************************
 * Unidad 9 · Ejercicio 9.10 · la fase 1 escrita como modelo
 * Estampa Sur con dos compromisos (1.280 poleras y 780 polerones) no tiene solución.
 * La fase 1 agrega una artificial a cada compromiso y minimiza su suma: el óptimo
 * dice cuántas unidades faltan para cumplir los dos.
 *********************************************/
{string} Prendas = {"poleras", "polerones"};
float est[Prendas] = [30, 90];
float pla[Prendas] = [20, 50];
float capEst = 30 * 3600;
float capPla = 18 * 3600;
float demPolerones = 830;
float compromiso[Prendas] = [1280, 780];

dvar float+ x[Prendas];
dvar float+ a[Prendas];                    // artificiales: lo que falta para cada compromiso

minimize sum(p in Prendas) a[p];

subject to {
  ctEstampado: sum(p in Prendas) est[p] * x[p] <= capEst;
  ctPlanchado: sum(p in Prendas) pla[p] * x[p] <= capPla;
  ctDemanda:   x["polerones"] <= demPolerones;
  forall(p in Prendas)
    ctCompromiso: x[p] + a[p] >= compromiso[p];
}

execute {
  writeln("x_poleras = ", x["poleras"]);
  writeln("x_polerones = ", x["polerones"]);
  writeln("a_poleras = ", a["poleras"]);
  writeln("a_polerones = ", a["polerones"]);
  writeln("dual_estampado = ", ctEstampado.dual);
}
