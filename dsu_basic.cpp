#include <iostream>
#include <vector>
using namespace std;

class DSU {
private:
    vector<int> parent;

public:
    void makeSet(int n) {
        parent.resize(n);

        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
    }

    int find(int x) {
        if (parent[x] == x)
            return x;

        return find(parent[x]);
    }

    void unite(int a, int b) {
        a = find(a);
        b = find(b);

        if (a == b)
            return;

        parent[b] = a;
    }

    bool connected(int a, int b) {
        return find(a) == find(b);
    }
 

};


int main(){
    DSU dsu;
    dsu.makeSet(5);
    dsu.unite(0, 1);
    dsu.unite(1, 2);
    dsu.unite(3, 4);
    dsu.unite(0, 4);
    cout << dsu.connected(0, 2) << '\n';
    cout << dsu.connected(0, 3) << '\n';    
};