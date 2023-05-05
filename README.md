Un programa que escribí y uso cotidianamente. Accede a mi calendario de Google y puede:

*buscar intervalos de 60 minutos o más disponibles en determinado rango de días,

*recopilar información acerca de uno o más alumnos, que incluye día de la clase, horario, valor, plata adeudada y data fiscal, todo en base al calendario y una minibase local.

*calcular ingresos en determinado rango de días.

Empaqueté la autenticación con los servidores de google (usando google-api-client-library) en una función a la que le das los scopes y hace lo suyo, para usar en otros programas que también la necesitan.
Solo funciona en mi máquina porque los paths a los módulos están hardcodeados, pero cambiando dos boludeces se puede adaptar.

Obviamente está hecho para para mi caso de uso particular, que incluye el valor de mi hora de trabajo, la manera en la que asiento los eventos en mi calendario, archivos de autenticación almacenados localmente, etc.
