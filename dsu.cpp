#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>

using namespace std;

class DSU {
private:
    vector<int> parent;
    vector<int> size;
    vector<string> log;

    static string arrToJson(const vector<int>& v) {
        ostringstream ss;
        ss << "[";

        for (size_t i = 0; i < v.size(); i++) {
            ss << v[i];

            if (i + 1 < v.size())
                ss << ",";
        }

        ss << "]";
        return ss.str();
    }

public:
    void makeSet(int n) {
        parent.resize(n);
        size.assign(n, 1);

        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }

        ostringstream ss;
        ss << "{\"op\":\"init\",\"n\":" << n
           << ",\"parent_after\":" << arrToJson(parent) << "}";

        log.push_back(ss.str());
    }

    int find(int x) {
        vector<int> path;

        int root = x;

        while (parent[root] != root) {
            path.push_back(root);
            root = parent[root];
        }

        path.push_back(root);

        vector<int> before = parent;

        for (int node : path)
            parent[node] = root;

        ostringstream ss;

        ss << "{\"op\":\"find\",\"x\":" << x
           << ",\"path\":" << arrToJson(path)
           << ",\"root\":" << root  
           << ",\"parent_before\":" << arrToJson(before)
           << ",\"parent_after\":" << arrToJson(parent) << "}";

        log.push_back(ss.str());

        return root;
    }

    void unite(int a, int b) {
        int ra = find(a);
        int rb = find(b);

        if (ra == rb)
            return;

        vector<int> before = parent;

        if (size[ra] < size[rb]) {
            int temp = ra;
            ra = rb;
            rb = temp;
        }

        parent[rb] = ra;
        size[ra] += size[rb];

        ostringstream ss;

        ss << "{\"op\":\"union\",\"a\":" << a
           << ",\"b\":" << b
           << ",\"attached\":" << rb
           << ",\"new_root\":" << ra
           << ",\"parent_before\":" << arrToJson(before)
           << ",\"parent_after\":" << arrToJson(parent) << "}";

        log.push_back(ss.str());
    }

    bool connected(int a, int b) {
        return find(a) == find(b);
    }

    int getSize(int x) {
        return size[find(x)];
    }

    int numSets() {
        int count = 0;

        for (int i = 0; i < (int)parent.size(); i++) {
            if (find(i) == i)
                count++;
        }

        return count;
    }

    void debugForceParent(int x, int p) {
        parent[x] = p;
    }

    void dumpLog(const string& filename) {
        ofstream out(filename);

        out << "{\n  \"events\": [\n";

        for (size_t i = 0; i < log.size(); i++) {
            out << "    " << log[i];

            if (i + 1 < log.size())
                out << ",";

            out << "\n";
        }

        out << "  ]\n}\n";
    }
};

int main() {

    {
        DSU dsu;
        dsu.makeSet(5);

        dsu.unite(0, 1);
        dsu.unite(1, 2);
        dsu.unite(3, 4);
        dsu.unite(0, 4);

        cout << "connected(0,2): "
             << dsu.connected(0, 2) << '\n';

        cout << "connected(0,3): "
             << dsu.connected(0, 3) << '\n';

        cout << "tamano del conjunto de 0: "
             << dsu.getSize(0) << '\n';

        cout << "numero de conjuntos: "
             << dsu.numSets() << '\n';

        dsu.dumpLog("logs/dsu_log_main.json");
    }

    {
        DSU dsu;
        dsu.makeSet(1);

        dsu.find(0);

        dsu.dumpLog("logs/dsu_log_single.json");
    }

    {
        DSU dsu;
        dsu.makeSet(7);

        for (int i = 1; i < 7; i++)
            dsu.debugForceParent(i, i - 1);

        dsu.find(6);

        dsu.dumpLog("logs/dsu_log_worstcase.json");
    }


    return 0;
}