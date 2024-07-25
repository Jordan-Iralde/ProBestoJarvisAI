import subprocess

def convert_to_cpp(python_code):
    # Placeholder function for Python to C++ conversion
    cpp_code = python_code.replace('def', 'void')
    return cpp_code

def compile_cpp(cpp_code, output_file='output.exe'):
    with open('temp.cpp', 'w') as f:
        f.write(cpp_code)
    subprocess.run(['g++', 'temp.cpp', '-o', output_file])
    subprocess.run(['rm', 'temp.cpp'])
