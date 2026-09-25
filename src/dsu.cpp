#ifndef DSU_HPP
#define DSU_HPP

#include <vector>
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include <algorithm>

/**
 * @brief Estructura de eventos para capturar el estado interno y pasos de cada operación.
 * Esto permite que la animación visual sea impulsada 100% por la ejecución real en C++.
 */
struct DSUEvent {
    std::string type;         // "INIT", "MAKE_SET", "FIND_VISIT", "FIND_COMPRESS", "UNION_QUERY", "UNION_LINK", "UNION_NOOP"
    int u = -1;
    int v = -1;
    int root_u = -1;
    int root_v = -1;
    int rank_u = -1;
    int rank_v = -1;
    std::string description;
    std::vector<int> current_parents;
    std::vector<int> current_ranks;
};

/**
 * @brief Implementación completa de Disjoint Set Union (DSU) / Union-Find.
 * Incluye Unión por Rango (Union by Rank) y Compresión de Caminos (Path Compression).
 */
class DisjointSetUnion {
private:
    int n;
    std::vector<int> parent;
    std::vector<int> rank;
    std::vector<int> set_size;
    std::vector<DSUEvent> event_log;

    void log_event(const std::string& type, int u, int v, int ru, int rv, const std::string& desc) {
        DSUEvent ev;
        ev.type = type;
        ev.u = u;
        ev.v = v;
        ev.root_u = ru;
        ev.root_v = rv;
        if (ru >= 0 && ru < n) ev.rank_u = rank[ru];
        if (rv >= 0 && rv < n) ev.rank_v = rank[rv];
        ev.description = desc;
        ev.current_parents = parent;
        ev.current_ranks = rank;
        event_log.push_back(ev);
    }

public:
    explicit DisjointSetUnion(int elements) : n(elements), parent(elements), rank(elements, 0), set_size(elements, 1) {
        for (int i = 0; i < n; ++i) {
            parent[i] = i; // Cada elemento empieza siendo su propio representante
        }
        log_event("INIT", -1, -1, -1, -1, "Inicialización de " + std::to_string(n) + " conjuntos disjuntos.");
    }

    /**
     * @brief Operación Find con Compresión de Caminos (Path Compression).
     * Amortiza el costo a O(alpha(N)).
     */
    int find(int x) {
        if (x < 0 || x >= n) return -1;

        std::vector<int> path;
        int curr = x;
        while (curr != parent[curr]) {
            path.push_back(curr);
            log_event("FIND_VISIT", curr, parent[curr], -1, -1, 
                      "Visitando nodo " + std::to_string(curr) + ", su padre actual es " + std::to_string(parent[curr]));
            curr = parent[curr];
        }
        int root = curr;
        log_event("FIND_ROOT", x, root, root, -1, 
                  "Raíz del conjunto encontrada: nodo " + std::to_string(root));

        // Compresión de caminos: conectar todos los nodos del camino directamente a la raíz
        for (int node : path) {
            if (parent[node] != root) {
                int old_p = parent[node];
                parent[node] = root;
                log_event("FIND_COMPRESS", node, root, root, -1,
                          "Compresión de camino: reconectando padre de " + std::to_string(node) + 
                          " de " + std::to_string(old_p) + " directamente a la raíz " + std::to_string(root));
            }
        }
        return root;
    }

    /**
     * @brief Operación Find estándar SIN compresión de caminos (útil para contrastar peor caso O(N)).
     */
    int find_without_compression(int x) {
        if (x < 0 || x >= n) return -1;
        int curr = x;
        while (curr != parent[curr]) {
            log_event("FIND_NAIVE_VISIT", curr, parent[curr], -1, -1,
                      "[Sin compresión] Visitando " + std::to_string(curr) + " -> " + std::to_string(parent[curr]));
            curr = parent[curr];
        }
        return curr;
    }

    /**
     * @brief Operación Union por Rango (Union by Rank).
     * @return true si se unieron dos conjuntos distintos, false si ya pertenecían al mismo conjunto (caso borde / ciclo).
     */
    bool unite(int x, int y) {
        log_event("UNION_QUERY", x, y, -1, -1, 
                  "Solicitud de unión entre elemento " + std::to_string(x) + " y " + std::to_string(y));

        int root_x = find(x);
        int root_y = find(y);

        if (root_x == root_y) {
            log_event("UNION_NOOP", x, y, root_x, root_y,
                      "Caso Borde: " + std::to_string(x) + " y " + std::to_string(y) + 
                      " ya pertenecen al mismo conjunto (raíz " + std::to_string(root_x) + "). No se modifica el grafo (previene ciclos).");
            return false;
        }

        // Unión por rango: el árbol de menor rango se cuelga bajo la raíz del árbol de mayor rango
        if (rank[root_x] < rank[root_y]) {
            parent[root_x] = root_y;
            set_size[root_y] += set_size[root_x];
            log_event("UNION_LINK", root_x, root_y, root_x, root_y,
                      "Unión por Rango: Rango(" + std::to_string(root_x) + ")=" + std::to_string(rank[root_x]) + 
                      " < Rango(" + std::to_string(root_y) + ")=" + std::to_string(rank[root_y]) + 
                      ". Se hace padre a " + std::to_string(root_y) + " sobre " + std::to_string(root_x));
        } else if (rank[root_x] > rank[root_y]) {
            parent[root_y] = root_x;
            set_size[root_x] += set_size[root_y];
            log_event("UNION_LINK", root_y, root_x, root_y, root_x,
                      "Unión por Rango: Rango(" + std::to_string(root_y) + ")=" + std::to_string(rank[root_y]) + 
                      " < Rango(" + std::to_string(root_x) + ")=" + std::to_string(rank[root_x]) + 
                      ". Se hace padre a " + std::to_string(root_x) + " sobre " + std::to_string(root_y));
        } else {
            // Rangos iguales: desempatar colgando root_y bajo root_x e incrementar rango de root_x
            parent[root_y] = root_x;
            set_size[root_x] += set_size[root_y];
            rank[root_x]++;
            log_event("UNION_LINK", root_y, root_x, root_y, root_x,
                      "Unión por Rango: Rangos iguales (" + std::to_string(rank[root_x] - 1) + 
                      "). Se cuelga " + std::to_string(root_y) + " bajo " + std::to_string(root_x) + 
                      " y se incrementa el rango de " + std::to_string(root_x) + " a " + std::to_string(rank[root_x]));
        }

        return true;
    }

    /**
     * @brief Conexión manual para demostrar peor caso (árbol degenerado tipo lista).
     */
    void link_manual(int child, int new_parent) {
        parent[child] = new_parent;
        log_event("MANUAL_LINK", child, new_parent, -1, -1, 
                  "Enlace directo " + std::to_string(child) + " -> " + std::to_string(new_parent));
    }

    const std::vector<DSUEvent>& get_events() const { return event_log; }
    void clear_events() { event_log.clear(); }

    /**
     * @brief Exporta el historial de eventos en formato JSON para que el script de Manim anime exactamente
     * cada paso ejecutado por la estructura de datos real en C++.
     */
    void export_json(const std::string& filepath) const {
        std::ofstream out(filepath);
        if (!out.is_open()) {
            std::cerr << "Error al abrir archivo para escribir JSON: " << filepath << std::endl;
            return;
        }

        out << "{\n";
        out << "  \"num_elements\": " << n << ",\n";
        out << "  \"events\": [\n";

        for (size_t i = 0; i < event_log.size(); ++i) {
            const auto& ev = event_log[i];
            out << "    {\n";
            out << "      \"step\": " << i << ",\n";
            out << "      \"type\": \"" << ev.type << "\",\n";
            out << "      \"u\": " << ev.u << ",\n";
            out << "      \"v\": " << ev.v << ",\n";
            out << "      \"root_u\": " << ev.root_u << ",\n";
            out << "      \"root_v\": " << ev.root_v << ",\n";
            out << "      \"rank_u\": " << ev.rank_u << ",\n";
            out << "      \"rank_v\": " << ev.rank_v << ",\n";
            out << "      \"description\": \"" << ev.description << "\",\n";
            
            out << "      \"parents\": [";
            for (size_t p = 0; p < ev.current_parents.size(); ++p) {
                out << ev.current_parents[p] << (p + 1 < ev.current_parents.size() ? ", " : "");
            }
            out << "],\n";

            out << "      \"ranks\": [";
            for (size_t r = 0; r < ev.current_ranks.size(); ++r) {
                out << ev.current_ranks[r] << (r + 1 < ev.current_ranks.size() ? ", " : "");
            }
            out << "]\n";

            out << "    }" << (i + 1 < event_log.size() ? "," : "") << "\n";
        }

        out << "  ]\n";
        out << "}\n";
        out.close();
        std::cout << "[DSU C++] Trace exportado exitosamente a: " << filepath << " (" << event_log.size() << " eventos)\n";
    }
};

#endif // DSU_HPP
