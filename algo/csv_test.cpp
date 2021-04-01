#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <utility> // std::pair
#include <stdexcept> // std::runtime_error
#include <sstream> // std::stringstream

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
	vector<unsigned int> stream = read_stream("stream.csv");

	cout << "Stream Length: " << stream.size() << endl;

	cout << "Values:" << endl;
	for (int i = 0; i < 10; i++)
	{
		cout << stream.at(i) << endl;
	}

	cout << "======================" << endl;

	vector<pair<unsigned int, unsigned int>> freqs = read_freq("frequency.csv");

	cout << "Unique Keys: " << freqs.size() << endl;

	cout << "Frequencies:" << endl;
	for (int i = 0; i < 10; i++)
	{
		cout << freqs.at(i).first << ", " << freqs.at(i).second << endl;
	}

	return 0;
}