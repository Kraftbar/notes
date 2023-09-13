#include <stdio.h>

// Function to increment an integer using a pointer
void increment(int *num) {
    (*num)++; // Increment the value pointed to by 'num'
}

int main() {
    int value1 = 5;
    int value2 = 10;

    int *addr1 = &value1; // Explicitly assign the address of 'value1' to 'addr1'

    printf("Before increment: value1 = %d, value2 = %d\n", *addr1, value2);

    // Call the increment function to increment 'value1' and 'value2'
    increment(addr1); // Pass 'addr1' to the increment function for 'value1'
    increment(&value2); // Pass the address of 'value2' directly to the increment function

    printf("After increment: value1 = %d, value2 = %d\n", *addr1, value2);

    return 0;
}
