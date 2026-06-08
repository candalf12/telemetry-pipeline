#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <unistd.h>
#include <librdkafka/rdkafkacpp.h>

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
    string errstr;
    string brokers = "kafka:29092";
    string topic_name = "system_metrics";

    RdKafka::Conf* conf = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);
    if (conf->set("bootstrap.servers", brokers, errstr) != RdKafka::Conf::CONF_OK) {
        cerr << "[HATA] Kafka ayarlari yapilamadi: " << errstr << endl;
        return 1;
    }

    // producer creation 
    RdKafka::Producer *producer = RdKafka::Producer::create(conf, errstr);
    
    if (!producer) {
        cerr << "Error while creating prucer " << errstr << endl;
        return 1;
    }
    
    cout << "Kafka has connected to broker (" << brokers << ")" << endl;
    // infinite loop for real-time monitoring
    while (true) {
        double ramUsage = getMemoryUsage();
        
        if (ramUsage >= 0.0) {
            //target data
            string payload = "{\"ram_usage_percent\": " + to_string(ramUsage) + "}";

            RdKafka::ErrorCode resp = producer->produce(
                topic_name,                          // target port 
                RdKafka::Topic::PARTITION_UA,   // partitioning
                RdKafka::Producer::RK_MSG_COPY, // copying the message
                const_cast<char *>(payload.c_str()), // data
                payload.size(),                 // data size
                NULL, 0,                        // Key 
                0,                              // time stamp
                NULL,                           // (Headers)
                NULL                            // (Opaque pointer)
            );

            // 3. Sonucu Kontrol Et
            if (resp != RdKafka::ERR_NO_ERROR) {
                cerr << "Unsuccesful" << RdKafka::err2str(resp) << endl;
            } else {
                cout << "Kafka has sent -> " << payload << endl;
            }

            // Kafka'nın kuyruktaki işlemleri tamamlaması için tetikleme
            producer->poll(0);
        }
        // sleep to avoid high cpu load
        sleep(2); 
    }
    delete producer;
    delete conf;
    return 0;
}