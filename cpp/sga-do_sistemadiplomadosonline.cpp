#include <algorithm>
#include <cctype>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <queue>
#include <sstream>
#include <stack>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#ifdef _WIN32
#include <conio.h>
#include <windows.h>
#endif

namespace fs = std::filesystem;

// ==========================================
// EXCEPCIÓN PERSONALIZADA PARA ESC
// ==========================================
class VolverAlMenuException : public std::runtime_error {
public:
    explicit VolverAlMenuException(const std::string& mensaje = "Regresando al menú principal...")
        : std::runtime_error(mensaje) {}
};

// ==========================================
// UTILIDADES DE CONSOLA Y CADENAS
// ==========================================
static std::string trim(const std::string& str) {
    size_t inicio = 0;
    while (inicio < str.size() && std::isspace(static_cast<unsigned char>(str[inicio]))) {
        ++inicio;
    }
    size_t fin = str.size();
    while (fin > inicio && std::isspace(static_cast<unsigned char>(str[fin - 1]))) {
        --fin;
    }
    return str.substr(inicio, fin - inicio);
}

static std::string toLower(const std::string& str) {
    std::string res = str;
    for (char& c : res) {
        c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    }
    return res;
}

static std::string toUpper(const std::string& str) {
    std::string res = str;
    for (char& c : res) {
        c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    }
    return res;
}

static std::string toTitle(const std::string& str) {
    std::string res = toLower(str);
    bool nuevaPalabra = true;
    for (char& c : res) {
        if (std::isspace(static_cast<unsigned char>(c))) {
            nuevaPalabra = true;
        } else if (nuevaPalabra) {
            c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
            nuevaPalabra = false;
        }
    }
    return res;
}

static bool esDigitoStr(const std::string& str) {
    if (str.empty()) return false;
    for (char c : str) {
        if (!std::isdigit(static_cast<unsigned char>(c))) return false;
    }
    return true;
}

static bool esConfirmacionSi(const std::string& resp) {
    std::string r = toLower(trim(resp));
    return (r == "s" || r == "si" || r == "sí");
}

static bool leerInputConEscape(const std::string& mensaje, std::string& salida) {
    std::cout << mensaje << std::flush;

#ifdef _WIN32
    std::string chars;
    while (true) {
        if (_kbhit()) {
            int ch = _getch();
            if (ch == 27) { // Código ASCII de ESC (\x1b)
                std::cout << "\n\n🔙 [ESC detectado] Cancelando y regresando al menú principal...\n";
                return false;
            } else if (ch == '\r' || ch == '\n') {
                std::cout << "\n";
                salida = chars;
                return true;
            } else if (ch == 8) { // Backspace
                if (!chars.empty()) {
                    chars.pop_back();
                    std::cout << "\b \b" << std::flush;
                }
            } else if (ch >= 32 && ch <= 126) {
                char c = static_cast<char>(ch);
                chars.push_back(c);
                std::cout << c << std::flush;
            }
        }
    }
#else
    if (!std::getline(std::cin, salida)) {
        return false;
    }
    if (toUpper(trim(salida)) == "ESC") {
        std::cout << "\n🔙 [ESC detectado] Cancelando y regresando al menú principal...\n";
        return false;
    }
    return true;
#endif
}

static std::string obtenerTimestamp() {
    auto ahora = std::chrono::system_clock::now();
    std::time_t tiempo = std::chrono::system_clock::to_time_t(ahora);
    std::tm tmLocal{};
#ifdef _WIN32
    localtime_s(&tmLocal, &tiempo);
#else
    localtime_r(&tiempo, &tmLocal);
#endif
    std::ostringstream oss;
    oss << std::put_time(&tmLocal, "%Y%m%d_%H%M%S");
    return oss.str();
}

// ==========================================
// CLASES DE PROGRAMAS ACADÉMICOS (POO + POLIMORFISMO)
// ==========================================
class ProgramaAcademico {
protected:
    std::string nombre;

public:
    explicit ProgramaAcademico(const std::string& nombre) : nombre(nombre) {}
    virtual ~ProgramaAcademico() = default;

    std::string getNombre() const { return nombre; }
    virtual bool estaAprobado(double promedio, const std::vector<int>& notas) const = 0;
    virtual std::string getEstatusCertificado() const = 0;
    virtual std::unique_ptr<ProgramaAcademico> clonar() const = 0;
};

class Curso : public ProgramaAcademico {
public:
    Curso() : ProgramaAcademico("Curso") {}

    bool estaAprobado(double promedio, const std::vector<int>&) const override {
        return promedio >= 10.0;
    }

    std::string getEstatusCertificado() const override {
        return "APROBADO";
    }

    std::unique_ptr<ProgramaAcademico> clonar() const override {
        return std::make_unique<Curso>(*this);
    }
};

class Diplomado : public ProgramaAcademico {
public:
    Diplomado() : ProgramaAcademico("Diplomado") {}

    bool estaAprobado(double promedio, const std::vector<int>&) const override {
        return promedio >= 14.0;
    }

    std::string getEstatusCertificado() const override {
        return "APROBADO";
    }

    std::unique_ptr<ProgramaAcademico> clonar() const override {
        return std::make_unique<Diplomado>(*this);
    }
};

class Bootcamp : public ProgramaAcademico {
public:
    Bootcamp() : ProgramaAcademico("Bootcamp") {}

    bool estaAprobado(double, const std::vector<int>& notas) const override {
        for (int nota : notas) {
            if (nota < 14) {
                return false;
            }
        }
        return !notas.empty();
    }

    std::string getEstatusCertificado() const override {
        return "APROBADO (Cumple regla de ninguna nota < 14)";
    }

    std::unique_ptr<ProgramaAcademico> clonar() const override {
        return std::make_unique<Bootcamp>(*this);
    }
};

// ==========================================
// CLASES DE PERSONAS (HERENCIA)
// ==========================================
class Persona {
protected:
    std::string cedula;
    std::string nombre;
    std::string correo;

public:
    Persona(const std::string& cedula, const std::string& nombre, const std::string& correo)
        : cedula(cedula), nombre(nombre), correo(correo) {}

    virtual ~Persona() = default;

    std::string getCedula() const { return cedula; }
    std::string getNombre() const { return nombre; }
    std::string getCorreo() const { return correo; }
};

class Alumno : public Persona {
private:
    std::unique_ptr<ProgramaAcademico> programa;
    std::vector<int> notas;
    double promedio;
    std::string estado;

public:
    Alumno(const std::string& cedula,
           const std::string& nombre,
           const std::string& correo,
           std::unique_ptr<ProgramaAcademico> prog)
        : Persona(cedula, nombre, correo),
          programa(std::move(prog)),
          promedio(0.0),
          estado("PENDIENTE") {}

    const ProgramaAcademico* getPrograma() const { return programa.get(); }
    const std::vector<int>& getNotas() const { return notas; }
    std::vector<int>& getNotasModificables() { return notas; }
    void setNotas(const std::vector<int>& nuevasNotas) { notas = nuevasNotas; }
    double getPromedio() const { return promedio; }
    std::string getEstado() const { return estado; }

    void calcularRendimiento() {
        if (notas.empty()) {
            promedio = 0.0;
            estado = "PENDIENTE";
            return;
        }

        int suma = 0;
        for (int nota : notas) {
            suma += nota;
        }
        promedio = static_cast<double>(suma) / static_cast<double>(notas.size());

        bool aprobado = false;
        if (programa != nullptr) {
            aprobado = programa->estaAprobado(promedio, notas);
        } else {
            aprobado = (promedio >= 10.0);
        }

        estado = aprobado ? "APROBADO" : "REPROBADO";
    }
};

class Profesor : public Persona {
private:
    std::string especialidad;
    std::string materia;

public:
    Profesor(const std::string& cedula,
             const std::string& nombre,
             const std::string& correo,
             const std::string& especialidad,
             const std::string& materia)
        : Persona(cedula, nombre, correo),
          especialidad(especialidad),
          materia(materia) {}

    std::string getEspecialidad() const { return especialidad; }
    std::string getMateria() const { return materia; }
};

struct AccionNota {
    std::string cedula;
    int nota;
};

// ==========================================
// CONTROLADOR DEL SISTEMA (MOTOR BACKEND)
// ==========================================
class SistemaGestionAcademica {
private:
    std::unordered_map<std::string, std::unique_ptr<Alumno>> alumnos;
    std::unordered_map<std::string, std::unique_ptr<Profesor>> profesores;
    std::stack<AccionNota> pilaNotas;

    static std::unique_ptr<ProgramaAcademico> crearProgramaPorNombre(const std::string& tipoProg) {
        if (tipoProg == "Diplomado") {
            return std::make_unique<Diplomado>();
        } else if (tipoProg == "Bootcamp") {
            return std::make_unique<Bootcamp>();
        }
        return std::make_unique<Curso>();
    }

public:
    SistemaGestionAcademica() {
        cargarDatosAlmacenados();
    }

    std::string pedir(const std::string& mensaje) const {
        std::string res;
        if (!leerInputConEscape(mensaje, res)) {
            throw VolverAlMenuException();
        }
        return trim(res);
    }

    void guardarAlumnosDisco() const {
        std::ofstream archivo("alumnos.txt", std::ios::out | std::ios::trunc);
        if (!archivo.is_open()) {
            std::cout << "⚠️ Error al actualizar alumnos.txt\n";
            return;
        }

        for (const auto& par : alumnos) {
            const Alumno* al = par.second.get();
            std::string tipoProg = (al->getPrograma() != nullptr) ? al->getPrograma()->getNombre() : "Curso";
            std::ostringstream notasOss;
            const auto& listaNotas = al->getNotas();
            for (size_t i = 0; i < listaNotas.size(); ++i) {
                notasOss << listaNotas[i];
                if (i + 1 < listaNotas.size()) {
                    notasOss << ",";
                }
            }
            std::string notasStr = notasOss.str();
            archivo << al->getCedula() << ","
                    << al->getNombre() << ","
                    << al->getCorreo() << ","
                    << tipoProg << ","
                    << notasStr << "\n";
        }
    }

    void cargarDatosAlmacenados() {
        // 1. Cargar Alumnos y generar copia de seguridad automática
        if (fs::exists("alumnos.txt")) {
            try {
                fs::create_directories("backups");
                std::string timestamp = obtenerTimestamp();
                fs::path backupPath = fs::path("backups") / ("alumnos_backup_" + timestamp + ".txt");

                fs::copy_file("alumnos.txt", backupPath, fs::copy_options::overwrite_existing);
                std::cout << "📦 [Backup Automático] Copia de seguridad creada en: " << backupPath.string() << "\n";

                std::ifstream archivo("alumnos.txt");
                std::string linea;
                while (std::getline(archivo, linea)) {
                    linea = trim(linea);
                    if (linea.empty()) continue;

                    std::vector<std::string> datos;
                    std::stringstream ss(linea);
                    std::string campo;
                    while (std::getline(ss, campo, ',')) {
                        datos.push_back(trim(campo));
                    }

                    if (datos.size() >= 4) {
                        std::string cedula = datos[0];
                        std::string nombre = datos[1];
                        std::string correo = datos[2];
                        std::string tipoProg = datos[3];

                        std::vector<int> notas;
                        for (size_t i = 4; i < datos.size(); ++i) {
                            if (esDigitoStr(datos[i])) {
                                notas.push_back(std::stoi(datos[i]));
                            }
                        }

                        auto objProg = crearProgramaPorNombre(tipoProg);
                        auto alumnoObj = std::make_unique<Alumno>(cedula, nombre, correo, std::move(objProg));
                        alumnoObj->setNotas(notas);
                        alumnoObj->calcularRendimiento();
                        alumnos[cedula] = std::move(alumnoObj);
                    }
                }
                std::cout << "📁 Alumnos cargados correctamente desde alumnos.txt.\n";
            } catch (const std::exception& e) {
                std::cout << "⚠️ Error al leer o respaldar alumnos.txt: " << e.what() << "\n";
            }
        }

        // 2. Cargar Profesores
        if (fs::exists("profesores.txt")) {
            try {
                std::ifstream archivo("profesores.txt");
                std::string linea;
                while (std::getline(archivo, linea)) {
                    linea = trim(linea);
                    if (linea.empty()) continue;

                    std::vector<std::string> row;
                    std::stringstream ss(linea);
                    std::string campo;
                    while (std::getline(ss, campo, ',')) {
                        row.push_back(trim(campo));
                    }

                    if (row.size() >= 5) {
                        auto profObj = std::make_unique<Profesor>(row[0], row[1], row[2], row[3], row[4]);
                        profesores[row[0]] = std::move(profObj);
                    }
                }
                std::cout << "📁 Profesores cargados correctamente.\n";
            } catch (const std::exception& e) {
                std::cout << "⚠️ Error al leer profesores.txt: " << e.what() << "\n";
            }
        }
    }

    void registrarAlumno() {
        try {
            while (true) {
                std::cout << "\n--- REGISTRO DE ALUMNO (Presione [ESC] para volver) ---\n";

                std::string cedula;
                while (true) {
                    cedula = toUpper(pedir("Cédula/ID (Ej. V-123456): "));
                    if (cedula.size() > 2 &&
                        (cedula.rfind("V-", 0) == 0 || cedula.rfind("E-", 0) == 0) &&
                        esDigitoStr(cedula.substr(2))) {
                        if (alumnos.find(cedula) != alumnos.end()) {
                            std::cout << "❌ Error: Ya existe un alumno registrado con esa cédula.\n";
                            std::string repetir = pedir("¿Desea intentar con otra cédula? (s/n): ");
                            if (esConfirmacionSi(repetir)) {
                                continue;
                            }
                            return;
                        }

                        std::string confirmacion = pedir("Has ingresado la cédula: " + cedula + ". ¿Es correcta? (s/n): ");
                        if (esConfirmacionSi(confirmacion)) {
                            break;
                        }
                        std::cout << "🔄 De acuerdo, vamos a ingresarla de nuevo.\n\n";
                        continue;
                    }
                    std::cout << "❌ Error: Formato inválido. Debe comenzar con V- o E- seguido de números (Ej: V-123456).\n";
                }

                std::string nombre;
                while (true) {
                    nombre = pedir("Nombre Completo: ");
                    std::string sinEspacios = nombre;
                    sinEspacios.erase(std::remove(sinEspacios.begin(), sinEspacios.end(), ' '), sinEspacios.end());
                    if (!nombre.empty() && !sinEspacios.empty() &&
                        std::all_of(sinEspacios.begin(), sinEspacios.end(), [](unsigned char c) {
                            return std::isalpha(c);
                        })) {
                        std::string nombreFormateado = toTitle(nombre);
                        std::string confirmacion = pedir("Has ingresado el nombre: " + nombreFormateado + ". ¿Es correcto? (s/n): ");
                        if (esConfirmacionSi(confirmacion)) {
                            nombre = nombreFormateado;
                            break;
                        }
                        std::cout << "🔄 De acuerdo, vamos a ingresar de nuevo el nombre completo.\n\n";
                        continue;
                    }
                    std::cout << "❌ Error: El nombre debe contener solo letras.\n";
                }

                std::string correo;
                while (true) {
                    correo = pedir("Correo Electrónico: ");
                    size_t arroba = correo.find('@');
                    size_t punto = (arroba != std::string::npos) ? correo.find('.', arroba) : std::string::npos;
                    if (arroba != std::string::npos && punto != std::string::npos && punto < correo.size() - 1) {
                        std::string confirmacion = pedir("Has ingresado el correo: " + correo + ". ¿Es correcto? (s/n): ");
                        if (esConfirmacionSi(confirmacion)) {
                            break;
                        }
                        std::cout << "🔄 De acuerdo, vamos a ingresar el correo de nuevo.\n\n";
                        continue;
                    }
                    std::cout << "❌ Formato inválido. Asegúrate de incluir '@' y un dominio válido.\n\n";
                }

                std::unique_ptr<ProgramaAcademico> programa;
                std::string tipoPrograma;
                while (true) {
                    std::cout << "\nSeleccione el Tipo de Programa:\n";
                    std::cout << "1. Curso\n";
                    std::cout << "2. Diplomado\n";
                    std::cout << "3. Bootcamp\n";

                    std::string opcionPrograma = pedir("Opción (1-3): ");

                    if (opcionPrograma == "1") {
                        tipoPrograma = "Curso";
                        programa = std::make_unique<Curso>();
                    } else if (opcionPrograma == "2") {
                        tipoPrograma = "Diplomado";
                        programa = std::make_unique<Diplomado>();
                    } else if (opcionPrograma == "3") {
                        tipoPrograma = "Bootcamp";
                        programa = std::make_unique<Bootcamp>();
                    } else {
                        std::cout << "❌ Error: Opción inválida. Debe seleccionar 1, 2 o 3.\n";
                        continue;
                    }

                    std::string confirmacion = pedir("Has seleccionado: " + tipoPrograma + ". ¿Es correcto? (s/n): ");
                    if (esConfirmacionSi(confirmacion)) {
                        break;
                    }
                    std::cout << "🔄 De acuerdo, vamos a seleccionar el tipo de programa de nuevo.\n\n";
                }

                auto nuevoAlumno = std::make_unique<Alumno>(cedula, nombre, correo, std::move(programa));
                alumnos[cedula] = std::move(nuevoAlumno);
                guardarAlumnosDisco();
                std::cout << "✅ Alumno '" << nombre << "' registrado exitosamente en memoria y en alumnos.txt\n";

                std::string continuar = pedir("\n¿Desea registrar otro alumno? (s/n): ");
                if (!esConfirmacionSi(continuar)) {
                    std::cout << "🔙 Regresando al menú principal...\n";
                    break;
                }
            }
        } catch (const VolverAlMenuException&) {
            std::cout << "🔙 Regresando al menú principal...\n";
        }
    }

    void registrarProfesor() {
        try {
            while (true) {
                std::cout << "\n--- REGISTRO DE PROFESOR (Presione [ESC] para volver) ---\n";

                std::string cedulaProf;
                while (true) {
                    cedulaProf = toUpper(pedir("Cédula/ID del Profesor (Ej. P-123456): "));
                    if (cedulaProf.size() > 2 &&
                        cedulaProf.rfind("P-", 0) == 0 &&
                        esDigitoStr(cedulaProf.substr(2))) {
                        if (profesores.find(cedulaProf) != profesores.end()) {
                            std::cout << "❌ Error: Ya existe un profesor registrado con esa cédula.\n";
                            std::string repetir = pedir("¿Desea intentar con otra cédula? (s/n): ");
                            if (esConfirmacionSi(repetir)) {
                                continue;
                            }
                            return;
                        }

                        std::string confirmacion = pedir("Has ingresado la cédula: " + cedulaProf + ". ¿Es correcta? (s/n): ");
                        if (esConfirmacionSi(confirmacion)) {
                            break;
                        }
                        std::cout << "🔄 De acuerdo, vamos a ingresarla de nuevo.\n\n";
                        continue;
                    }
                    std::cout << "❌ Error: Formato inválido. Debe comenzar con P- seguido de números (Ej: P-123456).\n";
                }

                std::string nombreProf;
                while (true) {
                    nombreProf = pedir("Nombre Completo del Profesor: ");
                    std::string limpio = nombreProf;
                    limpio.erase(std::remove(limpio.begin(), limpio.end(), ' '), limpio.end());
                    limpio.erase(std::remove(limpio.begin(), limpio.end(), '.'), limpio.end());
                    if (!nombreProf.empty() && !limpio.empty()) {
                        std::string nombreFormateado = toTitle(nombreProf);
                        std::string confirmacion = pedir("Has ingresado el nombre: " + nombreFormateado + ". ¿Es correcto? (s/n): ");
                        if (esConfirmacionSi(confirmacion)) {
                            nombreProf = nombreFormateado;
                            break;
                        }
                        std::cout << "🔄 De acuerdo, vamos a ingresar de nuevo el nombre completo.\n\n";
                        continue;
                    }
                    std::cout << "❌ Error: El nombre debe contener solo letras.\n";
                }

                std::string correoProf;
                while (true) {
                    correoProf = pedir("Correo Electrónico del Profesor: ");
                    size_t arroba = correoProf.find('@');
                    size_t punto = (arroba != std::string::npos) ? correoProf.find('.', arroba) : std::string::npos;
                    if (arroba != std::string::npos && punto != std::string::npos && punto < correoProf.size() - 1) {
                        std::string confirmacion = pedir("Has ingresado el correo: " + correoProf + ". ¿Es correcto? (s/n): ");
                        if (esConfirmacionSi(confirmacion)) {
                            break;
                        }
                        std::cout << "🔄 De acuerdo, vamos a ingresar el correo de nuevo.\n\n";
                        continue;
                    }
                    std::cout << "❌ Formato inválido. Asegúrate de incluir '@' y un dominio válido.\n\n";
                }

                std::string especialidad;
                while (true) {
                    especialidad = pedir("Especialidad del Profesor: ");
                    std::string sinEspacios = especialidad;
                    sinEspacios.erase(std::remove(sinEspacios.begin(), sinEspacios.end(), ' '), sinEspacios.end());
                    if (!especialidad.empty() && !sinEspacios.empty() &&
                        std::all_of(sinEspacios.begin(), sinEspacios.end(), [](unsigned char c) {
                            return std::isalpha(c);
                        })) {
                        std::string espFormateada = toTitle(especialidad);
                        std::string confirmacion = pedir("Has ingresado la especialidad: " + espFormateada + ". ¿Es correcta? (s/n): ");
                        if (esConfirmacionSi(confirmacion)) {
                            especialidad = espFormateada;
                            break;
                        }
                        std::cout << "🔄 De acuerdo, vamos a ingresar la especialidad de nuevo.\n\n";
                        continue;
                    }
                    std::cout << "❌ Error: La especialidad debe contener solo letras.\n";
                }

                std::string materia;
                while (true) {
                    materia = pedir("Materia que imparte: ");
                    if (!materia.empty()) {
                        std::string matFormateada = toTitle(materia);
                        std::string confirmacion = pedir("Has ingresado la materia: " + matFormateada + ". ¿Es correcta? (s/n): ");
                        if (esConfirmacionSi(confirmacion)) {
                            materia = matFormateada;
                            break;
                        }
                        std::cout << "🔄 De acuerdo, vamos a ingresar la materia de nuevo.\n\n";
                        continue;
                    }
                    std::cout << "❌ Error: La materia no puede estar vacía.\n";
                }

                auto profesor = std::make_unique<Profesor>(cedulaProf, nombreProf, correoProf, especialidad, materia);
                profesores[cedulaProf] = std::move(profesor);

                try {
                    std::ofstream f("profesores.txt", std::ios::out | std::ios::app);
                    if (!f.is_open()) {
                        throw std::runtime_error("No se pudo abrir profesores.txt");
                    }
                    f << cedulaProf << "," << nombreProf << "," << correoProf << "," << especialidad << "," << materia << "\n";
                    std::cout << "✅ Profesor '" << nombreProf << "' registrado exitosamente en memoria y en profesores.txt\n";
                } catch (const std::exception& e) {
                    std::cout << "⚠️ Error al guardar en profesores.txt: " << e.what() << "\n";
                }

                std::string continuar = pedir("\n¿Desea registrar otro profesor? (s/n): ");
                if (!esConfirmacionSi(continuar)) {
                    std::cout << "🔙 Regresando al menú principal...\n";
                    break;
                }
            }
        } catch (const VolverAlMenuException&) {
            std::cout << "🔙 Regresando al menú principal...\n";
        }
    }

    void registrarNotasAlumno() {
        if (alumnos.empty()) {
            std::cout << "❌ No hay alumnos registrados en el sistema.\n";
            return;
        }

        try {
            while (true) {
                std::cout << "\n--- REGISTRO DE NOTAS (Presione [ESC] para volver) ---\n";

                std::string cedulaBuscar;
                while (true) {
                    cedulaBuscar = toUpper(pedir("Cédula/ID del Alumno a calificar (Ej. V-123456): "));
                    if (cedulaBuscar.size() > 2 &&
                        (cedulaBuscar.rfind("V-", 0) == 0 || cedulaBuscar.rfind("E-", 0) == 0) &&
                        esDigitoStr(cedulaBuscar.substr(2))) {
                        break;
                    }
                    std::cout << "❌ Error: Formato inválido. Debe comenzar con V- o E- seguido de números.\n";
                }

                auto it = alumnos.find(cedulaBuscar);
                if (it == alumnos.end()) {
                    std::cout << "❌ No se encontró ningún alumno registrado con la cédula " << cedulaBuscar << ".\n";
                    std::string repetir = pedir("¿Desea buscar otro alumno? (s/n): ");
                    if (esConfirmacionSi(repetir)) {
                        continue;
                    }
                    return;
                }

                Alumno* alumnoInfo = it->second.get();
                std::string tipoProg = (alumnoInfo->getPrograma() != nullptr) ? alumnoInfo->getPrograma()->getNombre() : "Curso";
                std::cout << "✅ Alumno encontrado: " << alumnoInfo->getNombre() << " | Programa: " << tipoProg << "\n";

                std::vector<int> calificaciones;
                std::cout << "\nIngrese las 3 calificaciones ENTERAS (Escala de 0 a 20) para el " << tipoProg << ":\n";
                for (int i = 1; i <= 3; ++i) {
                    while (true) {
                        std::string notaStr = pedir("Calificación " + std::to_string(i) + " (0-20): ");
                        if (esDigitoStr(notaStr)) {
                            int nota = std::stoi(notaStr);
                            if (nota >= 0 && nota <= 20) {
                                calificaciones.push_back(nota);
                                alumnoInfo->setNotas(calificaciones);
                                alumnoInfo->calcularRendimiento();
                                guardarAlumnosDisco();
                                break;
                            }
                            std::cout << "❌ Error: La nota debe estar entre 0 y 20.\n";
                        } else {
                            std::cout << "❌ Error: Debe ingresar un valor numérico entero válido.\n";
                        }
                    }
                }

                for (int nota : calificaciones) {
                    pilaNotas.push(AccionNota{cedulaBuscar, nota});
                }

                std::ostringstream criterioOss;
                if (tipoProg == "Diplomado") {
                    criterioOss << "Promedio requerido: >= 14.0 (Tu promedio: "
                                << std::fixed << std::setprecision(2) << alumnoInfo->getPromedio() << ")";
                } else if (tipoProg == "Bootcamp") {
                    criterioOss << "Requisito Bootcamp: Ninguna nota individual puede ser menor a 14";
                } else {
                    criterioOss << "Promedio requerido: >= 10.0 (Tu promedio: "
                                << std::fixed << std::setprecision(2) << alumnoInfo->getPromedio() << ")";
                }

                std::cout << "\n" << std::string(45, '=') << "\n";
                std::cout << "📊 RESULTADOS FINALES PARA: " << alumnoInfo->getNombre() << "\n";
                std::cout << "Notas registradas: [";
                for (size_t i = 0; i < calificaciones.size(); ++i) {
                    std::cout << calificaciones[i] << (i + 1 < calificaciones.size() ? ", " : "");
                }
                std::cout << "]\n";
                std::cout << "Promedio obtenido: " << std::fixed << std::setprecision(2) << alumnoInfo->getPromedio() << "\n";
                std::cout << "Criterio aplicado: " << criterioOss.str() << "\n";
                std::cout << "Estado Final: " << alumnoInfo->getEstado() << "\n";
                std::cout << std::string(45, '=') << "\n";

                std::string continuar = pedir("\n¿Desea registrar notas a otro alumno? (s/n): ");
                if (!esConfirmacionSi(continuar)) {
                    std::cout << "🔙 Regresando al menú principal...\n";
                    break;
                }
            }
        } catch (const VolverAlMenuException&) {
            std::cout << "🔙 Regresando al menú principal...\n";
        }
    }

    void deshacerUltimaNota() {
        std::cout << "\n--- DESHACER ÚLTIMO REGISTRO DE NOTA (LIFO) ---\n";
        if (pilaNotas.empty()) {
            std::cout << "⚠️ No hay notas recientes en la pila para deshacer.\n";
            return;
        }

        AccionNota ultimaAccion = pilaNotas.top();
        pilaNotas.pop();

        auto it = alumnos.find(ultimaAccion.cedula);
        if (it != alumnos.end() && !it->second->getNotas().empty()) {
            Alumno* alumno = it->second.get();
            auto& notas = alumno->getNotasModificables();
            auto pos = std::find(notas.begin(), notas.end(), ultimaAccion.nota);
            if (pos != notas.end()) {
                notas.erase(pos);
            }

            alumno->calcularRendimiento();
            guardarAlumnosDisco();
            std::cout << "↩️ Se ha deshecho la nota " << ultimaAccion.nota
                      << " del alumno " << alumno->getNombre()
                      << " (Cédula: " << ultimaAccion.cedula << ").\n";
        } else {
            std::cout << "⚠️ El alumno asociado ya no tiene notas registradas.\n";
        }
    }

    void generarColaCertificados() const {
        std::vector<const Alumno*> alumnosAprobados;
        for (const auto& par : alumnos) {
            if (par.second->getEstado() == "APROBADO") {
                alumnosAprobados.push_back(par.second.get());
            }
        }

        if (alumnosAprobados.empty()) {
            std::cout << "\n⚠️ No hay alumnos aprobados en cola para emisión de certificados.\n";
            return;
        }

        std::queue<const Alumno*> colaCertificados;
        for (const Alumno* al : alumnosAprobados) {
            colaCertificados.push(al);
        }

        size_t totalGraduandos = colaCertificados.size();

        std::cout << "\n=========================================\n";
        std::cout << "REPORTE DE CERTIFICADOS PENDIENTES\n";
        std::cout << "=========================================\n";
        std::cout << "Total de graduandos en cola: " << totalGraduandos << "\n\n";

        int contador = 1;
        std::vector<std::string> lineasArchivo = {
            "=========================================\n",
            "REPORTE DE CERTIFICADOS PENDIENTES\n",
            "=========================================\n",
            "Total de graduandos en cola: " + std::to_string(totalGraduandos) + "\n\n"
        };

        while (!colaCertificados.empty()) {
            const Alumno* al = colaCertificados.front();
            colaCertificados.pop();

            std::string progNombre = (al->getPrograma() != nullptr) ? al->getPrograma()->getNombre() : "Curso";
            std::string estatusTxt = (al->getPrograma() != nullptr)
                                         ? al->getPrograma()->getEstatusCertificado()
                                         : "APROBADO";

            std::ostringstream promStream;
            promStream << std::fixed << std::setprecision(1) << al->getPromedio();

            std::string bloque =
                std::to_string(contador) + ". [" + al->getCedula() + "] " + al->getNombre() + "\n" +
                "- Programa: " + progNombre + "\n" +
                "- Promedio Final: " + promStream.str() + "\n" +
                "- Estatus: " + estatusTxt + "\n\n";

            std::cout << bloque;
            lineasArchivo.push_back(bloque);
            ++contador;
        }

        std::string piePagina = "=========================================\n- Fin del reporte - Generado por SGA-DO *";
        std::cout << piePagina << "\n";
        lineasArchivo.push_back(piePagina);

        try {
            std::ofstream f("certificados_pendientes.txt", std::ios::out | std::ios::trunc);
            if (!f.is_open()) {
                throw std::runtime_error("No se pudo abrir certificados_pendientes.txt");
            }
            for (const auto& linea : lineasArchivo) {
                f << linea;
            }
            std::cout << "\n📄 Archivo 'certificados_pendientes.txt' guardado exitosamente.\n";
        } catch (const std::exception& e) {
            std::cout << "⚠️ Error al escribir el archivo de certificados: " << e.what() << "\n";
        }
    }

    void mostrarReporteGeneral() const {
        std::cout << "\n" << std::string(60, '=') << "\n";
        std::cout << "📋 REPORTE GENERAL DEL SISTEMA ACADÉMICO\n";
        std::cout << std::string(60, '=') << "\n";

        std::cout << "\n--- PROFESORES REGISTRADOS (" << profesores.size() << ") ---\n";
        if (profesores.empty()) {
            std::cout << "No hay profesores registrados.\n";
        } else {
            for (const auto& par : profesores) {
                const Profesor* p = par.second.get();
                std::cout << "ID: " << p->getCedula()
                          << " | Nombre: " << p->getNombre()
                          << " | Materia: " << p->getMateria()
                          << " (" << p->getEspecialidad() << ")\n";
            }
        }

        std::cout << "\n--- ALUMNOS REGISTRADOS (" << alumnos.size() << ") ---\n";
        if (alumnos.empty()) {
            std::cout << "No hay alumnos registrados.\n";
        } else {
            for (const auto& par : alumnos) {
                const Alumno* a = par.second.get();
                std::string prog = (a->getPrograma() != nullptr) ? a->getPrograma()->getNombre() : "N/A";
                std::string notasTxt = "Sin notas";
                if (!a->getNotas().empty()) {
                    std::ostringstream oss;
                    for (size_t i = 0; i < a->getNotas().size(); ++i) {
                        oss << a->getNotas()[i];
                        if (i + 1 < a->getNotas().size()) oss << ", ";
                    }
                    notasTxt = oss.str();
                }
                std::cout << "ID: " << a->getCedula()
                          << " | Nombre: " << a->getNombre()
                          << " | Prog: " << prog
                          << " | Notas: [" << notasTxt << "]"
                          << " | Prom: " << std::fixed << std::setprecision(1) << a->getPromedio()
                          << " | Estado: " << a->getEstado() << "\n";
            }
        }
        std::cout << std::string(60, '=') << "\n";
    }
};

// ==========================================
// BUCLE PRINCIPAL DE CONSOLA
// ==========================================
int main() {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    std::system("color 17");
#endif

    SistemaGestionAcademica sistema;

    while (true) {
#ifdef _WIN32
        std::system("cls");
#else
        std::system("clear");
#endif

        std::cout << "\n==================================================\n";
        std::cout << "SGA-DO: SISTEMA DIPLOMADOSONLINE\n";
        std::cout << "==================================================\n";
        std::cout << "1. Registrar Alumno\n";
        std::cout << "2. Registrar Profesor\n";
        std::cout << "3. Registrar Notas a un Alumno\n";
        std::cout << "4. Deshacer Último Registro de Nota\n";
        std::cout << "5. Generar Cola de Certificados\n";
        std::cout << "6. Mostrar Reporte General\n";
        std::cout << "7. Salir\n";
        std::cout << "==================================================\n";
        std::cout << "Seleccione una opción (1-7): ";

        std::string entrada;
        if (!std::getline(std::cin, entrada)) {
            break;
        }
        entrada = trim(entrada);

        if (!esDigitoStr(entrada)) {
            std::cout << "\n❌ Error: Debe ingresar un valor numérico válido (no letras ni símbolos).\n";
            std::cout << "\nPresione Enter para continuar...";
            std::string pausa;
            std::getline(std::cin, pausa);
            continue;
        }

        int opcion = std::stoi(entrada);

        if (opcion == 1) {
            sistema.registrarAlumno();
            std::cout << "\nPresione Enter para volver al menú...";
            std::string pausa;
            std::getline(std::cin, pausa);
        } else if (opcion == 2) {
            sistema.registrarProfesor();
            std::cout << "\nPresione Enter para volver al menú...";
            std::string pausa;
            std::getline(std::cin, pausa);
        } else if (opcion == 3) {
            sistema.registrarNotasAlumno();
            std::cout << "\nPresione Enter para volver al menú...";
            std::string pausa;
            std::getline(std::cin, pausa);
        } else if (opcion == 4) {
            sistema.deshacerUltimaNota();
            std::cout << "\nPresione Enter para volver al menú...";
            std::string pausa;
            std::getline(std::cin, pausa);
        } else if (opcion == 5) {
            sistema.generarColaCertificados();
            std::cout << "\nPresione Enter para volver al menú...";
            std::string pausa;
            std::getline(std::cin, pausa);
        } else if (opcion == 6) {
            sistema.mostrarReporteGeneral();
            std::cout << "\nPresione Enter para volver al menú...";
            std::string pausa;
            std::getline(std::cin, pausa);
        } else if (opcion == 7) {
            std::cout << "\n💾 Guardando cambios pendientes y cerrando la aplicación de forma segura...\n";
            sistema.guardarAlumnosDisco();
            break;
        } else {
            std::cout << "\n❌ Opción inválida. Por favor, seleccione un número entre 1 y 7.\n";
            std::cout << "\nPresione Enter para continuar...";
            std::string pausa;
            std::getline(std::cin, pausa);
        }
    }

    return 0;
}