from wiki import wikiMisc


def label(label, acc):
    acc['labels'].append(label)
    return '<a name="%s"></a>' % label
