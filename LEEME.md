**SGA-DO — Sistema de Gestión Académica DiplomadosOnline**

Proyecto del Diplomado en Programación: Motor Core (Backend) por consola para la gestión de alumnos, profesores, notas y certificación, implementado en **Python**, **Java** y **C++**, con persistencia en archivos de texto plano.

**Estructura del repositorio**

sga-diplomadosonline/ ├── docs/ # Documentación del proyecto (análisis, plan de acción, diagrama UML) ├── python/ # Implementación en Python (Módulo 4) ├── java/ # Implementación en Java (Módulo 5) ├── cpp/ # Implementación en C++ (Módulo 6) └── README.md

**Contenido de /docs**

- 00_Enunciado_Proyecto.pdf — Enunciado original del proyecto
- 01_Analisis_del_Problema_y_Plan_de_Accion.pdf
  - Entregable 1: Análisis de la crisis operativa y plan de acción
- 02_Diagrama_de_Clases_UML.pdf
  - Entregable 2: Diagrama de clases UML (herencia y polimorfismo)

**Reglas de negocio (resumen)**

- **Curso**: aprueba con promedio ≥ 10/20
- **Diplomado**: aprueba con promedio ≥ 14/20
- **Bootcamp**: aprueba solo si ninguna nota individual es menor a 14/20

**Persistencia**

- alumnos.txt — Cedula,Nombre,Correo,TipoPrograma,Nota1,Nota2,Nota3
- profesores.txt — Cedula,Nombre,Correo,Especialidad,Materia
- certificados_pendientes.txt — Reporte de salida generado por la opción 5 del menú

**Autor**

**Manuel Carrasco Fernández | C.I.: V-5.970.831**