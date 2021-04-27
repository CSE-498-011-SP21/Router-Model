//
// Created by depaulsmiller on 1/15/21.
//

#include <unistd.h>
#include "helper.cuh"
#include <algorithm>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <dlfcn.h>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>

namespace pt = boost::property_tree;
using BatchWrapper = std::vector<RequestWrapper<unsigned long long, data_t *>>;
//#ifdef MODEL_CHANGE
using Model = kvgpu::AnalyticalModel<unsigned long long>;
//#else
//using Model = kvgpu::SimplModel<unsigned long long>;
//#endif
using RB = std::shared_ptr<Communication>;
using namespace std;
int RATIO_OF_READS = 95;
int totalBatches = 10000;
int BATCHSIZE = 512;
int KEY_SIZE = 8;
int NUM_THREADS = 4;//std::thread::hardware_concurrency() - 10;

void usage(char *command);
int count_workload(ifstream &inFile);
std::vector<BatchWrapper> getPopulationBatches(ifstream &inFile, unsigned seed, unsigned int nums);
std::vector<RequestWrapper<unsigned long long, data_t *>> generateWorkloadBatch(ifstream &inFile, unsigned *seed,int key_field ,int batchsize);
std::vector<RequestWrapper<unsigned long long, data_t *>> generatePopulation(ifstream &inFile, unsigned *seed,int key_field ,int batchsize);

struct ServerConf {
    int threads;
    int cpu_threads;

    int gpus;
    int streams;
    std::string modelFile;
    bool train;
    int size;
    int batchSize;
    bool cache;

    ServerConf() {
        batchSize = BATCHSIZE;
        modelFile = "";
        cpu_threads = NUM_THREADS;
        threads = 2;//1;//4;
        gpus = 1;
        streams = 10;//10;
        size = 1000000;
        train = false;
        cache = true;
    }

    explicit ServerConf(const std::string &filename) {
        pt::ptree root;
        pt::read_json(filename, root);
        cpu_threads = root.get<int>("cpu_threads", NUM_THREADS);
        threads = root.get<int>("threads", 4);
        streams = root.get<int>("streams", 2);
        gpus = root.get<int>("gpus", 2);
        modelFile = root.get<std::string>("modelFile", "");
        train = root.get<bool>("train", false);
        size = root.get<int>("size", 1000000);
        batchSize = root.get<int>("batchSize", BATCHSIZE);
        cache = root.get<bool>("cache", true);
    }

    void persist(const std::string &filename) const {
        pt::ptree root;
        root.put("threads", threads);
        root.put("streams", streams);
        root.put("gpus", gpus);
        root.put("modelFile", modelFile);
        root.put("train", train);
        root.put("size", size);
        root.put("batchSize", batchSize);
        root.put("cache", cache);
        pt::write_json(filename, root);
    }

    ~ServerConf() = default;

};

int main(int argc, char **argv) {

    ServerConf sconf;
    ifstream inFile("cluster001.csv", ios::in);

    int workload_count = count_workload(inFile);
    inFile.close();

    inFile.open("cluster001.csv");
    float ratio_train = 0.01f, 
           ratio_population = 0.3f;


    std::vector<PartitionedSlabUnifiedConfig> conf;
    for (int i = 0; i < sconf.gpus; i++) {
        for (int j = 0; j < sconf.streams; j++) {
            gpuErrchk(cudaSetDevice(i));
            cudaStream_t stream = cudaStreamDefault;
            if (j != 0) {
                gpuErrchk(cudaStreamCreate(&stream));
            }
            conf.push_back({sconf.size, i, stream});
        }
    }


    std::unique_ptr<KVStoreCtx<Model>> ctx = nullptr;
    unsigned tseed = time(nullptr);
    std::vector<std::pair<unsigned long long, unsigned>> trainVec;
    std::hash<unsigned long long> hfn{};

    int current_workload = workload_count * ratio_train;
    workload_count -= current_workload;
    // for (int i = 0; i < 50; i++) {
    //     BatchWrapper b = generatePopulation(inFile,&tseed, 1, );
    //     for (auto &elm : b) {
    //         trainVec.push_back({elm.key, hfn(elm.key)});
    //     }
        
    // }

   
    while (current_workload > 0){
        BatchWrapper b = generatePopulation(inFile,&tseed, 1,current_workload >= sconf.batchSize ? sconf.batchSize : current_workload);
        for (auto &elm : b) {
            trainVec.push_back({elm.key, hfn(elm.key)});
        }
        current_workload -= sconf.batchSize;
    }
    

        Model m;
        m.train(trainVec);
    //     m.persist("./temp.json");
        ctx = std::make_unique<KVStoreCtx<Model>>(conf, sconf.cpu_threads, m);
    // }

    GeneralClient<Model> *client = nullptr;
    if (sconf.cache) {
        if (sconf.gpus == 0) {
            client = new JustCacheKVStoreClient<Model>(*ctx);
        } else {
            client = new KVStoreClient<Model>(*ctx);
        }
    } else {
        client = new NoCacheKVStoreClient<Model>(*ctx);
    }
    
    init_loadbalance(sconf.cpu_threads);
    std::vector<BatchWrapper> work;
    std::vector<BatchWrapper> population;

    current_workload = workload_count * ratio_population;
    workload_count -= current_workload;

    while (current_workload > 0){
        population.push_back(generatePopulation(inFile, &tseed, 1, current_workload >= sconf.batchSize ? sconf.batchSize : current_workload));
        current_workload -= sconf.batchSize;
        cout << current_workload << endl;
    }
    // for(int i = 0; i < 1000; i++)
    //     population.push_back(generatePopulation(inFile, &tseed, 1, 512));


    for(auto i : population)
    {
        auto rb = std::make_shared<LocalCommunication>(i.size());
        auto start = std::chrono::high_resolution_clock::now();
        client->batch(i, rb, start);
    }

    while (workload_count > 0){
        work.push_back(generatePopulation(inFile, &tseed, 1, workload_count >= sconf.batchSize ? sconf.batchSize : workload_count));
        workload_count -= sconf.batchSize;
    }

  
    // for(int i = 0; i < 1000; i++)
    //     work.push_back(generateWorkloadBatch(inFile, &tseed, 1, 512));

    auto startTime = std::chrono::high_resolution_clock::now();

    std::cout << "before test" << std::endl;

    for(auto i : work)
    {
        auto rb = std::make_shared<LocalCommunication>(i.size());
        auto start = std::chrono::high_resolution_clock::now();
        client->batch(i, rb, start);
    }


    
    auto endTimeArrival = std::chrono::high_resolution_clock::now();

    auto endTime = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> dur = endTime - startTime;
    std::chrono::duration<double> durArr = endTimeArrival - startTime;
    size_t ops = client->getOps();
    // std::cerr << "Throughput (ops) " << ((double) ops)  << std::endl;

    std::cerr << "Hits rate: " << client->hitRate() << std::endl;
    // client->stat();
    delete client;
    // generateWorkloadBatch(inFile, &tseed, 1, 10);
    // generateWorkloadBatch(inFile, &tseed, 1, 10);
    inFile.close();
    return 0;
}

void usage(char *command) {
    using namespace std;
    cout << command << " [-f <config file>]" << std::endl;
}

int count_workload(ifstream &inFile){
    int counter = 0;
    string line;
    while (getline(inFile,line)){ 
        counter++;
    }

    return counter;
}
std::vector<RequestWrapper<unsigned long long, data_t *>> generateWorkloadBatch(ifstream &inFile, unsigned *seed,int key_field ,int batchsize) {
    std::vector<RequestWrapper<unsigned long long, data_t *>> vec;
    
    int counter = 0;
    string line;
    while (getline(inFile,line) && counter < batchsize){ 
        string field;
        string substr;
        istringstream readstr(line);

        unsigned long long l = 0;
        unsigned int type = REQUEST_GET;

        for(int j = 0;j < key_field+1;j++){ 
            getline(readstr,field,','); 
            if (j == key_field) {
            	// substr = string {field.c_str(), field.c_str().length()-8,field.c_str().length()};
                substr = field.substr(field.length()-8,field.length());
            	 for (int i = 0; i < 8; ++i) {
    			    l = l | ((unsigned long long)substr[i] << (8 * i));
  		        }
                //   cout << l << endl;

                if (rand_r(seed) % 100 < RATIO_OF_READS) {
                    type = REQUEST_GET;
                    vec.push_back({l, 0, nullptr, type});
                }
                else 
                    if (rand_r(seed) % 100 < 50) {
                        type = REQUEST_INSERT;
                        vec.push_back({l, 0,new data_t(KEY_SIZE), type});
                    } else {
                        type = REQUEST_REMOVE;
                        vec.push_back({l, 0, nullptr, type});
                    }
        
            }
        }

        counter++;

    }

    return vec;
    
}

std::vector<RequestWrapper<unsigned long long, data_t *>> generatePopulation(ifstream &inFile, unsigned *seed,int key_field ,int batchsize) {
    std::vector<RequestWrapper<unsigned long long, data_t *>> vec;
    
    int counter = 0;
    string line;
    while (getline(inFile,line) && counter < batchsize){ 
        string field;
        string substr;
        istringstream readstr(line);

        unsigned long long l = 0;
        unsigned int type = REQUEST_GET;

        for(int j = 0;j < key_field+1;j++){ 
            getline(readstr,field,','); 
            if (j == key_field) {
            	// substr = string {field.c_str(), field.c_str().length()-8,field.c_str().length()};
                substr = field.substr(field.length()-8,field.length());
            	 for (int i = 0; i < 8; ++i) {
    			    l = l | ((unsigned long long)substr[i] << (8 * i));
  		        }
                //   cout << l << endl;



            type = REQUEST_INSERT;
            vec.push_back({l, 0,new data_t(KEY_SIZE), type});

                       
                    
        
            }
        }

        counter++;

    }

    return vec;
    
}

std::vector<BatchWrapper> getPopulationBatches(ifstream &inFile, unsigned int *seed,int key_field ,unsigned int nums) {
    std::vector<BatchWrapper> batches;
    for(int i=0; i< nums; i++){
        std::vector<RequestWrapper<unsigned long long, data_t *>> vec;
        int counter = 0;
        string line;
        string field;
        while (getline(inFile,line) && counter < nums){ 
            string number;
            string substr;
            istringstream readstr(line);
    
            unsigned long long l = 0;
    
            for(int j = 0;j < key_field+1;j++){ 
                getline(readstr,number,','); 
                if (j == key_field) {
                    substr = string {number.c_str(), 0,8};
                     for (int i = 0; i < 8; ++i) {
                        l = l | ((unsigned long long)substr[i] << (8 * i));
                      }
    
                    
                    vec.push_back({l, 0,new data_t(KEY_SIZE), REQUEST_INSERT});
            
                }
                cout << l << endl;
            }
    
            counter++;
    
        }
        batches.push_back(vec);
    }

    return batches;
   
}
