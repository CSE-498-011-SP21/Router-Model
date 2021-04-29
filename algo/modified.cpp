#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <utility> // std::pair
#include <stdexcept> // std::runtime_error
#include <sstream> // std::stringstream
#include <unordered_map>
#include <chrono>
#include <array>
#include <random>
#include <algorithm>
#include <functional>

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


template<std::size_t N, typename T>
auto hashNT(const T& key) -> std::array<std::size_t, N>
{
	std::minstd_rand0 rng(std::hash<T>{}(key));
	std::array<std::size_t, N> hashes{};
	std::generate(std::begin(hashes), std::end(hashes), rng);
	return hashes;
}


int main()
{
	const size_t rows = 4;
	const size_t size = 500;
	short** counts = new short*[rows];
	for (size_t i = 0; i < rows; i++)
		counts[i] = new short*[size];

	// load key stream and frequency data
	vector<unsigned int> stream = read_stream("stream.csv");
	vector<pair<unsigned int, unsigned int>> freqs = read_freq("frequency.csv");

	// train the model
	auto start = chrono::system_clock::now();
	for (unsigned int key : stream)
	{
		// auto [h1, h2] = hashNT<2>(key);
		auto h = hashNT<4>(key);

		for (size_t i = 0; i < rows; i++)
			counts[i][h[i] % size]++;
	}
	auto end = chrono::system_clock::now();
	chrono::duration<double> elapsed_seconds = end - start;

	cout << "Training duration (s): " << elapsed_seconds.count() << endl;

	// validate accuracy
	float total_error = 0;
	size_t count = 0;
	int val;
	start = chrono::system_clock::now();
	for (auto freq : freqs)
	{
		// auto [h1, h2] = hashNT<2>(freq.first);
		auto h = hashNT<4>(freq.first);

		//TODO
		val = min({sketch_1[h1 % size], sketch_2[h2 % size],
					sketch_3[h3 % size], sketch_4[h4 % size]});

		total_error += abs((float)val - freq.second) / freq.second;
		count++;
	}
	end = chrono::system_clock::now();
	elapsed_seconds = end - start;

	cout << "Validation duration (s): " << elapsed_seconds.count() << endl;

	cout << "Average error: " << total_error / count << endl;

	total_error = 0;
	count = 0;
	start = chrono::system_clock::now();
	for (auto key : stream)
	{
		// auto [h1, h2] = hashNT<2>(freq.first);
		auto [h1, h2, h3, h4] = hashNT<4>(key);

		val = min({sketch_1[h1 % size], sketch_2[h2 % size],
					sketch_3[h3 % size], sketch_4[h4 % size]});

		total_error += abs((float)val - 5) / 5;
		count++;
	}
	end = chrono::system_clock::now();
	elapsed_seconds = end - start;

	cout << "Duration per million (s): " << elapsed_seconds.count() << endl;

	cout << total_error / count << endl;

	return 0;
}