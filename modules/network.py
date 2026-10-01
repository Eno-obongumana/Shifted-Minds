import re


class NetworkModule:
    def __init__(self, adb):
        self.adb = adb

    def ip_addresses(self):
        out, _, _ = self.adb.shell("ip -f inet addr show")
        return re.findall(r"inet (\d+\.\d+\.\d+\.\d+)", out)

    def wifi_info(self):
        out, _, _ = self.adb.shell("dumpsys wifi | grep -i 'mWifiInfo'")
        return out.strip()

    def open_ports(self):
        out, _, _ = self.adb.shell("cat /proc/net/tcp")
        ports = []
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 4:
                continue
            local = parts[1]
            state = parts[3]
            if state == "0A":  # LISTEN
                port_hex = local.split(":")[1]
                ports.append(int(port_hex, 16))
        return sorted(set(ports))

    def ping(self, host):
        out, _, _ = self.adb.shell(f"ping -c 3 {host}", timeout=15)
        return out
