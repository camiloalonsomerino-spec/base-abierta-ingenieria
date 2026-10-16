/*********************************************
 * Unidad 3 · Programación de máquinas con gran M
 * Flow shop: todos los trabajos pasan por las máquinas en el mismo orden.
 * Restricciones disyuntivas con gran M; se minimiza el makespan.
 * Datos en u03_flowshop.dat. Base abierta de ingeniería.
 *********************************************/

{string} Trabajos = ...;
{string} Maquinas = ...;              // en el orden en que se recorren

float p[Trabajos][Maquinas] = ...;    // horas del trabajo j en la máquina k

// gran M: si todo se hiciera uno detrás de otro, nada termina después de la suma de tiempos
float M = sum(j in Trabajos, k in Maquinas) p[j][k];

dvar float+  s[Trabajos][Maquinas];          // hora de inicio del trabajo j en la máquina k
dvar boolean z[Trabajos][Trabajos][Maquinas]; // 1 si i va antes que j en la máquina k; 0 si j va antes
dvar float+  Cmax;                            // makespan: hora en que termina el último trabajo

minimize Cmax;

subject to {
  // ruta: un trabajo pasa a la máquina siguiente solo cuando terminó en la anterior
  forall(j in Trabajos, k in Maquinas: k != last(Maquinas))
    Ruta:
      s[j][next(Maquinas, k)] >= s[j][k] + p[j][k];
  // disyunción: en cada máquina, i antes que j o j antes que i
  forall(i in Trabajos, j in Trabajos, k in Maquinas: ord(Trabajos, i) < ord(Trabajos, j)) {
    Antes:
      s[i][k] + p[i][k] <= s[j][k] + M * (1 - z[i][j][k]);
    Despues:
      s[j][k] + p[j][k] <= s[i][k] + M * z[i][j][k];
  }
  // el makespan no es menor que el término de ningún trabajo en la última máquina
  forall(j in Trabajos)
    Fin:
      Cmax >= s[j][last(Maquinas)] + p[j][last(Maquinas)];
}

execute {
  writeln("makespan = ", Cmax);
  for (var k in Maquinas) {
    var orden = "";
    var usados = new Array();
    for (var paso = 1; paso <= Trabajos.size; paso++) {
      var mejor = "";
      for (var j in Trabajos)
        if (usados[j] != 1 && (mejor == "" || s[j][k] < s[mejor][k])) mejor = j;
      usados[mejor] = 1;
      orden = orden + (paso > 1 ? "-" : "") + mejor;
    }
    writeln("orden[", k, "] = ", orden);
  }
}
