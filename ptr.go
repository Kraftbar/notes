package main

import "fmt"

// Function to increment an integer using a pointer
func increment(num *int) {
	*num++ // Increment the value pointed to by 'num'
}

func main() {
	value1 := 5
	value2 := 10

	addr1 := &value1 // Get the address of 'value1'

	fmt.Printf("Before increment: value1 = %d, value2 = %d\n", *addr1, value2)

	// Call the increment function to increment 'value1' and 'value2'
	increment(addr1) // Pass 'addr1' to the increment function for 'value1'
	increment(&value2) // Pass the address of 'value2' directly to the increment function

	fmt.Printf("After increment: value1 = %d, value2 = %d\n", *addr1, value2)
}
