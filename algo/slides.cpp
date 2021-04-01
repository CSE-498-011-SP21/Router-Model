// code included in Checkpoint 2 slides for demonstration purposes

#include <iostream>

using namespace std;

int main()
{
	short count = 0xFFFA;

	for (int i = 0; i < 10; i++)
	{
		// when incrementing, check if already max
		cout << count << ", " << !(count == (short)0xFFFF) << endl;
		count += !(count == (short)0xFFFF);
	}
}