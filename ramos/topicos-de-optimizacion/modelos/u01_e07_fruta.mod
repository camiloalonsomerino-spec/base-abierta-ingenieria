// Ejercicio 1.7 · fruta a la planta: camiones y furgones (enteros) y tren (continuo)
float carga       = 47.5;     // toneladas por día que hay que mover
float capCamion   = 12;       // toneladas por camión
float costoCamion = 180000;   // CLP por camión y día
float capFurgon   = 3.5;      // toneladas por furgón
float costoFurgon = 65000;    // CLP por furgón y día
float costoTren   = 9000;     // CLP por tonelada
float topeTren    = 20;       // toneladas por día que admite el tren

dvar int+   camiones;         // camiones que se arriendan por día
dvar int+   furgones;         // furgones que se arriendan por día
dvar float+ tren;             // toneladas que van en tren por día

minimize costoCamion * camiones + costoFurgon * furgones + costoTren * tren;

subject to {
  Carga:    capCamion * camiones + capFurgon * furgones + tren >= carga;
  TopeTren: tren <= topeTren;
}

execute {
  writeln("camiones = ", camiones);
  writeln("furgones = ", furgones);
  writeln("toneladas_tren = ", tren);
}
