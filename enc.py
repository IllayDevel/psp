import types
import io
import zlib
import random
import string
import sys
import base64
import pickle
#import dis
#from prettytable import PrettyTable

try:
    import copyreg  # Py 3
except ImportError:
    import copy_reg as copyreg  # Py 2

def code_ctor(*args):
    return types.CodeType(*args)

def reduce_code(co):
    args =  [co.co_argcount, co.co_nlocals, co.co_stacksize,
            co.co_flags, co.co_code, co.co_consts, co.co_names,
            co.co_varnames, co.co_filename, co.co_name, co.co_firstlineno,
            co.co_lnotab, co.co_freevars, co.co_cellvars]
    if sys.version_info[0] >= 3:
        args.insert(1, co.co_kwonlyargcount)
    if sys.version_info > (3, 8):
        args.insert(1, co.co_posonlyargcount)
    return code_ctor, tuple(args)

copyreg.pickle(types.CodeType, reduce_code)

HEADER = """import zlib, base64, pickle, types
{code} = b'eNqFUktrwzAMvvdX6JiMEDZ6GYX2MnbYfbdSgucqwdS1jKR0y379nObRjnbMJ0nfw0aflbvVAtJxx0isYCl2jM0CvyxGhbfz9JWZ+IZWJR4YmSV7rFO9x8oqcfZguJF8EDFqywG0iyjlS6K8p2pknGWM+9YmYYIyS6Oqh2ENsLVUWqpSa6kNWsDQB0/WeJlaUWMP4r6xOIunM4C1N83M7G+51EF0RoI5otzTnwwP2OTnPPaDa+EFY1HvAga6Z+UDqfmYyYyYzC9vQ+/7fjcsuwbppDwhi6NQuVDT9nEHmzUsV7N1v6bSBUHW7GnyOXxS8N20svwvN9hAtizgOf/HLpLc+o2pzpEXoG30mA2xjr+ijM4e0vB39sV14vkPPGbTgQ=='
exec(zlib.decompress(bytearray(base64.b64decode({code}))))
{name} = {value}
exec(pickle.loads(zlib.decompress(bytearray(base64.b64decode({name})))))"""

def encode(from_file, to_file):
    file = io.open(from_file, 'r').read()
#    bytecode = dis.Bytecode(file)
#    t = PrettyTable(['Opcode', 'Opname', 'Argument', 'Argument value', 'Argument readable', 'Offset', 'Starts line',
#                     'Is jump?'])
#    for instr in bytecode:
#        t.add_row(
#            [instr.opcode, instr.opname, instr.arg, instr.argval, instr.argrepr, instr.offset, instr.starts_line,
#             instr.is_jump_target])
#    print(t)
    codeobj = compile(file, 'fakemodule', 'exec')
    print("[INFO] Compress data")
    CompressedData = zlib.compress(pickle.dumps(codeobj), 9)
    print("[INFO] Save Data")
    open(to_file, 'w').write(HEADER.format(
        name=''.join(
            random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase + string.digits) for _ in
            range(random.randint(random.randint(10, 50), 99))),
        code=''.join(
            random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase + string.digits) for _ in
            range(random.randint(random.randint(10, 50), 99))),
        value=base64.b64encode(CompressedData)
    ))

if len(sys.argv) < 3:
    print("[Usage] python3 enc.py in.py out.py num_steps (optional)")
else:
    try:
       if (len(sys.argv)==3):
        encode(sys.argv[1],sys.argv[2])
       elif (len(sys.argv)==4):
           for i in range(int(sys.argv[3])):
               if (i==0):
                   encode(sys.argv[1], sys.argv[2])
               else:
                   print("Step: "+str(i))
                   encode(sys.argv[2], sys.argv[2])

    except:
       print("[ERROR] Invaild file name")