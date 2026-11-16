import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.regex.Pattern;

// ==========================================
// EXCEPCIÓN PERSONALIZADA (RuntimeException)
// ==========================================
class VolverAlMenuException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public VolverAlMenuException(String mensaje) {
        super(mensaje);
    }
}

// ==========================================
// CLASES DE PROGRAMAS ACADÉMICOS
// ==========================================
abstract class ProgramaAcademico {
    protected String nombre;

    public ProgramaAcademico(String nombre) {
        this.nombre = nombre;
    }

    public String getNombre() {
        return nombre;
    }
}

class Curso extends ProgramaAcademico {
    public Curso() { super("Curso"); }
}

class Diplomado extends ProgramaAcademico {
    public Diplomado() { super("Diplomado"); }
}

class Bootcamp extends ProgramaAcademico {
    public Bootcamp() { super("Bootcamp"); }
}

// ==========================================
// CLASES DE PERSONAS
// ==========================================
abstract class Persona {
    protected String cedula;
    protected String nombre;
    protected String correo;

    public Persona(String cedula, String nombre, String correo) {
        this.cedula = cedula;
        this.nombre = nombre;
        this.correo = correo;
    }

    public String getCedula() { return cedula; }
    public String getNombre() { return nombre; }
    public String getCorreo() { return correo; }
}

class Alumno extends Persona {
    private ProgramaAcademico programa;
    private List<Integer> notas;
    private double promedio;
    private String estado;

    public Alumno(String cedula, String nombre, String correo, ProgramaAcademico programa) {
        super(cedula, nombre, correo);
        this.programa = programa;
        this.notas = new ArrayList<>();
        this.promedio = 0.0;
        this.estado = "PENDIENTE";
    }

    public ProgramaAcademico getPrograma() { return programa; }
    public List<Integer> getNotas() { return notas; }
    public void setNotas(List<Integer> notas) { this.notas = notas; }
    public double getPromedio() { return promedio; }
    public String getEstado() { return estado; }

    public void calcularRendimiento() {
        if (notas.isEmpty()) {
            this.promedio = 0.0;
            this.estado = "PENDIENTE";
            return;
        }

        int suma = 0;
        for (int nota : notas) {
            suma += nota;
        }
        this.promedio = (double) suma / notas.size();
        String tipoProg = programa.getNombre();

        boolean aprobado;
        if (tipoProg.equals("Diplomado")) {
            aprobado = this.promedio >= 14.0;
        } else if (tipoProg.equals("Bootcamp")) {
            aprobado = true;
            for (int nota : notas) {
                if (nota < 14) {
                    aprobado = false;
                    break;
                }
            }
        } else {
            aprobado = this.promedio >= 10.0;
        }

        this.estado = aprobado ? "APROBADO" : "REPROBADO";
    }
}

class Profesor extends Persona {
    private String especialidad;
    private String materia;

    public Profesor(String cedula, String nombre, String correo, String especialidad, String materia) {
        super(cedula, nombre, correo);
        this.especialidad = especialidad;
        this.materia = materia;
    }

    public String getEspecialidad() { return especialidad; }
    public String getMateria() { return materia; }
}

class NotaAccion {
    String cedula;
    List<Integer> notasAnteriores;

    public NotaAccion(String cedula, List<Integer> notasAnteriores) {
        this.cedula = cedula;
        this.notasAnteriores = new ArrayList<>(notasAnteriores);
    }
}

// ==========================================
// CONTROLADOR DEL SISTEMA (MOTOR BACKEND)
// ==========================================
public class SistemaGestionAcademica {
    private Map<String, Alumno> alumnos;
    private Map<String, Profesor> profesores;
    private Stack<NotaAccion> pilaNotas;
    private Scanner scanner;

    private static final Pattern PATRON_CORREO = Pattern.compile("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");

    public SistemaGestionAcademica(Scanner scanner) {
        this.alumnos = new HashMap<>();
        this.profesores = new HashMap<>();
        this.pilaNotas = new Stack<>();
        this.scanner = scanner;
        cargarDatosAlmacenados();
    }

    public String pedir(String mensaje) {
        System.out.print(mensaje);
        String entrada = scanner.nextLine().trim();
        if (entrada.equalsIgnoreCase("ESC")) {
            throw new VolverAlMenuException("Regresando al menú principal...");
        }
        return entrada;
    }

    private String formatearNombre(String texto) {
        if (texto == null || texto.isEmpty()) return "";
        StringBuilder resultado = new StringBuilder();
        boolean capitalizarSiguiente = true;

        for (char c : texto.toLowerCase().toCharArray()) {
            if (Character.isWhitespace(c)) {
                capitalizarSiguiente = true;
                resultado.append(c);
            } else if (capitalizarSiguiente) {
                resultado.append(Character.toUpperCase(c));
                capitalizarSiguiente = false;
            } else {
                resultado.append(c);
            }
        }
        return resultado.toString().trim();
    }

    private String escaparCSV(String valor) {
        if (valor == null) return "";
        if (valor.contains(",") || valor.contains("\"") || valor.contains("\n")) {
            return "\"" + valor.replace("\"", "\"\"") + "\"";
        }
        return valor;
    }

    private List<String> parsearLineaCSV(String linea) throws IllegalArgumentException {
        List<String> tokens = new ArrayList<>();
        StringBuilder sb = new StringBuilder();
        boolean enComillas = false;
        
        for (int i = 0; i < linea.length(); i++) {
            char c = linea.charAt(i);
            if (c == '"') {
                if (enComillas && i + 1 < linea.length() && linea.charAt(i + 1) == '"') {
                    sb.append('"');
                    i++;
                } else {
                    enComillas = !enComillas;
                }
            } else if (c == ',' && !enComillas) {
                tokens.add(sb.toString().trim());
                sb.setLength(0);
            } else {
                sb.append(c);
            }
        }
        if (enComillas) {
            throw new IllegalArgumentException("Comillas mal formadas o sin cerrar");
        }
        tokens.add(sb.toString().trim());
        return tokens;
    }

    public void guardarAlumnosDisco() {
        Path archivoOriginal = Paths.get("alumnos.txt");

        List<Alumno> alumnosOrdenados = new ArrayList<>(alumnos.values());
        alumnosOrdenados.sort(Comparator.comparing(Alumno::getCedula));

        int intentos = 0;
        while (intentos < 5) {
            try (BufferedWriter bw = Files.newBufferedWriter(
                    archivoOriginal,
                    StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE,
                    StandardOpenOption.TRUNCATE_EXISTING,
                    StandardOpenOption.WRITE)) {
                for (Alumno al : alumnosOrdenados) {
                    String tipoProg = al.getPrograma() != null ? al.getPrograma().getNombre() : "Curso";
                    StringBuilder notasStr = new StringBuilder();
                    for (int i = 0; i < al.getNotas().size(); i++) {
                        notasStr.append(al.getNotas().get(i));
                        if (i < al.getNotas().size() - 1) {
                            notasStr.append(",");
                        }
                    }
                    String linea = escaparCSV(al.getCedula()) + "," +
                                   escaparCSV(al.getNombre()) + "," +
                                   escaparCSV(al.getCorreo()) + "," +
                                   escaparCSV(tipoProg) + "," +
                                   notasStr.toString();
                    bw.write(linea);
                    bw.newLine();
                }
                bw.flush();
                return;
            } catch (IOException e) {
                if (intentos == 4) {
                    System.out.println("⚠️ Error crítico al actualizar alumnos.txt: " + e.getMessage());
                    return;
                }
                intentos++;
                try {
                    Thread.sleep(200L * intentos);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }

    private void cargarDatosAlmacenados() {
        File archivoAlumnos = new File("alumnos.txt");
        if (archivoAlumnos.exists()) {
            try {
                File dirBackups = new File("backups");
                if (!dirBackups.exists()) dirBackups.mkdir();

                String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss_SSS"));
                File backupPath = new File(dirBackups, "alumnos_backup_" + timestamp + ".txt");
                Files.copy(archivoAlumnos.toPath(), backupPath.toPath());
                System.out.println("📦 [Backup Automático] Copia de seguridad creada en: " + backupPath.getPath());

                File[] backups = dirBackups.listFiles((dir, name) -> name.startsWith("alumnos_backup_") && name.endsWith(".txt"));
                if (backups != null && backups.length > 5) {
                    Arrays.sort(backups, Comparator.comparingLong(File::lastModified));
                    for (int i = 0; i < backups.length - 5; i++) {
                        backups[i].delete();
                    }
                }
            } catch (IOException e) {
                System.out.println("⚠️ Advertencia: No se pudo generar la copia de seguridad, pero se continuará con la carga: " + e.getMessage());
            }

            try (BufferedReader lector = new BufferedReader(new FileReader(archivoAlumnos))) {
                String linea;
                int numeroLinea = 0;
                int alumnosCargados = 0;
                int filasInvalidas = 0;

                while ((linea = lector.readLine()) != null) {
                    numeroLinea++;
                    linea = linea.trim();
                    if (linea.isEmpty()) continue;

                    List<String> datos;
                    try {
                        datos = parsearLineaCSV(linea);
                    } catch (IllegalArgumentException e) {
                        System.out.println("⚠️ [Línea " + numeroLinea + "] Fila descartada (" + e.getMessage() + "): " + linea);
                        filasInvalidas++;
                        continue;
                    }

                    if (datos.size() < 4) {
                        System.out.println("⚠️ [Línea " + numeroLinea + "] Fila descartada (estructura incompleta): " + linea);
                        filasInvalidas++;
                        continue;
                    }

                    String cedula = datos.get(0);
                    if (alumnos.containsKey(cedula)) {
                        System.out.println("⚠️ [Línea " + numeroLinea + "] Fila descartada por Cédula/ID duplicado ('" + cedula + "') en el archivo.");
                        filasInvalidas++;
                        continue;
                    }

                    String nombre = datos.get(1);
                    String correo = datos.get(2);
                    String tipoProg = datos.get(3);

                    ProgramaAcademico objProg;
                    if (tipoProg.equals("Diplomado")) {
                        objProg = new Diplomado();
                    } else if (tipoProg.equals("Bootcamp")) {
                        objProg = new Bootcamp();
                    } else if (tipoProg.equals("Curso")) {
                        objProg = new Curso();
                    } else {
                        System.out.println("⚠️ [Línea " + numeroLinea + "] Fila descartada por programa académico desconocido ('" + tipoProg + "').");
                        filasInvalidas++;
                        continue;
                    }

                    List<Integer> notas = new ArrayList<>();
                    boolean notasValidas = true;

                    for (int i = 4; i < datos.size(); i++) {
                        String notaStr = datos.get(i);
                        if (!notaStr.isEmpty()) {
                            try {
                                int nota = Integer.parseInt(notaStr);
                                if (nota >= 0 && nota <= 20) {
                                    notas.add(nota);
                                } else {
                                    System.out.println("⚠️ [Línea " + numeroLinea + "] Nota fuera de rango (0-20): '" + notaStr + "'.");
                                    notasValidas = false;
                                    break;
                                }
                            } catch (NumberFormatException e) {
                                System.out.println("⚠️ [Línea " + numeroLinea + "] Nota mal formada (no numérica): '" + notaStr + "'.");
                                notasValidas = false;
                                break;
                            }
                        }
                    }

                    if (!notasValidas) {
                        filasInvalidas++;
                        continue;
                    }

                    Alumno alumnoObj = new Alumno(cedula, nombre, correo, objProg);
                    alumnoObj.setNotas(notas);
                    alumnoObj.calcularRendimiento();
                    alumnos.put(cedula, alumnoObj);
                    alumnosCargados++;
                }

                System.out.println("📁 Alumnos procesados: " + alumnosCargados + " cargados correctamente." + 
                                   (filasInvalidas > 0 ? " ⚠️ Se descartaron " + filasInvalidas + " filas por datos corruptos, duplicados o inválidos." : ""));
            } catch (IOException e) {
                System.out.println("⚠️ Error crítico al leer alumnos.txt: " + e.getMessage());
            }
        }

        File archivoProfesores = new File("profesores.txt");
        if (archivoProfesores.exists()) {
            try (BufferedReader lector = new BufferedReader(new FileReader(archivoProfesores))) {
                String linea;
                int numLineaProf = 0;
                while ((linea = lector.readLine()) != null) {
                    numLineaProf++;
                    linea = linea.trim();
                    if (!linea.isEmpty()) {
                        List<String> row;
                        try {
                            row = parsearLineaCSV(linea);
                        } catch (IllegalArgumentException e) {
                            System.out.println("⚠️ [Profesor - Línea " + numLineaProf + "] Fila descartada (" + e.getMessage() + ").");
                            continue;
                        }

                        if (row.size() >= 5) {
                            String cedulaProf = row.get(0);
                            if (profesores.containsKey(cedulaProf)) {
                                System.out.println("⚠️ [Profesor - Línea " + numLineaProf + "] Fila descartada por ID duplicado ('" + cedulaProf + "').");
                                continue;
                            }
                            Profesor profObj = new Profesor(
                                cedulaProf, row.get(1), row.get(2), row.get(3), row.get(4)
                            );
                            profesores.put(cedulaProf, profObj);
                        } else {
                            System.out.println("⚠️ [Profesor - Línea " + numLineaProf + "] Fila descartada por datos incompletos.");
                        }
                    }
                }
                System.out.println("📁 Profesores cargados correctamente.");
            } catch (IOException e) {
                System.out.println("⚠️ Error al leer profesores.txt: " + e.getMessage());
            }
        }
    }

    public void registrarAlumno() {
        try {
            while (true) {
                System.out.println("\n--- REGISTRO DE ALUMNO (Escriba 'ESC' para volver) ---");

                String cedula;
                while (true) {
                    cedula = pedir("Cédula/ID (Ej. V-123456): ").toUpperCase();
                    if (cedula.length() > 2 && (cedula.startsWith("V-") || cedula.startsWith("E-")) && cedula.substring(2).matches("\\d+")) {
                        if (alumnos.containsKey(cedula)) {
                            System.out.println("❌ Error: Ya existe un alumno registrado con esa cédula.");
                            String repetir = pedir("¿Desea intentar con otra cédula? (s/n): ").toLowerCase();
                            if (repetir.equals("s") || repetir.equals("si") || repetir.equals("sí")) continue;
                            return;
                        }
                        String confirmacion = pedir("Has ingresado la cédula: " + cedula + ". ¿Es correcta? (s/n): ").toLowerCase();
                        if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) break;
                        System.out.println("🔄 De acuerdo, vamos a ingresarla de nuevo.\n");
                        continue;
                    }
                    System.out.println("❌ Error: Formato inválido. Debe comenzar con V- o E- seguido de números (Ej: V-123456).");
                }

                String nombre;
                while (true) {
                    nombre = pedir("Nombre Completo: ");
                    if (!nombre.isEmpty() && nombre.matches("[a-zA-ZáéíóúÁÉÍÓÚñÑ'\\-.\\s]+")) {
                        String nombreFormateado = formatearNombre(nombre);
                        String confirmacion = pedir("Has ingresado el nombre: " + nombreFormateado + ". ¿Es correcto? (s/n): ").toLowerCase();
                        if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) {
                            nombre = nombreFormateado;
                            break;
                        }
                        System.out.println("🔄 De acuerdo, vamos a ingresar de nuevo el nombre completo.\n");
                        continue;
                    }
                    System.out.println("❌ Error: El nombre debe contener solo letras, espacios, apóstrofos o guiones.");
                }

                String correo;
                while (true) {
                    correo = pedir("Correo Electrónico: ");
                    if (PATRON_CORREO.matcher(correo).matches()) {
                        String confirmacion = pedir("Has ingresado el correo: " + correo + ". ¿Es correcto? (s/n): ").toLowerCase();
                        if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) break;
                        System.out.println("🔄 De acuerdo, vamos a ingresar el correo de nuevo.\n");
                        continue;
                    }
                    System.out.println("❌ Formato de correo inválido. Asegúrese de ingresar una dirección correcta (Ej: usuario@dominio.com).\n");
                }

                ProgramaAcademico programa;
                String tipoPrograma;
                while (true) {
                    System.out.println("\nSeleccione el Tipo de Programa:");
                    System.out.println("1. Curso");
                    System.out.println("2. Diplomado");
                    System.out.println("3. Bootcamp");
                    String opcionProg = pedir("Opción (1-3): ");

                    if (opcionProg.equals("1")) {
                        tipoPrograma = "Curso";
                        programa = new Curso();
                    } else if (opcionProg.equals("2")) {
                        tipoPrograma = "Diplomado";
                        programa = new Diplomado();
                    } else if (opcionProg.equals("3")) {
                        tipoPrograma = "Bootcamp";
                        programa = new Bootcamp();
                    } else {
                        System.out.println("❌ Error: Opción inválida. Debe seleccionar 1, 2 o 3.");
                        continue;
                    }

                    String confirmacion = pedir("Has seleccionado: " + tipoPrograma + ". ¿Es correcto? (s/n): ").toLowerCase();
                    if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) break;
                    System.out.println("🔄 De acuerdo, vamos a seleccionar el tipo de programa de nuevo.\n");
                }

                Alumno nuevoAlumno = new Alumno(cedula, nombre, correo, programa);
                alumnos.put(cedula, nuevoAlumno);
                guardarAlumnosDisco();
                System.out.println("✅ Alumno '" + nombre + "' registrado exitosamente en memoria y en alumnos.txt");

                String continuar = pedir("\n¿Desea registrar otro alumno? (s/n): ").toLowerCase();
                if (!continuar.equals("s") && !continuar.equals("si") && !continuar.equals("sí")) {
                    System.out.println("🔙 Regresando al menú principal...");
                    break;
                }
            }
        } catch (VolverAlMenuException e) {
            System.out.println("🔙 Regresando al menú principal...");
        }
    }

    public void registrarProfesor() {
        try {
            while (true) {
                System.out.println("\n--- REGISTRO DE PROFESOR (Escriba 'ESC' para volver) ---");

                String cedulaProf;
                while (true) {
                    cedulaProf = pedir("Cédula/ID del Profesor (Ej. P-123456): ").toUpperCase();
                    if (cedulaProf.length() > 2 && cedulaProf.startsWith("P-") && cedulaProf.substring(2).matches("\\d+")) {
                        if (profesores.containsKey(cedulaProf)) {
                            System.out.println("❌ Error: Ya existe un profesor registrado con esa cédula.");
                            String repetir = pedir("¿Desea intentar con otra cédula? (s/n): ").toLowerCase();
                            if (repetir.equals("s") || repetir.equals("si") || repetir.equals("sí")) continue;
                            return;
                        }
                        String confirmacion = pedir("Has ingresado la cédula: " + cedulaProf + ". ¿Es correcta? (s/n): ").toLowerCase();
                        if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) break;
                        System.out.println("🔄 De acuerdo, vamos a ingresarla de nuevo.\n");
                        continue;
                    }
                    System.out.println("❌ Error: Formato inválido. Debe comenzar con P- seguido de números (Ej: P-123456).");
                }

                String nombreProf;
                while (true) {
                    nombreProf = pedir("Nombre Completo del Profesor: ");
                    if (!nombreProf.isEmpty() && nombreProf.matches("[a-zA-ZáéíóúÁÉÍÓÚñÑ'\\-.\\s]+")) {
                        String nombreFormateado = formatearNombre(nombreProf);
                        String confirmacion = pedir("Has ingresado el nombre: " + nombreFormateado + ". ¿Es correcto? (s/n): ").toLowerCase();
                        if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) {
                            nombreProf = nombreFormateado;
                            break;
                        }
                        System.out.println("🔄 De acuerdo, vamos a ingresar de nuevo el nombre completo.\n");
                        continue;
                    }
                    System.out.println("❌ Error: Nombre inválido. Solo se permiten letras, espacios, puntos, apóstrofos y guiones.");
                }

                String correoProf;
                while (true) {
                    correoProf = pedir("Correo Electrónico del Profesor: ");
                    if (PATRON_CORREO.matcher(correoProf).matches()) {
                        String confirmacion = pedir("Has ingresado el correo: " + correoProf + ". ¿Es correcto? (s/n): ").toLowerCase();
                        if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) break;
                        System.out.println("🔄 De acuerdo, vamos a ingresar el correo de nuevo.\n");
                        continue;
                    }
                    System.out.println("❌ Formato de correo inválido. Asegúrese de ingresar una dirección correcta (Ej: usuario@dominio.com).");
                }

                String especialidad;
                while (true) {
                    especialidad = pedir("Especialidad del Profesor: ");
                    if (!especialidad.isEmpty() && especialidad.matches("[a-zA-ZáéíóúÁÉÍÓÚñÑ'\\-.\\s]+")) {
                        String espFormateada = formatearNombre(especialidad);
                        String confirmacion = pedir("Has ingresado la especialidad: " + espFormateada + ". ¿Es correcta? (s/n): ").toLowerCase();
                        if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) {
                            especialidad = espFormateada;
                            break;
                        }
                        System.out.println("🔄 De acuerdo, vamos a ingresar la especialidad de nuevo.\n");
                        continue;
                    }
                    System.out.println("❌ Error: La especialidad debe contener solo letras, espacios, apóstrofos o guiones.");
                }

                String materia;
                while (true) {
                    materia = pedir("Materia que imparte (puede incluir comas, ej: Física, Matemáticas): ");
                    if (!materia.isEmpty()) {
                        String matFormateada = formatearNombre(materia);
                        String confirmacion = pedir("Has ingresado la materia: " + matFormateada + ". ¿Es correcta? (s/n): ").toLowerCase();
                        if (confirmacion.equals("s") || confirmacion.equals("si") || confirmacion.equals("sí")) {
                            materia = matFormateada;
                            break;
                        }
                        System.out.println("🔄 De acuerdo, vamos a ingresar la materia de nuevo.\n");
                        continue;
                    }
                    System.out.println("❌ Error: La materia no puede estar vacía.");
                }

                try (BufferedWriter bw = new BufferedWriter(new FileWriter("profesores.txt", true))) {
                    String lineaCSV = escaparCSV(cedulaProf) + "," +
                                      escaparCSV(nombreProf) + "," +
                                      escaparCSV(correoProf) + "," +
                                      escaparCSV(especialidad) + "," +
                                      escaparCSV(materia);
                    bw.write(lineaCSV);
                    bw.newLine();
                    
                    Profesor profesor = new Profesor(cedulaProf, nombreProf, correoProf, especialidad, materia);
                    profesores.put(cedulaProf, profesor);

                    System.out.println("✅ Profesor '" + nombreProf + "' registrado exitosamente en memoria y en profesores.txt");
                } catch (IOException e) {
                    System.out.println("⚠️ Error crítico al guardar en profesores.txt: " + e.getMessage());
                    System.out.println("❌ El profesor NO fue registrado debido a un fallo de escritura en disco.");
                }

                String continuar = pedir("\n¿Desea registrar otro profesor? (s/n): ").toLowerCase();
                if (!continuar.equals("s") && !continuar.equals("si") && !continuar.equals("sí")) {
                    System.out.println("🔙 Regresando al menú principal...");
                    break;
                }
            }
        } catch (VolverAlMenuException e) {
            System.out.println("🔙 Regresando al menú principal...");
        }
    }

    public void registrarNotasAlumno() {
        if (alumnos.isEmpty()) {
            System.out.println("❌ No hay alumnos registrados en el sistema.");
            return;
        }

        try {
            while (true) {
                System.out.println("\n--- REGISTRO DE NOTAS (Escriba 'ESC' para volver) ---");

                String cedulaBuscar;
                while (true) {
                    cedulaBuscar = pedir("Cédula/ID del Alumno a calificar (Ej. V-123456): ").toUpperCase();
                    if (cedulaBuscar.length() > 2 && (cedulaBuscar.startsWith("V-") || cedulaBuscar.startsWith("E-")) && cedulaBuscar.substring(2).matches("\\d+")) {
                        break;
                    }
                    System.out.println("❌ Error: Formato inválido. Debe comenzar con V- o E- seguido de números.");
                }

                Alumno alumnoInfo = alumnos.get(cedulaBuscar);
                if (alumnoInfo == null) {
                    System.out.println("❌ No se encontró ningún alumno registrado con la cédula " + cedulaBuscar + ".");
                    String repetir = pedir("¿Desea buscar otro alumno? (s/n): ").toLowerCase();
                    if (repetir.equals("s") || repetir.equals("si") || repetir.equals("sí")) continue;
                    return;
                }

                String tipoProg = alumnoInfo.getPrograma().getNombre();
                System.out.println("✅ Alumno encontrado: " + alumnoInfo.getNombre() + " | Programa: " + tipoProg);

                List<Integer> calificacionesTemporales = new ArrayList<>();
                System.out.println("\nIngrese las 3 calificaciones ENTERAS (Escala de 0 a 20) para el " + tipoProg + ":");
                for (int i = 1; i <= 3; i++) {
                    while (true) {
                        try {
                            String notaStr = pedir("Calificación " + i + " (0-20): ");
                            int nota = Integer.parseInt(notaStr);
                            if (nota >= 0 && nota <= 20) {
                                calificacionesTemporales.add(nota);
                                break;
                            }
                            System.out.println("❌ Error: La nota debe estar entre 0 y 20.");
                        } catch (NumberFormatException e) {
                            System.out.println("❌ Error: Debe ingresar un valor numérico entero válido.");
                        }
                    }
                }

                List<Integer> notasAnteriores = new ArrayList<>(alumnoInfo.getNotas());
                List<Integer> notasActualizadas = new ArrayList<>(alumnoInfo.getNotas());
                notasActualizadas.addAll(calificacionesTemporales);

                alumnoInfo.setNotas(notasActualizadas);
                alumnoInfo.calcularRendimiento();
                guardarAlumnosDisco();

                pilaNotas.push(new NotaAccion(cedulaBuscar, notasAnteriores));

                String criterioTxt;
                if (tipoProg.equals("Diplomado")) {
                    criterioTxt = String.format(Locale.US, "Promedio requerido: >= 14.0 (Tu promedio: %.2f)", alumnoInfo.getPromedio());
                } else if (tipoProg.equals("Bootcamp")) {
                    criterioTxt = "Requisito Bootcamp: Ninguna nota individual puede ser menor a 14";
                } else {
                    criterioTxt = String.format(Locale.US, "Promedio requerido: >= 10.0 (Tu promedio: %.2f)", alumnoInfo.getPromedio());
                }

                System.out.println("\n=============================================");
                System.out.println("📊 RESULTADOS FINALES PARA: " + alumnoInfo.getNombre());
                System.out.println("Notas registradas: " + calificacionesTemporales);
                System.out.println("Promedio obtenido: " + String.format(Locale.US, "%.2f", alumnoInfo.getPromedio()));
                System.out.println("Criterio aplicado: " + criterioTxt);
                System.out.println("Estado Final: " + alumnoInfo.getEstado());
                System.out.println("=============================================");

                String continuar = pedir("\n¿Desea registrar notas al alumno u otro? (s/n): ").toLowerCase();
                if (!continuar.equals("s") && !continuar.equals("si") && !continuar.equals("sí")) {
                    System.out.println("🔙 Regresando al menú principal...");
                    break;
                }
            }
        } catch (VolverAlMenuException e) {
            System.out.println("\n🔙 [ESC detectado] Cancelando registro de notas y regresando al menú principal...");
        }
    }

    public void deshacerUltimaNota() {
        System.out.println("\n--- DESHACER ÚLTIMO REGISTRO DE NOTA (LIFO) ---");
        if (pilaNotas.isEmpty()) {
            System.out.println("⚠️ No hay modificaciones previas en la pila para deshacer.");
            return;
        }

        NotaAccion ultimaAccion = pilaNotas.pop();
        Alumno alumno = alumnos.get(ultimaAccion.cedula);
        if (alumno != null) {
            alumno.setNotas(ultimaAccion.notasAnteriores);
            alumno.calcularRendimiento();
            guardarAlumnosDisco();
            System.out.println("↩️ Se ha deshecho la última modificación de notas para el alumno: " + alumno.getNombre() + " (Cédula: " + ultimaAccion.cedula + ").");
        } else {
            System.out.println("⚠️ El alumno asociado ya no existe en el sistema.");
        }
    }

    public void generarColaCertificados() {
        List<Alumno> alumnosAprobados = new ArrayList<>();
        for (Alumno a : alumnos.values()) {
            if (a.getEstado().equals("APROBADO")) {
                alumnosAprobados.add(a);
            }
        }

        if (alumnosAprobados.isEmpty()) {
            System.out.println("\n⚠️ No hay alumnos aprobados en cola para emisión de certificados.");
            return;
        }

        alumnosAprobados.sort(Comparator.comparing(Alumno::getCedula));

        Queue<Alumno> colaCertificados = new LinkedList<>(alumnosAprobados);
        int totalGraduandos = colaCertificados.size();

        StringBuilder reporte = new StringBuilder();
        reporte.append("=========================================\n");
        reporte.append("REPORTE DE CERTIFICADOS PENDIENTES\n");
        reporte.append("=========================================\n");
        reporte.append("Total de graduandos en cola: ").append(totalGraduandos).append("\n");

        int contador = 1;
        while (!colaCertificados.isEmpty()) {
            Alumno al = colaCertificados.poll();
            String progNombre = al.getPrograma().getNombre();
            
            String estatusTxt;
            if (progNombre.equals("Bootcamp")) {
                estatusTxt = "APROBADO (Cumple regla de ninguna nota < 14)";
            } else {
                estatusTxt = "APROBADO";
            }

            reporte.append(contador).append(". [").append(al.getCedula()).append("] ").append(al.getNombre()).append("\n");
            reporte.append("- Programa: ").append(progNombre).append("\n");
            reporte.append("- Promedio Final: ").append(String.format(Locale.US, "%.1f", al.getPromedio())).append("\n");
            reporte.append("- Estatus: ").append(estatusTxt).append("\n");
            
            contador++;
        }

        reporte.append("=========================================\n");
        reporte.append("- Fin del reporte - Generado por SGA-DO *");

        System.out.println();
        System.out.println(reporte.toString());

        try (PrintWriter writer = new PrintWriter(new FileWriter("certificados_pendientes.txt", false))) {
            writer.print(reporte.toString());
            System.out.println("\n📄 Archivo 'certificados_pendientes.txt' guardado exitosamente.");
        } catch (IOException e) {
            System.out.println("⚠️ Error al escribir el archivo de certificados: " + e.getMessage());
        }
    }

    public void mostrarReporteGeneral() {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("📋 REPORTE GENERAL DEL SISTEMA ACADÉMICO");
        System.out.println("=".repeat(60));

        List<Profesor> profesoresOrdenados = new ArrayList<>(profesores.values());
        profesoresOrdenados.sort(Comparator.comparing(Profesor::getCedula));

        System.out.println("\n--- PROFESORES REGISTRADOS (" + profesoresOrdenados.size() + ") ---");
        if (profesoresOrdenados.isEmpty()) {
            System.out.println("No hay profesores registrados.");
        } else {
            for (Profesor p : profesoresOrdenados) {
                System.out.println("ID: " + p.getCedula() + " | Nombre: " + p.getNombre() + " | Materia: " + p.getMateria() + " (" + p.getEspecialidad() + ")");
            }
        }

        List<Alumno> alumnosOrdenados = new ArrayList<>(alumnos.values());
        alumnosOrdenados.sort(Comparator.comparing(Alumno::getCedula));

        System.out.println("\n--- ALUMNOS REGISTRADOS (" + alumnosOrdenados.size() + ") ---");
        if (alumnosOrdenados.isEmpty()) {
            System.out.println("No hay alumnos registrados.");
        } else {
            for (Alumno a : alumnosOrdenados) {
                String prog = a.getPrograma() != null ? a.getPrograma().getNombre() : "N/A";
                String notasTxt = a.getNotas().isEmpty() ? "Sin notas" : a.getNotas().toString().replace("[", "").replace("]", "");
                System.out.println("ID: " + a.getCedula() + " | Nombre: " + a.getNombre() + " | Prog: " + prog + " | Notas: [" + notasTxt + "] | Prom: " + String.format(Locale.US, "%.1f", a.getPromedio()) + " | Estado: " + a.getEstado());
            }
        }
        System.out.println("=".repeat(60));
    }

    // ==========================================
    // BUCLE PRINCIPAL DE CONSOLA
    // ==========================================
    public static void main(String[] args) {
        try {
            System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8.name()));
        } catch (UnsupportedEncodingException e) {
            System.err.println("⚠️ No se pudo establecer la codificación UTF-8 para la consola: " + e.getMessage());
        }

        Scanner sc = new Scanner(System.in);
        SistemaGestionAcademica sistema = new SistemaGestionAcademica(sc);

        while (true) {
            System.out.println("\n==================================================");
            System.out.println("SGA-DO: SISTEMA DIPLOMADOSONLINE");
            System.out.println("==================================================");
            System.out.println("1. Registrar Alumno");
            System.out.println("2. Registrar Profesor");
            System.out.println("3. Registrar Notas a un Alumno");
            System.out.println("4. Deshacer Último Registro de Nota");
            System.out.println("5. Generar Cola de Certificados");
            System.out.println("6. Mostrar Reporte General");
            System.out.println("7. Salir");
            System.out.println("==================================================");
            System.out.print("Seleccione una opción (1-7): ");

            String entrada = sc.nextLine().trim();
            int opcion;
            
            try {
                opcion = Integer.parseInt(entrada);
            } catch (NumberFormatException e) {
                System.out.println("\n❌ Error: Opción inválida o número demasiado grande.");
                System.out.print("\nPresione Enter para continuar...");
                sc.nextLine();
                continue;
            }

            switch (opcion) {
                case 1:
                    sistema.registrarAlumno();
                    System.out.print("\nPresione Enter para volver al menú...");
                    sc.nextLine();
                    break;
                case 2:
                    sistema.registrarProfesor();
                    System.out.print("\nPresione Enter para volver al menú...");
                    sc.nextLine();
                    break;
                case 3:
                    sistema.registrarNotasAlumno();
                    System.out.print("\nPresione Enter para volver al menú...");
                    sc.nextLine();
                    break;
                case 4:
                    sistema.deshacerUltimaNota();
                    System.out.print("\nPresione Enter para volver al menú...");
                    sc.nextLine();
                    break;
                case 5:
                    sistema.generarColaCertificados();
                    System.out.print("\nPresione Enter para volver al menú...");
                    sc.nextLine();
                    break;
                case 6:
                    sistema.mostrarReporteGeneral();
                    System.out.print("\nPresione Enter para volver al menú...");
                    sc.nextLine();
                    break;
                case 7:
                    System.out.println("\n💾 Guardando cambios pendientes y cerrando la aplicación de forma segura...");
                    sistema.guardarAlumnosDisco();
                    sc.close();
                    return;
                default:
                    System.out.println("\n❌ Opción inválida. Por favor, seleccione un número entre 1 y 7.");
                    System.out.print("\nPresione Enter para continuar...");
                    sc.nextLine();
                    break;
            }
        }
    }
}