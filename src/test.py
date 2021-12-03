from message import message as msg

#Message will contain 20 characters
mesg = 0b11110001010001100010

#Instance of message type
m1   = msg(mesg)

#Prints message type bits in binary as Type: String
print(m1.return_message_type_bin())

#Prints the message types bits as string Type: String
m1.print_message_type_str()

#Prints the message data in binary as Type: string
m1.print_raw_data_bits()

#Prints message parity bit as Type: string
m1.print_parity_bit()