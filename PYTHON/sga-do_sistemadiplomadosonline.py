import csv
import os
import shutil
import sys
from collections import deque
from datetime import datetime

os.system("color 17")


# ==========================================
# EXCEPCIÓN PERSONALIZADA PARA ESC
# ==========================================
class VolverAlMenuException(Exception):
    """Excepción lanzada cuando el usuario presiona la tecla ESC para volver al menú."""


def leer_input_con_escape(mensaje):
    """Lee caracteres de consola uno a uno para detectar la tecla ESC (\x1b) de forma cruzada (Windows/Linux/Mac)."""
    print(mensaje, end="", flush=True)
    chars = []

    if os.name == "nt":
        import msvcrt

        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch == b"\x1b":  # Código de la tecla ESC
                    print(
                        "\n\n🔙 [ESC detectado] Cancelando y regresando al menú principal..."
                    )
                    return None
                elif ch in (b"\r", b"\n"):  # Enter
                    print()
                    return "".join(chars)
                elif ch == b"\x08":  # Backspace
                    if chars:
                        chars.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                else:
                    try:
                        decoded = ch.decode("utf-8")
                        chars.append(decoded)
                        sys.stdout.write(decoded)
                        sys.stdout.flush()
                    except UnicodeDecodeError:
                        pass
    else:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch == "\x1b":  # Código de la tecla ESC
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    print(
                        "\r\n\n🔙 [ESC detectado] Cancelando y regresando al menú principal...\r"
                    )
                    return None
                elif ch in ("\r", "\n"):
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    return "".join(chars)
                elif ch == "\x7f":  # Backspace
                    if chars:
                        chars.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                else:
                    chars.append(ch)
                    sys.stdout.write(ch)
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


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
        self.promedio = 0.0
        self.estado = "PENDIENTE"

    def calcular_rendimiento(self):
        if not self.notas:
            self.promedio = 0.0
            self.estado = "PENDIENTE"
            return

        self.promedio = sum(self.notas) / len(self.notas)
        tipo_prog = self.programa.nombre

        if tipo_prog == "Diplomado":
            aprobado = self.promedio >= 14.0
        elif tipo_prog == "Bootcamp":
            aprobado = all(nota >= 14 for nota in self.notas)
        else:
            aprobado = self.promedio >= 10.0

        self.estado = "APROBADO" if aprobado else "REPROBADO"


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
        self.alumnos = {}
        self.profesores = {}
        self.pila_notas = []
        self.cargar_datos_almacenados()

    def pedir(self, mensaje):
        res = leer_input_con_escape(mensaje)
        if res is None:
            raise VolverAlMenuException()
        return res.strip()

    def guardar_alumnos_disco(self):
        """Guarda en alumnos.txt: cedula,nombre,correo,curso,nota1,nota2,nota3 (separado por comas)"""
        try:
            with open("alumnos.txt", "w", encoding="utf-8", newline="") as archivo:
                for al in self.alumnos.values():
                    tipo_prog = al.programa.nombre if al.programa else "Curso"
                    notas_str = ",".join(map(str, al.notas)) if al.notas else ""
                    linea = (
                        f"{al.cedula},{al.nombre},{al.correo},{tipo_prog},{notas_str}\n"
                        if notas_str
                        else f"{al.cedula},{al.nombre},{al.correo},{tipo_prog},\n"
                    )
                    archivo.write(linea)
        except OSError as e:
            print(f"⚠️ Error al actualizar alumnos.txt: {e}")

    def cargar_datos_almacenados(self):
        # 1. Cargar Alumnos y generar copia de seguridad automática
        if os.path.exists("alumnos.txt"):
            try:
                os.makedirs("backups", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join("backups", f"alumnos_backup_{timestamp}.txt")

                shutil.copy("alumnos.txt", backup_path)
                print(
                    f"📦 [Backup Automático] Copia de seguridad creada en: {backup_path}"
                )

                with open("alumnos.txt", "r", encoding="utf-8") as archivo:
                    for linea in archivo:
                        linea = linea.strip()
                        if linea:
                            datos = linea.split(",")
                            if len(datos) >= 4:
                                cedula = datos[0]
                                nombre = datos[1]
                                correo = datos[2]
                                tipo_prog = datos[3]

                                notas_str_list = datos[4:]
                                notas = [
                                    int(n)
                                    for n in notas_str_list
                                    if n.strip().isdigit()
                                ]

                                if tipo_prog == "Diplomado":
                                    obj_prog = Diplomado()
                                elif tipo_prog == "Bootcamp":
                                    obj_prog = Bootcamp()
                                else:
                                    obj_prog = Curso()

                                alumno_obj = Alumno(cedula, nombre, correo, obj_prog)
                                alumno_obj.notas = notas
                                alumno_obj.calcular_rendimiento()
                                self.alumnos[cedula] = alumno_obj
                print("📁 Alumnos cargados correctamente desde alumnos.txt.")
            except (OSError, ValueError) as e:
                print(f"⚠️ Error al leer o respaldar alumnos.txt: {e}")

        # 2. Cargar Profesores
        if os.path.exists("profesores.txt"):
            try:
                with open(
                    "profesores.txt", "r", encoding="utf-8", newline=""
                ) as archivo:
                    lector = csv.reader(archivo)
                    for row in lector:
                        if len(row) >= 5:
                            cedula, nombre, correo, especialidad, materia = row[:5]
                            prof_obj = Profesor(
                                cedula, nombre, correo, especialidad, materia
                            )
                            self.profesores[cedula] = prof_obj
                print("📁 Profesores cargados correctamente.")
            except OSError as e:
                print(f"⚠️ Error al leer profesores.txt: {e}")

    def registrar_alumno(self):
        try:
            while True:
                print("\n--- REGISTRO DE ALUMNO (Presione [ESC] para volver) ---")

                while True:
                    cedula = self.pedir("Cédula/ID (Ej. V-123456): ").upper()
                    if (
                        len(cedula) > 2
                        and cedula[:2] in ("V-", "E-")
                        and cedula[2:].isdigit()
                    ):
                        if cedula in self.alumnos:
                            print(
                                "❌ Error: Ya existe un alumno registrado con esa cédula."
                            )
                            repetir = self.pedir(
                                "¿Desea intentar con otra cédula? (s/n): "
                            ).lower()
                            if repetir in ["s", "si", "sí"]:
                                continue
                            else:
                                return

                        confirmacion = self.pedir(
                            f"Has ingresado la cédula: {cedula}. ¿Es correcta? (s/n): "
                        ).lower()
                        if confirmacion in ["s", "si", "sí"]:
                            break
                        else:
                            print("🔄 De acuerdo, vamos a ingresarla de nuevo.\n")
                            continue
                    print(
                        "❌ Error: Formato inválido. Debe comenzar con V- o E- seguido de números (Ej: V-123456)."
                    )

                while True:
                    nombre = self.pedir("Nombre Completo: ")
                    if nombre and nombre.replace(" ", "").isalpha():
                        nombre_formateado = nombre.title()
                        confirmacion = self.pedir(
                            f"Has ingresado el nombre: {nombre_formateado}. ¿Es correcto? (s/n): "
                        ).lower()
                        if confirmacion in ["s", "si", "sí"]:
                            nombre = nombre_formateado
                            break
                        else:
                            print(
                                "🔄 De acuerdo, vamos a ingresar de nuevo el nombre completo.\n"
                            )
                            continue
                    print("❌ Error: El nombre debe contener solo letras.")

                while True:
                    correo = self.pedir("Correo Electrónico: ")
                    if "@" in correo and "." in correo.split("@")[-1]:
                        confirmacion = self.pedir(
                            f"Has ingresado el correo: {correo}. ¿Es correcto? (s/n): "
                        ).lower()
                        if confirmacion in ["s", "si", "sí"]:
                            break
                        else:
                            print(
                                "🔄 De acuerdo, vamos a ingresar el correo de nuevo.\n"
                            )
                            continue
                    print(
                        "❌ Formato inválido. Asegúrate de incluir '@' y un dominio válido.\n"
                    )

                while True:
                    print("\nSeleccione el Tipo de Programa:")
                    print("1. Curso")
                    print("2. Diplomado")
                    print("3. Bootcamp")

                    opcion_programa = self.pedir("Opción (1-3): ")

                    if opcion_programa == "1":
                        tipo_programa = "Curso"
                        programa = Curso()
                    elif opcion_programa == "2":
                        tipo_programa = "Diplomado"
                        programa = Diplomado()
                    elif opcion_programa == "3":
                        tipo_programa = "Bootcamp"
                        programa = Bootcamp()
                    else:
                        print("❌ Error: Opción inválida. Debe seleccionar 1, 2 o 3.")
                        continue

                    confirmacion = self.pedir(
                        f"Has seleccionado: {tipo_programa}. ¿Es correcto? (s/n): "
                    ).lower()
                    if confirmacion in ["s", "si", "sí"]:
                        break
                    print(
                        "🔄 De acuerdo, vamos a seleccionar el tipo de programa de nuevo.\n"
                    )

                nuevo_alumno = Alumno(cedula, nombre, correo, programa)
                self.alumnos[cedula] = nuevo_alumno
                self.guardar_alumnos_disco()
                print(
                    f"✅ Alumno '{nombre}' registrado exitosamente en memoria y en alumnos.txt"
                )

                continuar = self.pedir(
                    "\n¿Desea registrar otro alumno? (s/n): "
                ).lower()
                if continuar not in ["s", "si", "sí"]:
                    print("🔙 Regresando al menú principal...")
                    break
        except VolverAlMenuException:
            print("🔙 Regresando al menú principal...")
            return

    def registrar_profesor(self):
        try:
            while True:
                print("\n--- REGISTRO DE PROFESOR (Presione [ESC] para volver) ---")

                while True:
                    cedula_prof = self.pedir(
                        "Cédula/ID del Profesor (Ej. P-123456): "
                    ).upper()
                    if (
                        len(cedula_prof) > 2
                        and cedula_prof.startswith("P-")
                        and cedula_prof[2:].isdigit()
                    ):
                        if cedula_prof in self.profesores:
                            print(
                                "❌ Error: Ya existe un profesor registrado con esa cédula."
                            )
                            repetir = self.pedir(
                                "¿Desea intentar con otra cédula? (s/n): "
                            ).lower()
                            if repetir in ["s", "si", "sí"]:
                                continue
                            else:
                                return

                        confirmacion = self.pedir(
                            f"Has ingresado la cédula: {cedula_prof}. ¿Es correcta? (s/n): "
                        ).lower()
                        if confirmacion in ["s", "si", "sí"]:
                            break
                        print("🔄 De acuerdo, vamos a ingresarla de nuevo.\n")
                        continue
                    print(
                        "❌ Error: Formato inválido. Debe comenzar con P- seguido de números (Ej: P-123456)."
                    )

                while True:
                    nombre_prof = self.pedir("Nombre Completo del Profesor: ")
                    if nombre_prof and nombre_prof.replace(".", "").replace(".", ""):
                        nombre_formateado = nombre_prof.title()
                        confirmacion = self.pedir(
                            f"Has ingresado el nombre: {nombre_formateado}. ¿Es correcto? (s/n): "
                        ).lower()
                        if confirmacion in ["s", "si", "sí"]:
                            nombre_prof = nombre_formateado
                            break
                        print(
                            "🔄 De acuerdo, vamos a ingresar de nuevo el nombre completo.\n"
                        )
                        continue
                    print("❌ Error: El nombre debe contener solo letras.")

                while True:
                    correo_prof = self.pedir("Correo Electrónico del Profesor: ")
                    if "@" in correo_prof and "." in correo_prof.split("@")[-1]:
                        confirmacion = self.pedir(
                            f"Has ingresado el correo: {correo_prof}. ¿Es correcto? (s/n): "
                        ).lower()
                        if confirmacion in ["s", "si", "sí"]:
                            break
                        print("🔄 De acuerdo, vamos a ingresar el correo de nuevo.\n")
                        continue
                    print(
                        "❌ Formato inválido. Asegúrate de incluir '@' y un dominio válido.\n"
                    )

                while True:
                    especialidad = self.pedir("Especialidad del Profesor: ")
                    if especialidad and especialidad.replace(" ", "").isalpha():
                        especialidad_formateada = especialidad.title()
                        confirmacion = self.pedir(
                            f"Has ingresado la especialidad: {especialidad_formateada}. ¿Es correcta? (s/n): "
                        ).lower()
                        if confirmacion in ["s", "si", "sí"]:
                            especialidad = especialidad_formateada
                            break
                        print(
                            "🔄 De acuerdo, vamos a ingresar la especialidad de nuevo.\n"
                        )
                        continue
                    print("❌ Error: La especialidad debe contener solo letras.")

                while True:
                    materia = self.pedir("Materia que imparte: ")
                    if materia:
                        materia_formateada = materia.title()
                        confirmacion = self.pedir(
                            f"Has ingresado la materia: {materia_formateada}. ¿Es correcta? (s/n): "
                        ).lower()
                        if confirmacion in ["s", "si", "sí"]:
                            materia = materia_formateada
                            break
                        print("🔄 De acuerdo, vamos a ingresar la materia de nuevo.\n")
                        continue
                    print("❌ Error: La materia no puede estar vacía.")

                profesor = Profesor(
                    cedula_prof, nombre_prof, correo_prof, especialidad, materia
                )
                self.profesores[cedula_prof] = profesor

                try:
                    with open("profesores.txt", "a", encoding="utf-8", newline="") as f:
                        escritor = csv.writer(f)
                        escritor.writerow(
                            [
                                cedula_prof,
                                nombre_prof,
                                correo_prof,
                                especialidad,
                                materia,
                            ]
                        )
                    print(
                        f"✅ Profesor '{nombre_prof}' registrado exitosamente en memoria y en profesores.txt"
                    )
                except OSError as e:
                    print(f"⚠️ Error al guardar en profesores.txt: {e}")

                continuar = self.pedir(
                    "\n¿Desea registrar otro profesor? (s/n): "
                ).lower()
                if continuar not in ["s", "si", "sí"]:
                    print("🔙 Regresando al menú principal...")
                    break
        except VolverAlMenuException:
            print("🔙 Regresando al menú principal...")
            return

    def registrar_notas_alumno(self):
        if not self.alumnos:
            print("❌ No hay alumnos registrados en el sistema.")
            return

        try:
            while True:
                print("\n--- REGISTRO DE NOTAS (Presione [ESC] para volver) ---")

                while True:
                    cedula_buscar = self.pedir(
                        "Cédula/ID del Alumno a calificar (Ej. V-123456): "
                    ).upper()
                    if (
                        len(cedula_buscar) > 2
                        and cedula_buscar[:2] in ("V-", "E-")
                        and cedula_buscar[2:].isdigit()
                    ):
                        break
                    print(
                        "❌ Error: Formato inválido. Debe comenzar con V- o E- seguido de números."
                    )

                alumno_info = self.alumnos.get(cedula_buscar)
                if alumno_info is None:
                    print(
                        f"❌ No se encontró ningún alumno registrado con la cédula {cedula_buscar}."
                    )
                    repetir = self.pedir("¿Desea buscar otro alumno? (s/n): ").lower()
                    if repetir in ["s", "si", "sí"]:
                        continue
                    else:
                        return

                tipo_prog = alumno_info.programa.nombre
                print(
                    f"✅ Alumno encontrado: {alumno_info.nombre} | Programa: {tipo_prog}"
                )

                calificaciones = []
                print(
                    f"\nIngrese las 3 calificaciones ENTERAS (Escala de 0 a 20) para el {tipo_prog}:"
                )
                for i in range(1, 4):
                    while True:
                        try:
                            nota_str = self.pedir(f"Calificación {i} (0-20): ")
                            nota = int(nota_str)
                            if 0 <= nota <= 20:
                                calificaciones.append(nota)

                                # Persistencia atómica e inmediata por cada nota
                                alumno_info.notas = calificaciones
                                alumno_info.calcular_rendimiento()
                                self.guardar_alumnos_disco()

                                break
                            print("❌ Error: La nota debe estar entre 0 y 20.")
                        except ValueError:
                            print(
                                "❌ Error: Debe ingresar un valor numérico entero válido."
                            )

                for nota in calificaciones:
                    self.pila_notas.append({"cedula": cedula_buscar, "nota": nota})

                if tipo_prog == "Diplomado":
                    criterio_txt = f"Promedio requerido: >= 14.0 (Tu promedio: {alumno_info.promedio:.2f})"
                elif tipo_prog == "Bootcamp":
                    criterio_txt = "Requisito Bootcamp: Ninguna nota individual puede ser menor a 14"
                else:
                    criterio_txt = f"Promedio requerido: >= 10.0 (Tu promedio: {alumno_info.promedio:.2f})"

                print("\n" + "=" * 45)
                print(f"📊 RESULTADOS FINALES PARA: {alumno_info.nombre}")
                print(f"Notas registradas: {calificaciones}")
                print(f"Promedio obtenido: {alumno_info.promedio:.2f}")
                print(f"Criterio aplicado: {criterio_txt}")
                print(f"Estado Final: {alumno_info.estado}")
                print("=" * 45)

                continuar = self.pedir(
                    "\n¿Desea registrar notas a otro alumno? (s/n): "
                ).lower()
                if continuar not in ["s", "si", "sí"]:
                    print("🔙 Regresando al menú principal...")
                    break
        except VolverAlMenuException:
            print("🔙 Regresando al menú principal...")
            return

    def deshacer_ultima_nota(self):
        print("\n--- DESHACER ÚLTIMO REGISTRO DE NOTA (LIFO) ---")
        if not self.pila_notas:
            print("⚠️ No hay notas recientes en la pila para deshacer.")
            return

        ultima_accion = self.pila_notas.pop()
        cedula = ultima_accion["cedula"]
        nota_removida = ultima_accion["nota"]

        alumno = self.alumnos.get(cedula)
        if alumno and alumno.notas:
            if nota_removida in alumno.notas:
                alumno.notas.remove(nota_removida)

            alumno.calcular_rendimiento()
            self.guardar_alumnos_disco()
            print(
                f"↩️ Se ha deshecho la nota {nota_removida} del alumno {alumno.nombre} (Cédula: {cedula})."
            )
        else:
            print("⚠️ El alumno asociado ya no tiene notas registradas.")

    def generar_cola_certificados(self):
        alumnos_aprobados = [a for a in self.alumnos.values() if a.estado == "APROBADO"]

        if not alumnos_aprobados:
            print("\n⚠️ No hay alumnos aprobados en cola para emisión de certificados.")
            return

        cola_certificados = deque(alumnos_aprobados)
        total_graduandos = len(cola_certificados)

        print("\n=========================================")
        print("REPORTE DE CERTIFICADOS PENDIENTES")
        print("=========================================")
        print(f"Total de graduandos en cola: {total_graduandos}\n")

        contador = 1
        lineas_archivo = [
            "=========================================\n",
            "REPORTE DE CERTIFICADOS PENDIENTES\n",
            "=========================================\n",
            f"Total de graduandos en cola: {total_graduandos}\n\n",
        ]

        while cola_certificados:
            al = cola_certificados.popleft()
            prog_nombre = al.programa.nombre

            if prog_nombre == "Bootcamp":
                estatus_txt = "APROBADO (Cumple regla de ninguna nota < 14)"
            else:
                estatus_txt = "APROBADO"

            bloque = (
                f"{contador}. [{al.cedula}] {al.nombre}\n"
                f"- Programa: {prog_nombre}\n"
                f"- Promedio Final: {al.promedio:.1f}\n"
                f"- Estatus: {estatus_txt}\n\n"
            )

            print(bloque, end="")
            lineas_archivo.append(bloque)
            contador += 1

        pie_pagina = "=========================================\n- Fin del reporte - Generado por SGA-DO *"
        print("=========================================")
        print("- Fin del reporte - Generado por SGA-DO *")

        lineas_archivo.append(pie_pagina)

        try:
            with open("certificados_pendientes.txt", "w", encoding="utf-8") as f:
                f.writelines(lineas_archivo)
            print("\n📄 Archivo 'certificados_pendientes.txt' guardado exitosamente.")
        except OSError as e:
            print(f"⚠️ Error al escribir el archivo de certificados: {e}")

    def mostrar_reporte_general(self):
        print("\n" + "=" * 60)
        print("📋 REPORTE GENERAL DEL SISTEMA ACADÉMICO")
        print("=" * 60)

        print(f"\n--- PROFESORES REGISTRADOS ({len(self.profesores)}) ---")
        if not self.profesores:
            print("No hay profesores registrados.")
        else:
            for p in self.profesores.values():
                print(
                    f"ID: {p.cedula} | Nombre: {p.nombre} | Materia: {p.materia} ({p.especialidad})"
                )

        print(f"\n--- ALUMNOS REGISTRADOS ({len(self.alumnos)}) ---")
        if not self.alumnos:
            print("No hay alumnos registrados.")
        else:
            for a in self.alumnos.values():
                prog = a.programa.nombre if a.programa else "N/A"
                notas_txt = ", ".join(map(str, a.notas)) if a.notas else "Sin notas"
                print(
                    f"ID: {a.cedula} | Nombre: {a.nombre} | Prog: {prog} | Notas: [{notas_txt}] | Prom: {a.promedio:.1f} | Estado: {a.estado}"
                )
        print("=" * 60)


# ==========================================
# BUCLE PRINCIPAL DE CONSOLA
# ==========================================
def main():
    sistema = SistemaGestionAcademica()

    while True:
        # Limpiar pantalla de forma compatible (Windows / Linux / macOS)
        os.system("cls" if os.name == "nt" else "clear")

        print("\n==================================================")
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

        entrada = input("Seleccione una opción (1-7): ").strip()

        if not entrada.isdigit():
            print(
                "\n❌ Error: Debe ingresar un valor numérico válido (no letras ni símbolos)."
            )
            input("\nPresione Enter para continuar...")
            continue

        opcion = int(entrada)

        if opcion == 1:
            sistema.registrar_alumno()
            input("\nPresione Enter para volver al menú...")
        elif opcion == 2:
            sistema.registrar_profesor()
            input("\nPresione Enter para volver al menú...")
        elif opcion == 3:
            sistema.registrar_notas_alumno()
            input("\nPresione Enter para volver al menú...")
        elif opcion == 4:
            sistema.deshacer_ultima_nota()
            input("\nPresione Enter para volver al menú...")
        elif opcion == 5:
            sistema.generar_cola_certificados()
            input("\nPresione Enter para volver al menú...")
        elif opcion == 6:
            sistema.mostrar_reporte_general()
            input("\nPresione Enter para volver al menú...")
        elif opcion == 7:
            print(
                "\n💾 Guardando cambios pendientes y cerrando la aplicación de forma segura..."
            )
            sistema.guardar_alumnos_disco()
            break
        else:
            print("\n❌ Opción inválida. Por favor, seleccione un número entre 1 y 7.")
            input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main()
