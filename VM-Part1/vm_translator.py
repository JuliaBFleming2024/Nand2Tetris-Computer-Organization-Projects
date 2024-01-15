# -*- coding: utf-8 -*-
"""
Compiler back end for the Hack processor.
Translates from a stack-based language for the virtual machine to the Hack assembly 

Author: Naga Kandasamy
Date created: September 1, 2020
Date modified: May 12, 2022

Student name(s): Julia Fleming
Date modified: 08/25/2023
"""
import os
import sys
address_map = {'local':'@LCL', 'argument':'@ARG', 'this':'@THIS', 'that':'@THAT', 'pointer':3, 'temp':5, 'static':1024}
arithmetic_logic_map = {'add':'+','sub':'-','and':'&','or':'|','not':'!','neg':'-'}

def generate_exit_code():
    """Generate some epilogue code that places the program, upon completion, into 
    an infinite loop. 
    """
    s = []
    s.append('(THATS_ALL_FOLKS)')
    s.append('@THATS_ALL_FOLKS')
    s.append('0;JMP')
    return s


def generate_push_code(segment, index):
    """Generate assembly code to push value into the stack.
    In the case of a variab/Users/juliafleming/Documents/ECE350/VM-Part2/vm_translator_v2.pyle, it is read from the specified memory segment using (base + index) 
    addressing.
    """
    s = [] 
    if segment == 'constant':
        # FIXME: complete the implementation 
        s.append('@{}'.format(index))
        s.append('D=A')
    else:
        if segment in ('local', 'argument', 'this', 'that'):

            s.append(address_map.get(segment))
            s.append('D=M')
            s.append('@{}'.format(index))
            s.append('A=D+A')        
            s.append('D=M')     /Users/juliafleming/Documents/ECE350/VM-Part2/vm_translator_v2.py
        elif segment in ('temp','pointer'):
            s.append('@R{}'.format(address_map.get(segment) + int(index)))
            s.append('D=M')
        elif segment == 'static':
            s.append('@{}'.format(address_map.get(segment) + int(index)))
            s.append('D=M')
    s.append('@SP')
    s.append('A=M')
    s.append('M=D')
    s.append('@SP')
    s.append('M=M+1')
    return s
    

def generate_pop_code(segment, index):
    """Generate assembly code to pop value from the stack.
    The popped value is stored in the specified memory segment using (base + index) 
    addressing.
    """
    s = []
    if segment in ('local', 'argument', 'this', 'that'):
        s.append(address_map.get(segment))
        s.append('D=M')
        s.append('@{}'.format(index))
        s.append('D=D+A')
    elif segment in ('temp','pointer'):
        s.append('@R{}'.format(address_map.get(segment) + int(index)))
        s.append('D=A')
    elif segment == 'static':
        s.append('@{}'.format(address_map.get(segment) + int(index)))
        s.append('D=A')
    else:
        print('Invalid pop, segment: {}'.format(segment))
    s.append('@R13')
    s.append('M=D')
    s.append('@SP')
    s.append('M=M-1')
    s.append('A=M')
    s.append('D=M')
    s.append('@R13')
    s.append('A=M')
    s.append('M=D')
    return s


def generate_arithmetic_or_logic_code(operation):
    s = []

    if operation in ('add','sub','and','or'):
        # FIXME: complete implementation for + , - , | , and & operators
        s.append('@SP')
        s.append('M=M-1')
        s.append('A=M')
        s.append('D=M')
        s.append('@SP')
        s.append('M=M-1')
        s.append('A=M')
        s.append('D=M{}D'.format(arithmetic_logic_map.get(operation)))
        s.append('@SP')
        s.append('A=M')
        s.append('M=D')
        s.append('@SP')
        s.append('M=M+1')
                 
    return s


def generate_unary_operation_code(operation):
    """Generate assembly code to perform the specified unary operation. 
    The operand is popped from the stack and the result of the operation 
    placed back in the stack.
    """
    s = []
    s.append('@SP')
    s.append('M=M-1')
    s.append('A=M')
    s.append('D=M')
    s.append('@SP')
    s.append('A=M')
    s.append('M={}D'.format(arithmetic_logic_map.get(operation)))
    s.append('@SP')
    s.append('M=M+1')

    return s


def generate_relation_code(operation, line_number):
    """Generate assembly code to perform the specified relational operation. 
    The two operands are popped from the stack and the result of the operation 
    placed back in the stack.
    """
    s = []
    label_1 = ''
    label_2 = ''
    s.append('@SP')
    s.append('M=M-1')
    s.append('A=M')
    s.append('D=M')            
    s.append('@SP')
    s.append('M=M-1') 
    s.append('A=M')
    if operation == 'lt':
        s.append('D=M-D')   
        label_1 = 'IF_LT_' + str(line_number)
        s.append('@' + label_1)
        s.append('D;JLT') 
        s.append('@SP')
        s.append('A=M')
        s.append('M=0') 
        label_2 = 'END_IF_ELSE_' + str(line_number)
        s.append('@' + label_2)
        s.append('0;JMP')
        s.append('(' + label_1 + ')')
        s.append('@SP')
        s.append('A=M')
        s.append('M=-1')  
        s.append('(' + label_2 + ')')
    elif operation == 'eq':
        s.append('D=M-D')  
        label_1 = 'IF_EQ_' + str(line_number)
        s.append('@' + label_1)
        s.append('D;JEQ')  
        s.append('@SP')
        s.append('A=M')
        s.append('M=0') 
        label_2 = 'END_IF_ELSE_' + str(line_number)
        s.append('@' + label_2)
        s.append('0;JMP')
        s.append('(' + label_1 + ')')
        s.append('@SP')
        s.append('A=M')
        s.append('M=-1') 
        s.append('(' + label_2 + ')')
    elif operation == 'gt':
        s.append('D=M-D') 
        label_1 = 'IF_GT_' + str(line_number)
        s.append('@' + label_1)
        s.append('D;JGT')
        s.append('@SP')
        s.append('A=M')
        s.append('M=0') 
        label_2 = 'END_IF_ELSE_' + str(line_number)
        s.append('@' + label_2)
        s.append('0;JMP')
        s.append('(' + label_1 + ')')
        s.append('@SP')
        s.append('A=M')
        s.append('M=-1')  
        s.append('(' + label_2 + ')')     
    s.append('@SP')
    s.append('M=M+1')
    return s
  
def generate_set_code(register, value):
    """Generate assembly code for set"""
    s = []
    s.append('@' + value)
    s.append('D=A')
    if register == 'sp':
        s.append('@SP')
    if register == 'local':
        s.append('@LCL')
    if register == 'argument':
        s.append('@ARG')
    if register == 'this':
        s.append('@THIS')
    if register == 'that':
        s.append('@THAT')        
    s.append('M=D')
    return s


def translate(tokens, line_number):
    """Translate a VM command/statement into the corresponding Hack assembly commands/statements."""
    s = []
    
    if tokens[0] == 'push':
        s = generate_push_code(tokens[1], tokens[2])    # Generate code to push into stack
        
    elif tokens[0] == 'pop':
        s = generate_pop_code(tokens[1], tokens[2])  
        
    elif tokens[0] == 'add' or tokens[0] == 'sub' \
         or tokens[0] == 'mult' or tokens[0] == 'div' \
         or tokens[0] == 'or' or tokens[0] == 'and':
        s = generate_arithmetic_or_logic_code(tokens[0]) 
        
    elif tokens[0] == 'neg' or tokens[0] == 'not':
        s = generate_unary_operation_code(tokens[0])  
        
    elif tokens[0] == 'eq' or tokens[0] == 'lt' or tokens[0] == 'gt':
        s = generate_relation_code(tokens[0], line_number)
      
    elif tokens[0] == 'set':
        s = generate_set_code(tokens[1], tokens[2])
    
    elif tokens[0] == 'end':
        s = generate_exit_code()
        
    else:
        print('translate: Unknown operation, {}, {}'.format(tokens, line_number))  
    return s

def run_vm_translator(file_name):
    """Main translator code. """
    assembly_code = []
    line_number = 1
    
    with open(file_name, 'r') as f:
        for command in f:  
            tokens = (command.rstrip('\n')).split()
            if not tokens:
                continue              
            if tokens[0] == '//':
                continue      
            else:
                s = translate(tokens, line_number)
                line_number = line_number + 1
            if s:
                for i in s:
                    assembly_code.append(i)
            else:
                assembly_code = []
                return assembly_code
    
    return assembly_code


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Python vm_translator.py file-name.vm")
        print("Example: Python vm_translator.py mult.vm")
    else:
        print("Translating VM file:", sys.argv[1])
        print()
        file_name_minus_extension, _ = os.path.splitext(sys.argv[1])
        output_file = file_name_minus_extension + '.asm'
        assembly_code = run_vm_translator(sys.argv[1])
        # print(assembly_code)
        if assembly_code:
            print('Assembly code generated successfully')
            print('Writing output to file:', output_file)
            f = open(output_file, 'w')
            for s in assembly_code:
                f.write('%s\n' %s)
            f.close()
        else:
            print('Error generating assembly code')
