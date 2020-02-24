#!/usr/bin/python


''' -----------------------------------
Run this script from crontab -e, schedule to run once every 10 minutes
*/10 * * * * export OPENVPN_2FA_TOKEN=<put_2fa_static_token_here> && python /home/automation/zbat/util/reboot_open_vpn.py
---------------------------------------'''

import pexpect, pdb, os, sys, time, subprocess

#sudo_password = 'password'
#username = os.environ['OPENVPN_USERNAME']
#password = os.environ['OPENVPN_PASSWORD']
token = os.environ['OPENVPN_2FA_TOKEN']


tunnel = 'tun0'

path_config = '--config /etc/openvpn/zingbox_office.conf'
log_option = '--log /var/log/syslog'
auth_retry = '--auth-retry interact'


tunnel_status = pexpect.spawn('sudo',['ifconfig', tunnel])
#tunnel_status.expect('[sudo]')
#tunnel_status.sendline(sudo_password)

status = tunnel_status.expect(['RUNNING', 'error'])
if status == 0:
    print('tun0 running')
    sys.exit()

elif status == 1:
    # print('did not find tunnel')
    output_ps = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
    output_grep = subprocess.Popen(['grep', 'openvpn'], stdin=output_ps.stdout, stdout=subprocess.PIPE)
    output_awk = subprocess.Popen(['awk', '{print $2}'], stdin=output_grep.stdout, stdout=subprocess.PIPE).communicate()

    openvpn_pid = output_awk[0].split()
    if len(openvpn_pid) > 1:
        for pid in openvpn_pid:
            subprocess.call(['sudo', 'kill', '-9', pid])

    time.sleep(10)

    openvpn_boot = pexpect.spawn('sudo openvpn {0} --log /var/log/syslog --auth-retry interact'.format(path_config))

    '''
    openvpn_boot.expect('[sudo]')
    openvpn_boot.sendline(sudo_password)

    openvpn_boot.expect('Username')
    openvpn_boot.sendline(username)

    openvpn_boot.expect('Password')
    openvpn_boot.sendline(password)
    '''

    openvpn_boot.expect('CHALLENGE')
    openvpn_boot.sendline(token)

    time.sleep(10)
    openvpn_boot.sendcontrol('z')
    time.sleep(1)
    openvpn_boot.sendline('bg')

    time.sleep(10)
    #openvpn_boot.wait()
    print('Done setup openvpn')
    sys.exit()
