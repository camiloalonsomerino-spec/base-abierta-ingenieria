// Ejercicio 2.10 · feria de dos días: qué número va qué día
int n = ...;
range Numeros = 1..n;
{string} Dias = ...;
{int} Folclor = ...;
float costo[Numeros]   = ...;   // cientos de miles de CLP
float publico[Numeros] = ...;   // cientos de personas
int   cupo[Dias]        = ...;   // números exactos por día
float presupuesto[Dias] = ...;
int   minFolclor[Dias]  = ...;

dvar boolean x[Numeros][Dias];  // 1 si el número i se presenta el día t, 0 en otro caso

maximize sum(i in Numeros, t in Dias) publico[i] * x[i][t];

subject to {
  forall(i in Numeros)
    UnaVez:      sum(t in Dias) x[i][t] <= 1;
  forall(t in Dias)
    Cupo:        sum(i in Numeros) x[i][t] == cupo[t];
  forall(t in Dias)
    Presupuesto: sum(i in Numeros) costo[i] * x[i][t] <= presupuesto[t];
  forall(t in Dias)
    FolclorMin:  sum(i in Folclor) x[i][t] >= minFolclor[t];
}

execute {
  for (var t in Dias) for (var i in Numeros) if (x[i][t] == 1) writeln("x[", i, "][", t, "] = 1");
}
