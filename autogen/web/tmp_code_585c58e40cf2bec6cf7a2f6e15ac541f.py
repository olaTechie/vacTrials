# Open a file for writing
with open('numbers.txt', 'w') as f:
    # Write the numbers 1 to 100 to the file
    for i in range(1, 101):
        f.write(str(i) + '\n')