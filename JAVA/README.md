# Implementación en Java — SGA-DO

Aquí va el código fuente en Java del sistema (Módulo 5).

La implementación completa en Java para el Motor Core Backend del Sistema de Gestión Académica (SGA-DO).
Esta solución debe cumplir estrictamente con el Modelado Orientado a Objetos (UML), la persistencia en archivos de texto (.txt) y el uso de Pila (LIFO) para deshacer notas y Cola (FIFO) para certificar graduandos.

Estrategia de Archivos y Persistencia

- alumnos.txt: Guarda cedula|nombre|correo|tipoPrograma|nota1,nota2,...
- profesores.txt: Guarda cedula|nombre|correo|especialidad|materia
- certificados_pendientes.txt: Guarda cedula|nombre|correo|tipoPrograma|promedioFinal
