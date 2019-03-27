#!/usr/bin/env python3

import base64
import sys
from jenkins.utils import Secret
from jenkins.compat import AES

master_key = open('/var/jenkins_home/secrets/master.key','rb').read()
hudson_secret_key = open('/var/jenkins_home/secrets/hudson.util.Secret','rb').read()
cipher = Secret(master_key=master_key, hudson_secret_key=hudson_secret_key)
encrypted = cipher.encrypt(sys.argv[1],cipher_type=AES.MODE_CBC)
b64_encoded = base64.b64encode(encrypted).decode('utf-8')
message = '{%s}' % b64_encoded
print (message)

