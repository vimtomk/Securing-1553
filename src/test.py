# This is to test getting hex and putting into an array

from bitstring import BitArray
i = 0
str_array = ["Hello","World","1337"]
hex_array= []

for str in str_array:
    tmp = ""
    for char in str:
        tmp += (BitArray(uint=ord(char), length=8)).hex
    hex_array.append(tmp)

    print(tmp)

## TODO: Figure out how to get four hex characters into a single element
print("running hex_array loop")
for hex in hex_array:
    iter = 0
    while iter < len(hex):
        print(hex_array[iter], hex_array[iter+1])
        iter += 2


    

#print("0x{}{}".format(BitArray(uint=ord(str[i]), length=8)).hex, (BitArray(uint=ord(str[i+1]), length=8)).hex)
#i = i+2