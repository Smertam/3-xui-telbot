import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('212.87.199.33', username='root', password='Artin@1234', timeout=15)

sftp = ssh.open_sftp()
sftp.put(r'C:\Users\Elyas\Desktop\3x-ui\test_server.py', '/tmp/test_import.py')
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/root/3x-ui/venv/bin/python /tmp/test_import.py')
out = stdout.read()
err = stderr.read()
print("STDOUT:", out.decode("utf-8", errors="replace"))
print("STDERR:", err.decode("utf-8", errors="replace"))

ssh.close()
