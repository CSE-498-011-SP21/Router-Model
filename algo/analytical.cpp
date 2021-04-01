#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <utility> // std::pair
#include <stdexcept> // std::runtime_error
#include <sstream> // std::stringstream
#include <unordered_map>
#include <chrono>

using namespace std;


vector<unsigned int> read_stream(string filename)
{
	vector<unsigned int> retval;

	// Create an input filestream
	std::ifstream fd(filename);

	// Make sure the file is open
	if(!fd.is_open())
		throw std::runtime_error("Could not open file");

	string line;
	unsigned int val;
	while(getline(fd, line))
	{
		stringstream ss(line);
		while(ss >> val)
		{
			retval.push_back(val);

			// If the next token is a comma, ignore it
            if(ss.peek() == ',') ss.ignore();
		}
	}

	fd.close();

	return retval;
}


vector<pair<unsigned int, unsigned int>> read_freq(string filename)
{
	vector<pair<unsigned int, unsigned int>> retval;

	// Create an input filestream
	std::ifstream fd(filename);

	// Make sure the file is open
	if(!fd.is_open())
		throw std::runtime_error("Could not open file");

	string line;
	unsigned int key;
	unsigned int freq;
	while(getline(fd, line))
	{
		stringstream ss(line);

		// read each row and ignore commas
		ss >> key;
		if(ss.peek() == ',') ss.ignore();
		ss >> freq;
		if(ss.peek() == ',') ss.ignore();

		retval.push_back(make_pair(key, freq));
	}

	fd.close();

	return retval;
}


int main()
{
	size_t size = 1000;
	float* pred = new float[size];

	// load key stream and frequency data
	vector<unsigned int> stream = read_stream("stream.csv");
	vector<pair<unsigned int, unsigned int>> freqs = read_freq("frequency.csv");
	
	hash<unsigned int> hash_1;

	// train the model
	auto start = chrono::system_clock::now();
	for (unsigned int key : stream)
	{
		pred[hash_1(key) % size]++;
	}
	auto end = chrono::system_clock::now();
	chrono::duration<double> elapsed_seconds = end - start;

	cout << "Training duration (s): " << elapsed_seconds.count() << endl;

	// validate accuracy
	float total_error = 0;
	size_t count = 0;
	start = chrono::system_clock::now();
	for (auto freq : freqs)
	{
		total_error += abs(pred[hash_1(freq.first) % size] - freq.second) / freq.second;
		count++;
	}
	end = chrono::system_clock::now();
	elapsed_seconds = end - start;

	cout << "Validation duration (s): " << elapsed_seconds.count() << endl;

	cout << "Average error: " << total_error / count << endl;

	return 0;
}