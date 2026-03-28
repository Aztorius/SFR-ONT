#!/usr/bin/env python3
from telnetlib3 import Telnet
import re

host = "192.168.4.254"
user = "admin4me"
password = "connect4you@support"
host_tag = "FTTHRED"
ontdatas = {

}

def ont_open(ipaddress: str, user: str, password: str):
    ont = Telnet(ipaddress)
    ont.read_until(b"login:")
    ont.write(user.encode("ascii") + b"\n")
    ont.read_until(b"Password:")
    ont.write(password.encode("ascii") + b"\n")
    ont.read_until(b"> ")
    return ont

def queryont(ont: Telnet, command: str):
    ont.write(command.encode("ascii") + b"\n")
    datasread = ont.read_until(b"> ").decode("ascii")
    print(datasread)
    return datasread

def ont_reboot(ont: Telnet):
    ont.write("reboot".encode("ascii") + b"\n")


def get_led_status(ont: Telnet):
    datas = queryont(ont, "show led status")

    lednames = ['EQPT', 'PON', 'MGMT', 'LAN']
    leds = {}
    regexp_colors = r".*COLOR +([A-Z]+) +([A-Z]+) +([A-Z]+) +([A-Z]+) +.*"
    regexp_curstate = r".*CURSTATE +([A-Z]+) +([A-Z]+) +([A-Z]+) +([A-Z]+) +.*"
    regexp_prestate = r".*PRESTATE +([A-Z]+) +([A-Z]+) +([A-Z]+) +([A-Z]+) +.*"
    regexp_ledstate = r".*LEDSTATE +([A-Z]+) +([A-Z]+) +.*"
    ledcolors = re.search(regexp_colors, datas, re.DOTALL)
    ledstates = re.search(regexp_ledstate, datas, re.DOTALL)
    curstates = re.search(regexp_curstate, datas, re.DOTALL)
    prestates = re.search(regexp_prestate, datas, re.DOTALL)
    index = 1
    for led in lednames:
        leds[led] = {}
        leds[led]['color'] = ledcolors.group(index)
        leds[led]['curstate'] = curstates.group(index)
        leds[led]['prestate'] = prestates.group(index)
        if led == "PON" or led == "LAN":
            leds[led]['ledstate'] = ledstates.group(index // 2)
        ontdatas[led] = ledcolors.group(index)
        index += 1


def get_password(ont: Telnet):
    datas = queryont(ont, "show gpon slid")

    regexp = r".*GPON SLID\(ASCII\)= +([A-Za-z0-9]*).*"
    m = re.search(regexp, datas, re.DOTALL)
    if m:
        ontdatas['Password'] = m.group(1)


def get_serial_number(ont: Telnet):
    datas = queryont(ont, "show gpon sn")
    regexp = r".*GPON Serial Number\(ASCII\) = +([A-Za-z0-9]*).*"
    m = re.search(regexp, datas, re.DOTALL)
    if m:
        ontdatas['Serial Number'] = m.group(1)


def get_rssi(ont: Telnet):
    datas = queryont(ont, "show gpon rssi")
    regexp = r".*receive RSSI = +([\-0-9]*\.[0-9]*).*"
    m = re.search(regexp, datas, re.DOTALL)
    if m:
        ontdatas['rcv_rssi'] = m.group(1)

    regexp = r".*transmit RSSI = +([\-0-9]*\.[0-9]*).*"
    m = re.search(regexp, datas, re.DOTALL)
    if m:
        ontdatas['transmit_rssi'] = m.group(1)

    regexp = r".*Temperature = +([\-0-9]*\.[0-9]*).*"
    m = re.search(regexp, datas, re.DOTALL)
    if m:
        ontdatas['Temperature'] = m.group(1)

    regexp = r".*Vcc = +([\-0-9]*\.[0-9]*).*"
    m = re.search(regexp, datas, re.DOTALL)
    if m:
        ontdatas['Vcc'] = m.group(1)
    regexp = r".*Bias Current = +([\-0-9]*\.[0-9]*).*"
    m = re.search(regexp, datas, re.DOTALL)
    if m:
        ontdatas['Bias Current'] = m.group(1)


def get_firmware(ont: Telnet):
    datas = queryont(ont, "show firmware version")
    version = "Not found"
    for slot in ["Active", "Passive"]:
        regexp = r".*" + slot + r" software ?: ([A-Za-z0-9]*).*"
        m = re.search(regexp, datas, re.DOTALL)
        if m:
            version = m.group(1)
        ontdatas[slot] = version


def get_ranging(ont: Telnet):
    datas = queryont(ont, 'show gpon ranging state')
    regexp = r".*RANGING STATE =+([A-Za-z0-9]*]*).*"
    m = re.search(regexp, datas, re.DOTALL)
    if m:
        ontdatas['Ranging'] = m.group(1)


if __name__ == "__main__":
    ont = ont_open(host, user, password)
    get_led_status(ont)
    get_firmware(ont)
    get_rssi(ont)
    get_password(ont)
    get_serial_number(ont)
    get_ranging(ont)
    print("sfront,host=%s ontpassword=\"%s\",ontserial=\"%s\",rcv_rssi=%s,transmit_rssi=%s,bias_current=%s,"
          "temperature=%s,active_firmware=\"%s\",passive_firmware=\"%s\",eqpt=\"%s\",mgmt=\"%s\",pon=\"%s\","
          "lan=\"%s\",vcc=%s,ranging=%s" % (
           host_tag,
           ontdatas['Password'],
           ontdatas['Serial Number'],
           ontdatas['rcv_rssi'],
           ontdatas['transmit_rssi'],
           ontdatas['Bias Current'],
           ontdatas['Temperature'],
           ontdatas["Active"],
           ontdatas["Passive"],
           ontdatas['EQPT'],
           ontdatas['MGMT'],
           ontdatas['PON'],
           ontdatas['LAN'],
           ontdatas['Vcc'],
           ontdatas['Ranging'],
    ))

