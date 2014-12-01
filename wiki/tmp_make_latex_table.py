replace_table = 'replace_table = {\n'

char_list = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

for a in char_list:
    replace_table += "'\\\\b%s': '{\\\\mathbf %s}',\n" % (a, a)
replace_table += '}\n'

f = open('tmp.py', 'w')
f.write(replace_table)
f.close()
'''
replace_table = eval(replace_table)

def preprocess(s):
    for a in replace_table:
        s = s.replace(a, replace_table[a])
    return s
'''
