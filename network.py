"""
File:    network.py
Author:  Daniel Finney
Date:    12/07/2023
Section: 31
E-mail:  dfinney1@umbc.edu
Description:
  Implemenet a simulation of a local switchboard to connect phones in the network.
"""

HYPHEN = "-"
QUIT = 'quit'
SWITCH_CONNECT = 'switch-connect'
SWITCH_ADD = 'switch-add'
PHONE_ADD = 'phone-add'
NETWORK_SAVE = 'network-save'
NETWORK_LOAD = 'network-load'
START_CALL = 'start-call'
END_CALL = 'end-call'
DISPLAY = 'display'

# class for switchboard
class Switchboard:
    
    # constructor method
    def __init__(self, area_code):
        self.area_code = area_code
        self.connected_switchboards = set()
        self.phone_numbers = []

    def add_connection(self, other_switchboard):
        self.connected_switchboards.add(other_switchboard)
        other_switchboard.connected_switchboards.add(self)

    def add_phone_number(self, phone_number):
        self.phone_numbers.append(phone_number)

    def disconnect(self, other_switchboard):
        if other_switchboard in self.connected_switchboards:
            self.connected_switchboards.remove(other_switchboard)
            other_switchboard.connected_switchboards.remove(self)

    def __repr__(self):
        return f"Switchboard(area_code={self.area_code})"

# class for phone number
class PhoneNumber:
    
    # constructor method
    def __init__(self, area_code, number):
        self.area_code = area_code
        self.number = number
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def __repr__(self):
        return f"PhoneNumber(area_code={self.area_code}, number={self.number}, connected={self.connected})"

# function connects two switchboards
def connect_switchboards(switchboards, area_1, area_2):
    switch_1 = switchboards.get(area_1)
    switch_2 = switchboards.get(area_2)

    if switch_1 and switch_2:
        switch_1.add_connection(switch_2)

# function adds a new switchboard
def add_switchboard(switchboards, area_code):
    if area_code not in switchboards:
        switchboards[area_code] = Switchboard(area_code)

# function adds a new phone number to a switchboard
def add_phone(switchboards, area_code, phone_number):
    switchboard = switchboards.get(area_code)
    if switchboard:
        switchboard.add_phone_number(PhoneNumber(area_code, phone_number))

# function saves the network information to a file
def save_network(switchboards, file_name):
    with open(file_name, 'w') as file:
        for area_code, switchboard in switchboards.items():
            file.write(f"SWITCHBOARD {area_code}\n")
            for connected_switchboard in switchboard.connected_switchboards:
                file.write(f"CONNECT {area_code} {connected_switchboard.area_code}\n")
            for phone_number in switchboard.phone_numbers:
                file.write(f"PHONE {phone_number.area_code}-{phone_number.number}\n")

# function to load network information from a file
def load_network(file_name):
    switchboards = {}
    current_switchboard = None

    with open(file_name, 'r') as file:
        lines = file.readlines()

        for line in lines:
            parts = line.strip().split()

            if parts[0] == 'SWITCHBOARD':
                area_code = int(parts[1])
                current_switchboard = Switchboard(area_code)
                switchboards[area_code] = current_switchboard
            elif parts[0] == 'CONNECT':
                area_1 = int(parts[1])
                area_2 = int(parts[2])
                switchboards[area_1].add_connection(switchboards[area_2])
            elif parts[0] == 'PHONE':
                number_parts = parts[1].split('-')
                area_code = int(number_parts[0])
                phone_number = int(''.join(number_parts[1:]))
                switchboards[area_code].add_phone_number(PhoneNumber(area_code, phone_number))

    return switchboards

# recursive function to find a path between two switchboards
# helper function for start_call function
def find_path(start_switchboard, end_switchboard, visited):
    # base case
    if start_switchboard == end_switchboard:
        return True

    visited.add(start_switchboard)
    
    # recursive call
    for switchboard in start_switchboard.connected_switchboards:
        if switchboard not in visited and find_path(switchboard, end_switchboard, visited):
            return True

    return False

# function initiates a call between two phone numbers if a path exists between their switchboards
def start_call(switchboards, start_area_code, start_src_number, end_area_code, end_src_number):
    start_switchboard = switchboards.get(start_area_code)
    end_switchboard = switchboards.get(end_area_code)

    if start_switchboard and end_switchboard:
        visited = set()
        if find_path(start_switchboard, end_switchboard, visited):
            # Connect the phone numbers
            for phone in start_switchboard.phone_numbers:
                if phone.area_code == start_area_code and phone.number == start_src_number:
                    for end_phone in end_switchboard.phone_numbers:
                        if end_phone.area_code == end_area_code and end_phone.number == end_src_number:
                            phone.connect()
                            end_phone.connect()
                            print(f"Connected {start_area_code}-{start_src_number} to {end_area_code}-{end_src_number}")
                            return  # Call connected successfully

        print("No path found between the given phone numbers.")

# function ends a call bewteen 2 phone numbers
def end_call(switchboards, start_area_code, start_src_number):
    switchboard = switchboards.get(start_area_code)
    if switchboard:
        for phone in switchboard.phone_numbers:
            if phone.area_code == start_area_code and phone.number == start_src_number:
                phone.disconnect()

# function displays the network information
def display(switchboards):
    for area_code, switchboard in switchboards.items():
        print(f"Switchboard with area code: {area_code}")
        print("\tTrunk lines are:")
        if switchboard.connected_switchboards:
            for connected_switchboard in switchboard.connected_switchboards:
                print(f"\t  Trunk line connection to: {connected_switchboard.area_code}")
        else:
            print("\t  No trunk line connections")

        print("\tLocal phone numbers are:")
        if switchboard.phone_numbers:
            for phone in switchboard.phone_numbers:
                if phone.connected:
                    connected_to = f"connected to {phone.area_code}-{phone.number}"
                else:
                    connected_to = "not in use"
                print(f"\t  Phone with number: {phone.area_code}-{phone.number} is {connected_to}")
        else:
            print("\t  No local phone numbers")


if __name__ == '__main__':
    switchboards = {}  # Dictionary to store switchboards
    s = input('Enter command: ')
    while s.strip().lower() != QUIT:
        split_command = s.split()
        if len(split_command) == 3 and split_command[0].lower() == SWITCH_CONNECT:
            area_1 = int(split_command[1])
            area_2 = int(split_command[2])
            connect_switchboards(switchboards, area_1, area_2)
        elif len(split_command) == 2 and split_command[0].lower() == SWITCH_ADD:
            add_switchboard(switchboards, int(split_command[1]))
        elif len(split_command) == 2 and split_command[0].lower() == PHONE_ADD:
            number_parts = split_command[1].split('-')
            area_code = int(number_parts[0])
            phone_number = int(''.join(number_parts[1:]))
            add_phone(switchboards, area_code, phone_number)
        elif len(split_command) == 2 and split_command[0].lower() == NETWORK_SAVE:
            save_network(switchboards, split_command[1])
            print('Network saved to {}.'.format(split_command[1]))
        elif len(split_command) == 2 and split_command[0].lower() == NETWORK_LOAD:
            switchboards = load_network(split_command[1])
            print('Network loaded from {}.'.format(split_command[1]))
        elif len(split_command) == 3 and split_command[0].lower() == START_CALL:
            src_number_parts = split_command[1].split(HYPHEN)
            src_area_code = int(src_number_parts[0])
            src_number = int(''.join(src_number_parts[1:]))

            dest_number_parts = split_command[2].split(HYPHEN)
            dest_area_code = int(dest_number_parts[0])
            dest_number = int(''.join(dest_number_parts[1:]))
            start_call(switchboards, src_area_code, src_number, dest_area_code, dest_number)

        elif len(split_command) == 2 and split_command[0].lower() == END_CALL:
            number_parts = split_command[1].split(HYPHEN)
            area_code = int(number_parts[0])
            number = int(''.join(number_parts[1:]))
            end_call(switchboards, area_code, number)

        elif split_command[0].lower() == DISPLAY:
            display(switchboards)

        s = input('Enter command: ')