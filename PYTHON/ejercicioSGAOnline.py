# ==========================================
# CLASES DE PROGRAMAS ACADÉMICOS
# ==========================================
class ProgramaAcademico:
    def __init__(self, nombre: str):
        self.nombre = nombre


class Curso(ProgramaAcademico):
    def __init__(self):
        super().__init__("Curso")


class Diplomado(ProgramaAcademico):
    def __init__(self):
        super().__init__("Diplomado")


class Bootcamp(ProgramaAcademico):
    def __init__(self):
        super().__init__("Bootcamp")


# ==========================================
# CLASES DE PERSONAS
# ==========================================
class Persona:
    def __init__(self, cedula: str, nombre: str, correo: str):
        self.cedula = cedula
        self.nombre = nombre
        self.correo = correo


class Alumno(Persona):
    def __init__(
        self, cedula: str, nombre: str, correo: str, programa: ProgramaAcademico
    ):
        super().__init__(cedula, nombre, correo)
        self.programa = programa
        self.notas = []


class Profesor(Persona):
    def __init__(
        self, cedula: str, nombre: str, correo: str, especialidad: str, materia: str
    ):
        super().__init__(cedula, nombre, correo)
        self.especialidad = especialidad
        self.materia = materia


# ==========================================
# CONTROLADOR DEL SISTEMA (MOTOR BACKEND)
# ==========================================
class SistemaGestionAcademica:
    def __init__(self):
        self.alumnos = {}  # Diccionario para almacenar alumnos en memoria
        self.profesores = {}  # Diccionario para almacenar profesores en memoria
        self.pila_notas = []  # Historial LIFO para la función Deshacer

    def registrar_alumno(self):
        print("\n--- REGISTRO DE ALUMNO ---")

        while True:
            cedula = input("Cédula/ID (Ej. V-123456): ").strip().upper()

            # Validar que comience con V- o E- y que lo que sigue sean solo números
            if len(cedula) > 2 and cedula[:2] in ("V-", "E-") and cedula[2:].isdigit():
                if cedula in self.alumnos:
                    print("❌ Error: Ya existe un alumno registrado con esa cédula.")
                    continue

                # --- PASO DE VERIFICACIÓN ---
                confirmacion = (
                    input(f"Has ingresado la cédula: {cedula}. ¿Es correcta? (s/n): ")
                    .strip()
                    .lower()
                )

                if confirmacion in ["s", "si", "sí"]:
                    break  # Sale del bucle si el usuario confirma que está bien
                else:
                    print("🔄 De acuerdo, vamos a ingresarla de nuevo.\n")
                    continue
                # ---------------------------

            print(
                "❌ Error: Formato inválido. Debe comenzar con V- o E- seguido de números (Ej: V-123456)."
            )

        while True:
            nombre = input("Nombre Completo: ").strip()

            # 1. Verificamos que no esté vacío y que solo contenga letras y espacios
            if nombre and nombre.replace(" ", "").isalpha():
                nombre_formateado = nombre.title()

                # 2. Pedimos la confirmación AQUÍ DENTRO
                confirmacion = (
                    input(
                        f"Has ingresado el nombre: {nombre_formateado}. ¿Es correcto? (s/n): "
                    )
                    .strip()
                    .lower()
                )

                if confirmacion in ["s", "si", "sí"]:
                    nombre = nombre_formateado  # Guardamos el nombre formateado
                    break  # Rompe el bucle porque ya es válido y está confirmado
                else:
                    print(
                        "🔄 De acuerdo, vamos a ingresar de nuevo el nombre completo.\n"
                    )
                    continue  # Vuelve a empezar el bucle

            # 3. Si no pasa la validación de letras
            print("❌ Error: El nombre debe contener solo letras.")

        while True:
            correo = input("Correo Electrónico: ").strip()

            # 1. Verificamos que cumpla con el formato básico del '@' y el dominio
            if "@" in correo and "." in correo.split("@")[-1]:
                # 2. Pedimos la confirmación antes de registrarlo definitivamente
                confirmacion = (
                    input(f"Has ingresado el correo: {correo}. ¿Es correcto? (s/n): ")
                    .strip()
                    .lower()
                )

                if confirmacion in ["s", "si", "sí"]:
                    print(f"¡Correo registrado con éxito: {correo}!")
                    break  # Sale del bucle porque ya está validado y confirmado
                else:
                    print("🔄 De acuerdo, vamos a ingresar el correo de nuevo.\n")
                    continue  # Vuelve al inicio del bucle para reintentar

            # 3. Si no cumple con el formato básico
            print(
                "❌ Formato inválido. Asegúrate de incluir '@' y un dominio válido (ej: usuario@dominio.com).\n"
            )

        # --- Selección del Tipo de Programa ---
        while True:
            print("\nSeleccione el Tipo de Programa:")
            print("1. Curso")
            print("2. Diplomado")
            print("3. Bootcamp")

            opcion_programa = input("Opción (1-3): ").strip()

            if opcion_programa == "1":
                tipo_programa = "Curso"
            elif opcion_programa == "2":
                tipo_programa = "Diplomado"
            elif opcion_programa == "3":
                tipo_programa = "Bootcamp"
            else:
                print("❌ Error: Opción inválida. Debe seleccionar 1, 2 o 3.")
                continue

            confirmacion = (
                input(f"Has seleccionado: {tipo_programa}. ¿Es correcto? (s/n): ")
                .strip()
                .lower()
            )

            if confirmacion in ["s", "si", "sí"]:
                break
            print("🔄 De acuerdo, vamos a seleccionar el tipo de programa de nuevo.\n")

        programa = {
            "Curso": Curso,
            "Diplomado": Diplomado,
            "Bootcamp": Bootcamp,
        }[tipo_programa]()
        nuevo_alumno = Alumno(cedula, nombre, correo, programa)
        self.alumnos[cedula] = nuevo_alumno

        with open("alumnos.txt", "a", encoding="utf-8") as f:
            f.write(f"{cedula},{nombre},{correo},{programa.nombre}\n")

        print(
            f"✅ Alumno '{nombre}' registrado exitosamente en memoria y en alumnos.txt"
        )

    def registrar_profesor(self):
        print("\n--- REGISTRO DE PROFESOR ---")

        # 1. Cédula
        while True:
            cedula_prof = input("Cédula/ID del Profesor (Ej. V-123456): ").strip().upper()
            if len(cedula_prof) > 2 and cedula_prof[:2] in ("V-", "E-") and cedula_prof[2:].isdigit():
                if cedula_prof in self.profesores:
                    print("❌ Error: Ya existe un profesor registrado con esa cédula.")
                    continue
                confirmacion = input(f"Has ingresado la cédula: {cedula_prof}. ¿Es correcta? (s/n): ").strip().lower()
                if confirmacion in ["s", "si", "sí"]:
                    break
                print("🔄 De acuerdo, vamos a ingresarla de nuevo.\n")
                continue
            print("❌ Error: Formato inválido. Debe comenzar con V- o E- seguido de números (Ej: V-123456).")

        # 2. Nombre
        while True:
            nombre_prof = input("Nombre Completo del Profesor: ").strip()
            if nombre_prof and nombre_prof.replace(" ", "").isalpha():
                nombre_formateado = nombre_prof.title()
                confirmacion = input(f"Has ingresado el nombre: {nombre_formateado}. ¿Es correcto? (s/n): ").strip().lower()
                if confirmacion in ["s", "si", "sí"]:
                    nombre_prof = nombre_formateado
                    break
                print("🔄 De acuerdo, vamos a ingresar de nuevo el nombre completo.\n")
                continue
            print("❌ Error: El nombre debe contener solo letras.")

        # 3. Correo
        while True:
            correo_prof = input("Correo Electrónico del Profesor: ").strip()
            if "@" in correo_prof and "." in correo_prof.split("@")[-1]:
                confirmacion = input(f"Has ingresado el correo: {correo_prof}. ¿Es correcto? (s/n): ").strip().lower()
                if confirmacion in ["s", "si", "sí"]:
                    break
                print("🔄 De acuerdo, vamos a ingresar el correo de nuevo.\n")
                continue
            print("❌ Formato inválido. Asegúrate de incluir '@' y un dominio válido.\n")

        # 4. Especialidad
        while True:
            especialidad = input("Especialidad del Profesor: ").strip()
            if especialidad and especialidad.replace(" ", "").isalpha():
                especialidad_formateada = especialidad.title()
                confirmacion = input(f"Has ingresado la especialidad: {especialidad_formateada}. ¿Es correcta? (s/n): ").strip().lower()
                if confirmacion in ["s", "si", "sí"]:
                    especialidad = especialidad_formateada
                    break
                print("🔄 De acuerdo, vamos a ingresar la especialidad de nuevo.\n")
                continue
            print("❌ Error: La especialidad debe contener solo letras.")

        # 5. Materia
        while True:
            materia = input("Materia que imparte: ").strip()
            if materia:
                materia_formateada = materia.title()
                confirmacion = input(f"Has ingresado la materia: {materia_formateada}. ¿Es correcta? (s/n): ").strip().lower()
                if confirmacion in ["s", "si", "sí"]:
                    materia = materia_formateada
                    break
                print("🔄 De acuerdo, vamos a ingresar la materia de nuevo.\n")
                continue
            print("❌ Error: La materia no puede estar vacía.")

        profesor = Profesor(cedula_prof, nombre_prof, correo_prof, especialidad, materia)
        self.profesores[cedula_prof] = profesor

        with open("profesores.txt", "a", encoding="utf-8") as f:
            f.write(f"{cedula_prof},{nombre_prof},{correo_prof},{especialidad},{materia}\n")

        print(f"✅ Profesor '{nombre_prof}' registrado exitosamente en memoria y en profesores.txt")

    def registrar_notas_alumno(self):
        print("\n--- REGISTRAR NOTA A UN ALUMNO ---")
        cedula = input("Ingrese la Cédula del alumno: ").strip()

        # Buscar en memoria
        alumno = self.alumnos.get(cedula)
        if not alumno:
            print("❌ Alumno no encontrado.")
            return

        if len(alumno.notas) >= 3:
            print("⚠️ El alumno ya tiene el máximo de 3 notas registradas.")
            return

        try:
            nota = float(input(f"Ingrese la nota #{len(alumno.notas) + 1} (0-20): "))
            if 0 <= nota <= 20:
                alumno.notas.append(nota)
                # Apilar acción para opción Deshacer (LIFO)
                self.pila_notas.append({"cedula": cedula, "nota": nota})
                print(f"✅ Nota {nota} asignada a {alumno.nombre}.")
            else:
                print("❌ La nota debe estar entre 0 y 20.")
        except ValueError:
            print("❌ Entrada inválida. Debe ingresar un número.")

    def deshacer_ultima_nota(self):
        print("\n--- DESHACER ÚLTIMO REGISTRO DE NOTA (Ctrl + Z / LIFO) ---")
        if not self.pila_notas:
            print("⚠️ No hay notas registradas en la pila para deshacer.")
            return

        # Extraer último elemento apilado (LIFO)
        ultimo_registro = self.pila_notas.pop()
        cedula = ultimo_registro["cedula"]
        nota_removida = ultimo_registro["nota"]

        alumno = self.alumnos.get(cedula)
        if alumno and nota_removida in alumno.notas:
            alumno.notas.remove(nota_removida)
            print(
                f"✅ Se removió la nota {nota_removida} del alumno {alumno.nombre} (ID: {cedula})."
            )
        else:
            print("⚠️ No se pudo remover la nota.")

    def generar_cola_certificados(self):
        print("\n--- GENERAR COLA DE CERTIFICADOS (FIFO) ---")
        # Lógica de aprobación y cola FIFO
        print("Procesando cola de certificados...")

    def mostrar_reporte_general(self):
        print("\n--- REPORTE GENERAL ---")
        print("\nPROFESORES REGISTRADOS:")
        for prof in self.profesores.values():
            print(
                f"- {prof.nombre} | ID: {prof.cedula} | Especialidad: {prof.especialidad} | Materia: {prof.materia}"
            )

        print("\nALUMNOS REGISTRADOS:")
        for al in self.alumnos.values():
            print(
                f"- {al.nombre} | ID: {al.cedula} | Programa: {al.programa.nombre} | Notas: {al.notas}"
            )

# ==========================================
# BUCLE PRINCIPAL DE CONSOLA
# ==========================================
def main():
    sistema = SistemaGestionAcademica()

    while True:
        print("==================================================")
        print("SGA-DO: SISTEMA DIPLOMADOSONLINE")
        print("==================================================")
        print("1. Registrar Alumno")
        print("2. Registrar Profesor")
        print("3. Registrar Notas a un Alumno")
        print("4. Deshacer Último Registro de Nota")
        print("5. Generar Cola de Certificados")
        print("6. Mostrar Reporte General")
        print("7. Salir")
        print("==================================================")

        opcion = input("Seleccione una opción (1-7): ").strip()

        if opcion == "1":
            sistema.registrar_alumno()
        elif opcion == "2":
            sistema.registrar_profesor()
        elif opcion == "3":
            sistema.registrar_notas_alumno()
        elif opcion == "4":
            sistema.deshacer_ultima_nota()
        elif opcion == "5":
            sistema.generar_cola_certificados()
        elif opcion == "6":
            sistema.mostrar_reporte_general()
        elif opcion == "7":
            print(
                "\n💾 Guardando cambios pendientes y cerrando la aplicación de forma segura..."
            )
            break  # Rompe el bucle continuo y finaliza el programa
        else:
            print("❌ Opción inválida. Por favor, seleccione un número del 1 al 7.\n")


if __name__ == "__main__":
    main()
