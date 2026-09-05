#include <iostream>

// Function to increment an integer using a pointer
void increment(int &num) {
    num++; // Increment the value directly
}

int main() {
    int value1 = 5;
    int value2 = 10;

    int &ref1 = value1; // Create a reference to 'value1'
    
    std::cout << "Before increment: value1 = " << ref1 << ", value2 = " << value2 << std::endl;

    // Call the increment function to increment 'value1' and 'value2'
    increment(ref1); // Pass the reference to 'value1' to the increment function
    increment(value2); // Pass 'value2' directly to the increment function

    std::cout << "After increment: value1 = " << ref1 << ", value2 = " << value2 << std::endl;

    return 0;
}
