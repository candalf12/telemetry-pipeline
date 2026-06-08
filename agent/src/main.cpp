#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <unistd.h>

using namespace std;

// read ram usage from /proc/meminfo from the server
double getMemoryUsage() {
    ifstream meminfo("/proc/meminfo");
    string line;
    long totalMem = 0;
    long freeMem = 0;
    long buffers = 0;
    long cached = 0;

    if (meminfo.is_open()) {
        while (getline(meminfo, line)) {
            istringstream iss(line);
            string key;
            long value;
            string unit;

            iss >> key >> value >> unit;

            if (key == "MemTotal:") {
                totalMem = value;
            }
            else if (key == "MemFree:") {
                freeMem = value;
            }
            else if (key == "Buffers:") {
                buffers = value;
            }
            else if (key == "Cached:") {
                cached = value;
            }
        }
        meminfo.close();
    } 
    else {
        cerr << "Error: /proc/meminfo cannot be opened!" << endl;
        return -1.0;
    }

    // calculate actual memory usage
    long actuallyUsedMem = totalMem - (freeMem + buffers + cached);
    double usagePercent = (static_cast<double>(actuallyUsedMem) / totalMem) * 100.0;

    return usagePercent;
}

int main() {
    cout << "SRE Telemetry Agent Started..." << endl;

    // infinite loop for real-time monitoring
    while (true) {
        double ramUsage = getMemoryUsage();
        
        if (ramUsage >= 0.0) {
            cout << " RAM Usage: %" << ramUsage << endl;
        }
        // sleep to avoid high cpu load
        sleep(2); 
    }

    return 0;
}