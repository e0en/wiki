import os
import re


def extSWFnJoinMP4(address, output_name='output.mp4', is_verbose=True):
    if is_verbose:
        print 'downloading swf...'
    os.system('wget %s -O tmp.swf -q' % address)
    os.system('swfcombine -d tmp.swf -o tmp_unzip.swf')
    f = open('tmp_unzip.swf', 'r')
    s = f.read()
    f.close()
    os.system('rm tmp.swf; rm tmp_unzip.swf')

    if is_verbose:
        print 'extracting urls...'
    urls = []
    i = 0
    while 1:
        # assumption: the url doesn't contain any non-ascii character
        m = re.search('[^"](http://[A-Za-z0-9_\-,.@#$%^&?*/]{5,})', s[i:])
        if m == None:
            break
        else:
            i += m.start(1) + 1
            urls += [m.group(1)]
    urls = urls[2:]

    if is_verbose:
        print 'downloading mp4 files... (this may take a while)'
    N_mp4 = 0
    for i in xrange(len(urls)):
        # heuristic: remove up to 10 characters to remove characters
        # incorrectly included
        for k in xrange(10):
            try:
                if k == 0:
                    s = urls[i]
                else:
                    s = urls[i][:-k]
                os.system('wget %s -O TMP_FILE -q' % s)
                file_size = os.path.getsize('./TMP_FILE')
                # heuristic: file smaller than 100KB is considered to be
                # errorneous output
                if file_size < 10 ** 6:
                    continue
                else:
                    if is_verbose:
                        print ' * downloaded %s' % s
                    N_mp4 += 1
                    os.system('mv TMP_FILE %d.mp4' % N_mp4)
                    break
            except:
                continue

    if N_mp4 > 1:
        if is_verbose:
            print 'Joining %d downloaded files to make %s' % (N_mp4, output_name)
        try:
            cmd = 'mencoder '
            for n in xrange(N_mp4):
                cmd += '%d.mp4 ' % (n + 1)
            cmd += '-ovc copy -oac copy -of lavf -lavfopts format=mp4 -o %s -really-quiet' % output_name
            os.system(cmd)

            #
            if os.path.getsize(output_name) < 1000:
                print 'Joining failed. Trying AAC codec for audio..'
                os.system(cmd.replace('-oac copy', '-oac faac'))
                if os.path.getsize(output_name) < 1000:
                    raise
            else:
                join_success = True
                for n in xrange(N_mp4):
                    os.system('rm %d.mp4' % (n + 1))
        except:
            print 'Joining failed. Intermedite files will not be deleted.'
    elif N_mp4 == 1:
        os.system('mv 1.mp4 %s' % output_name)
    else:
        print 'Sorry, I failed to download any mp4 files.'


if __name__ == '__main__':
    # extSWFnJoinMP4('http://cfile7.uf.tistory.com/media/1530380B4CE866334DA91F')
    # extSWFnJoinMP4('http://cfile8.uf.tistory.com/media/1971B71F4CE85F6F3491F4')
    extSWFnJoinMP4(
        'http://cfile30.uf.tistory.com/media/181C3F024CEB5A1B276069')
