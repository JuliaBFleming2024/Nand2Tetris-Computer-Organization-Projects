# -*- coding: utf-8 -*-
"""Assembler for the Hack processor.

Author: Naga Kandasamy
Date created: August 8, 2020
Date modified: April 25, 2022

Student name(s): Julia Fleming
Date modified: 2023-08-11
"""

import os
import sys
import enum
from multiprocessing.sharedctypes import Value

"""The comp field is a c1 c2 c3 c4 c5 c6"""
valid_comp_patterns = {'0':'0101010',
                       '1':'0111111',
                       '-1':'0111010',
                       'D':'0001100',
                       'A':'0110000',
                       '!D':'0001101',
                       '!A':'0110001',
                       '-D':'0001111',
                       '-A':'0110011',
                       'D+1':'0011111',
                       'A+1':'0110111',
                       'D-1':'0001110',
                       'A-1':'0110010',
                       'D+A':'0000010',
                       'D-A':'0010011',
                       'A-D':'0000111',
                       'D&A':'0000000',
                       'D|A':'0010101',
                       'M':'1110000',
                       '!M':'1110001',
                       '-M':'1110011',
                       'M+1':'1110111',
                       'M-1':'1110010',
                       'D+M':'1000010',
                       'M+D':'1000010',
                       'D-M':'1010011',
                       'M-D':'1000111',
                       'D&M':'1000000',
                       'D|M':'1010101'
                       }

"""The dest bits are d1 d2 d3"""
valid_dest_patterns = {'null':'000',
                       'M':'001',
                       'D':'010',
                       'MD':'011',
                       'A':'100',
                       'AM':'101',
                       'AD':'110',
                       'AMD':'111'
                       }

"""The jump fields are j1 j2 j3"""
valid_jmp_patterns =  {'null':'000',
                       'JGT':'001',
                       'JEQ':'010',
                       'JGE':'011',
                       'JLT':'100',
                       'JNE':'101',
                       'JLE':'110',
                       'JMP':'111'
                       }

"""Symbol table populated with predefined symbols and RAM locations"""
symbol_table = {'SP':0,
                'LCL':1,
                'ARG':2,
                'THIS':3,
                'THAT':4,
                'R0':0,
                'R1':1,
                'R2':2,
                'R3':3,
                'R4':4,
                'R5':5,
                'R6':6,
                'R7':7,
                'R8':8,
                'R9':9,
                'R10':10,
                'R11':11,
                'R12':12,
                'R13':13,
                'R14':14,
                'R15':15,
                'SCREEN':16384,
                'KBD':24576
                }

newMemAddr = 16
def print_intermediate_representation(ir):
    """Print intermediate representation"""
    
    for i in ir:
        print()
        for key, value in i.items():
            print(key, ':', value)

        
def print_instruction_fields(s):
    """Print fields in instruction"""
    
    print()
    for key, value in s.items():
        print(key, ':', value)


def valid_tokens(s):
    """Return True if tokens belong to valid instruction-field patterns"""
    if s['instruction_type'] == 'PSEUDO_INSTRUCTION':
        """Return status = -1 if first character of the instruction is a number"""
        if s['value'][0].isnumeric():
            return -1
    elif s['instruction_type'] == 'C_INSTRUCTION':
        """Return status = -1 if any of the field is invalid"""
        if (s['dest'] not in valid_dest_patterns) or (s['comp'] not in valid_comp_patterns) or (s['jmp'] not in valid_jmp_patterns):
            return -1

    return 0


def parse(command):
    """Implements finite automate to scan assembly statements and parse them.

    WHITE SPACE: Space characters are ignored. Empty lines are ignored.
    
    COMMENT: Text beginning with two slashes (//) and ending at the end of the line is considered
    comment and is ignored.
    
    CONSTANTS: Must be non-negative and are written in decimal notation.
    
    SYMBOL: A user-defined symbol can be any sequence of letters, digits, underscore (_), dot (.),
    dollar sign ($), and colon (:) that does not begin with a digit.
    
    LABEL: (SYMBOL)
    """
    
    # Data structure to hold the parsed fields for the command
    s = {}
    s['instruction_type'] = ''
    s['value'] = ''
    s['value_type'] = ''
    s['dest'] = ''
    s['comp'] = ''
    s['jmp'] = ''
    s['status'] = 0
      
    
    # Valid operands and operations for C-type instructions
    valid_operands = '01DMA'
    valid_operations = '+-&|'
    
    
    # Implement your finite automata to extract tokens from command
    command = command.strip()
    if command == '':
        return {}
    elif command[0] == '/':
        return {}
    else:
        command.replace(' ', '')
        for i, ch in enumerate(command):
            if ch == '/':
                command = command[0:i]
    if command[0] == '@':
        s['instruction_type'] = 'A_INSTRUCTION'
        s['value'] = command[1::]
        s['value_type'] = 'NUMERIC' if s['value'].isnumeric() else 'SYMBOL'
    elif command[0] ==  '(' and command[-1] == ')':
        s['instruction_type'] = 'PSEUDO_INSTRUCTION'
        s['value'] = command[1:-1]
    else:
        if '=' not in command:
            command = 'null=' + command
        if ';' not in command:
            command += ';null'
        command = command.replace(' ','')
        temp = command.split('=')
        s['instruction_type'] = 'C_INSTRUCTION'
        s['dest'] = temp[0]
        temp = temp[1].split(';')
        s['comp'] = temp[0]
        s['jmp'] = temp[1]
          
    # check if the tokens were formed correctly
    s['status'] = valid_tokens(s)

    return s
   
def generate_machine_code(ir):
    """Generate machine code from intermediate data structure"""
    
    machine_code = []
    instruction = ''
    for s in ir:
        if s['instruction_type'] == 'A_INSTRUCTION':
            instruction = '0'
            if s['value_type'] == 'NUMERIC':
                instruction = bin(int(s['value']))[2:].zfill(16)
            else:
                var_address = symbol_table[s['value']]
                instruction += format(var_address, 'b').zfill(15)
            machine_code.append(instruction)
        elif s['instruction_type'] == 'C_INSTRUCTION':
            instruction = '111' + valid_comp_patterns[s['comp']] + valid_dest_patterns[s['dest']] + valid_jmp_patterns[s['jmp']]
            machine_code.append(instruction)
        else:
            continue

    return machine_code
    

def print_machine_code(machine_code):
    
    rom_address = 0
    for code in machine_code:
        print(rom_address, ':', code)
        rom_address = rom_address + 1


def run_assembler(file_name):
    global newMemAddr
    
    # Implement Pass 1 of the assembler to generate the intermediate data structure
    ir = []
    with open(file_name, 'r') as f:
        linecount = 0
        for command in f:
            s = parse(command)
            if s != {}:
            
                linecount +=1
                # print_instruction_fields(s)
                if s['status'] == -1:
                    return
                ir.append(s)
                if (s['instruction_type'] == 'PSEUDO_INSTRUCTION') and (s['value'] not in  symbol_table):
                    linecount -=  1
                    symbol_table[s['value']] =  linecount
        for s in ir:
            if (s['instruction_type'] == 'A_INSTRUCTION' and  s['value_type'] == 'SYMBOL') and (s['value'] not in symbol_table):
                symbol_table[s['value']] = newMemAddr
                newMemAddr += 1
        print_intermediate_representation(ir)
        f.close()
    # print(symbol_table)
    # Implement Pass 2 of assembler to generate the machine code from the intermediate data structure
    machine_code = generate_machine_code(ir)
    print_machine_code(machine_code)

    
    return machine_code
    
  
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Python assembler.py file-name.asm")
        print("Example: Python assembler.py mult.asm")
    else:
        print("Assembling file:", sys.argv[1])
        print()
        file_name_minus_extension, _ = os.path.splitext(sys.argv[1])
        output_file = file_name_minus_extension + '.hack'
        machine_code = run_assembler(sys.argv[1])
        if machine_code:
            print('Machine code generated successfully');
            print('Writing output to file:', output_file)
            f = open(output_file, 'w')
            for s in machine_code:
                f.write('%s\n' %s)
            f.close()
        else:
            print('Error generating machine code')
            
        

    
    
    
    
