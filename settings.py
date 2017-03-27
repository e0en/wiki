import os

current_dir = os.path.dirname(__file__)
site_uri = '/'
file_num_edits = os.path.join(current_dir, 'num_edits.txt')
log_filename = os.path.join(current_dir, 'log.txt')
upload_path = os.path.join(current_dir, 'media/wiki/upload')
blocked_IPs = ['67.195.111.*', '61.247.204.*', '66.249.*.*', '61.111.15.10',
               '168.188.117.199', '211.245.21.18', '85.25.132.*',
               '91.143.58.*', '188.143.*.*']

main_page = 'MainPage'
yahoo_api_id = \
        't2WwJc_V34Erfd0oEJ5YNUJ0CUfkZo..Lhn3xEWBrITAKSdA.191_6JNCIKhQA--'
