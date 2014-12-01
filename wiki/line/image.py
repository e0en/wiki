from wiki import wikiMisc

def parse(s, acc):
    d, l = wikiMisc.bar2Dict(s.strip())
    uri = l[0]

    if 'figs' not in acc:
        acc['figs'] = []

    if 'chapters' not in acc:
        section = 0
    else:
        section = acc['chapters'][-1]['section'][0]

    if len(acc['figs']) == 0:
        fig_num = 1
    elif acc['figs'][-1]['section'] == section:
        fig_num = acc['figs'][-1]['num'] + 1
    else:
        fig_num = 1
   
    fig_anchor = 'fig_' + str(section) + '_' + str(fig_num)
    acc['figs'].append({'section':section, 'num':fig_num, 'content': s, 'anchor_txt': fig_anchor})

    result = '<img class="image" src="'+ uri + '" '

    if 'dim' in d:
        dim = d['dim'].split('x')
        w = dim[0]
        h = dim[1]
        if w != '':
            result += 'width="%s" ' %w
        if h != '':
            result += 'height="%s" ' %h

        d.pop('dim')

    for k in d:
        result += k + '="' + d[k] + '" '

    result += '/>'

    return result
