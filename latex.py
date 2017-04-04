replace_table = {
    '\\ba': '{\\mathbf a}',
    '\\bb': '{\\mathbf b}',
    '\\bc': '{\\mathbf c}',
    '\\bd': '{\\mathbf d}',
    '\\be': '{\\mathbf e}',
    '\\bf': '{\\mathbf f}',
    '\\bg': '{\\mathbf g}',
    '\\bh': '{\\mathbf h}',
    '\\bi': '{\\mathbf i}',
    '\\bj': '{\\mathbf j}',
    '\\bk': '{\\mathbf k}',
    '\\bl': '{\\mathbf l}',
    '\\bm': '{\\mathbf m}',
    '\\bn': '{\\mathbf n}',
    '\\bo': '{\\mathbf o}',
    '\\bp': '{\\mathbf p}',
    '\\bq': '{\\mathbf q}',
    '\\br': '{\\mathbf r}',
    '\\bs': '{\\mathbf s}',
    '\\bt': '{\\mathbf t}',
    '\\bu': '{\\mathbf u}',
    '\\bv': '{\\mathbf v}',
    '\\bw': '{\\mathbf w}',
    '\\bx': '{\\mathbf x}',
    '\\by': '{\\mathbf y}',
    '\\bz': '{\\mathbf z}',
    '\\bA': '{\\mathbf A}',
    '\\bB': '{\\mathbf B}',
    '\\bC': '{\\mathbf C}',
    '\\bD': '{\\mathbf D}',
    '\\bE': '{\\mathbf E}',
    '\\bF': '{\\mathbf F}',
    '\\bG': '{\\mathbf G}',
    '\\bH': '{\\mathbf H}',
    '\\bI': '{\\mathbf I}',
    '\\bJ': '{\\mathbf J}',
    '\\bK': '{\\mathbf K}',
    '\\bL': '{\\mathbf L}',
    '\\bM': '{\\mathbf M}',
    '\\bN': '{\\mathbf N}',
    '\\bO': '{\\mathbf O}',
    '\\bP': '{\\mathbf P}',
    '\\bQ': '{\\mathbf Q}',
    '\\bR': '{\\mathbf R}',
    '\\bS': '{\\mathbf S}',
    '\\bT': '{\\mathbf T}',
    '\\bU': '{\\mathbf U}',
    '\\bV': '{\\mathbf V}',
    '\\bW': '{\\mathbf W}',
    '\\bX': '{\\mathbf X}',
    '\\bY': '{\\mathbf Y}',
    '\\bZ': '{\\mathbf Z}',
}


def preprocess(s):
    global replace_table
    for a in replace_table:
        s = s.replace(a, replace_table[a])
    return s


if __name__ == '__main__ ':
    print(preprocess('abcde\\bb\\beta'))
