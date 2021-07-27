import types
import io
import zlib
import random
import string
import sys
import base64
import pickle
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

import mitogen.core

if sys.version_info < (2, 7, 11):
    from mitogen.compat import tokenize
else:
    import tokenize

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

def get_unic_name():
    return ''.join(
            random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase + string.digits) for _ in
            range(random.randint(random.randint(10, 50), 99)))

def strip_docstrings(tokens):
    stack = []
    state = 'wait_string'
    for t in tokens:
        typ = t[0]
        if state == 'wait_string':
            if typ in (tokenize.NL, tokenize.COMMENT):
                yield t
            elif typ in (tokenize.DEDENT, tokenize.INDENT, tokenize.STRING):
                stack.append(t)
            elif typ == tokenize.NEWLINE:
                stack.append(t)
                start_line, end_line = stack[0][2][0], stack[-1][3][0]+1
                for i in range(start_line, end_line):
                    yield tokenize.NL, '\n', (i, 0), (i,1), '\n'
                for t in stack:
                    if t[0] in (tokenize.DEDENT, tokenize.INDENT):
                        yield t[0], t[1], (i+1, t[2][1]), (i+1, t[3][1]), t[4]
                del stack[:]
            else:
                stack.append(t)
                for t in stack: yield t
                del stack[:]
                state = 'wait_newline'
        elif state == 'wait_newline':
            if typ == tokenize.NEWLINE:
                state = 'wait_string'
            yield t

def strip_comments(tokens):
    prev_typ = None
    prev_end_col = 0
    for typ, tok, (start_row, start_col), (end_row, end_col), line in tokens:
        if typ in (tokenize.NL, tokenize.NEWLINE):
            if prev_typ in (tokenize.NL, tokenize.NEWLINE):
                start_col = 0
            else:
                start_col = prev_end_col
            end_col = start_col + 1
        elif typ == tokenize.COMMENT and start_row > 2:
            continue
        prev_typ = typ
        prev_end_col = end_col
        yield typ, tok, (start_row, start_col), (end_row, end_col), line

def reindent(tokens, indent=' '):
    old_levels = []
    old_level = 0
    new_level = 0
    for typ, tok, (start_row, start_col), (end_row, end_col), line in tokens:
        if typ == tokenize.INDENT:
            old_levels.append(old_level)
            old_level = len(tok)
            new_level += 1
            tok = indent * new_level
        elif typ == tokenize.DEDENT:
            old_level = old_levels.pop()
            new_level -= 1
        start_col = max(0, start_col - old_level + new_level)
        if start_row == end_row:
            end_col = start_col + len(tok)
        yield typ, tok, (start_row, start_col), (end_row, end_col), line

def minimize_source(source):
    source = mitogen.core.to_text(source)
    tokens = tokenize.generate_tokens(StringIO(source).readline)
    tokens = strip_comments(tokens)
    tokens = strip_docstrings(tokens)
    tokens = reindent(tokens)
    return tokenize.untokenize(tokens)

HEADER = """#This file encrypted PSP v1.0 (https://github.com/IllayDevel/psp)
import zlib, base64, pickle, types
{code} = b'eNqFUktrwzAMvvdX6JiMEDZ6GYX2MnbYfbdSgucqwdS1jKR0y379nObRjnbMJ0nfw0aflbvVAtJxx0isYCl2jM0CvyxGhbfz9JWZ+IZWJR4YmSV7rFO9x8oqcfZguJF8EDFqywG0iyjlS6K8p2pknGWM+9YmYYIyS6Oqh2ENsLVUWqpSa6kNWsDQB0/WeJlaUWMP4r6xOIunM4C1N83M7G+51EF0RoI5otzTnwwP2OTnPPaDa+EFY1HvAga6Z+UDqfmYyYyYzC9vQ+/7fjcsuwbppDwhi6NQuVDT9nEHmzUsV7N1v6bSBUHW7GnyOXxS8N20svwvN9hAtizgOf/HLpLc+o2pzpEXoG30mA2xjr+ijM4e0vB39sV14vkPPGbTgQ=='
exec(zlib.decompress(bytearray(base64.b64decode({code}))))
{name} = {value}
exec(pickle.loads(zlib.decompress(bytearray(base64.b64decode({name})))))"""

def encode(from_file, to_file):
    file = io.open(from_file, 'r').read()
    print("[INFO] Compile file")
    codeobj = compile(minimize_source(file), get_unic_name(), 'exec')
    print("[INFO] Compress data")
    CompressedData = zlib.compress(pickle.dumps(codeobj), 9)
    print("[INFO] Save Data")
    open(to_file, 'w').write(HEADER.format(
        name= get_unic_name(),
        code= get_unic_name(),
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