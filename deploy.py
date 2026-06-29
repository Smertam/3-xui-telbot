import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('212.87.199.33', username='root', password='Artin@1234', timeout=15)

sftp = ssh.open_sftp()
sftp.put(r'C:\Users\Elyas\Desktop\3x-ui\handlers\user.py', '/root/3x-ui/handlers/user.py')
print('Uploaded user.py')
sftp.close()

stdin, stdout, stderr = ssh.exec_command('lsof -ti:5000')
pids = stdout.read().decode().strip()
for p in pids.split('\n'):
    if p.strip():
        ssh.exec_command('kill -9 ' + p.strip())
time.sleep(2)

ssh.exec_command('cd /root/3x-ui && nohup /root/3x-ui/venv/bin/python run.py > bot.log 2>&1 &')
time.sleep(5)

stdin, stdout, stderr = ssh.exec_command('tail -5 /root/3x-ui/bot.log')
print(stdout.read().decode('utf-8', 'replace'))
ssh.close()
