#!/usr/bin/env python

import logging
import os
from rich.console import Console
from rich.table import Table
#from tabulate import tabulate
from arvanApi import Arvan

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

console = Console()

def clearScreen():
    #console.print("\033c", end="")
    os.system('cls' if os.name == 'nt' else 'clear')


def changeSslStatus(domain, ssl_status):
    if ssl_status :
        console.print("\n> Do you want to disable ssl? (yes/no)")
        ssl = input("> ").strip()
        if ssl in ["yes", "y"] :
            domain.changeSsl(ssl_status=False)
    else :
        console.print("\n> Do you want to enable ssl? (yes/no)")
        ssl = input("> ").strip()
        if ssl in ["yes", "y"] :
            domain.changeSsl(ssl_status=True)


def showDnsRecords(DNSs, showindex=False):
    dnsList = []
    table = Table(show_lines=True, show_header=True, header_style="bold magenta", 
                    row_styles=["dim", ""], highlight=True)
    
    if showindex:
        table.add_column("Index", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Name", style="bright_cyan", justify="center")
    table.add_column("IP", style="green", justify="center")
    table.add_column("cloud", justify="center")

    index = 0
    for key, rec in DNSs:
        port  = f":{rec.value[0]['port']}" if rec.value[0]['port'] else ""
        host = f"{rec.value[0]['ip']}{port}"
        name = rec.domain if rec.name == '@' else f"{rec.name}.{rec.domain}"
        if showindex:
            table.add_row(str(index), rec.type, name, host, str(rec.cloud))
        else:
            table.add_row(rec.type, name, host, str(rec.cloud))
        dnsList.append([rec.type, name, host, rec.cloud, rec.id])
        index += 1
    # https://stackoverflow.com/questions/9535954
    #table = tabulate(dnsList, headers=['Type', 'name', 'ip', 'cloud', 'id'], tablefmt='fancy_grid', showindex=showindex)
    #console.print(table)

    console.print(table)

    return dnsList


def createDnsRecord(domain):
    # create dns record with type A or AAAA
    console.print("\nCreate DNS record with type A or AAAA")

    console.print("\n> Please enter your dns record name. (subdomain or @ for root domain)")
    dnsName = input("> ").strip()

    console.print("\n> Please enter your dns record ipv4 or ipv6. For example it like (192.168.27.32)")
    dnsIp = input("> ").strip()

    console.print("\n> Please enter your dns record port. For example it like (80)")
    console.print("  port should be in (1, 65535)")
    console.print("  If you don't want to use port, just press enter")
    dnsPort = input("> ")
    try:
        dnsPort = int(dnsPort)
    except:
        dnsPort = None

    console.print("\n> Please enter your dns ttl. For example it like (1800)")
    console.print("  TTL is the time to live for the DNS record. It is the amount of time that the DNS record is cached by the DNS server.")
    console.print("  The lower the TTL, the more often the DNS server will check for changes to the DNS record.")
    console.print("  The higher the TTL, the longer the DNS server will cache the DNS record.")
    console.print("  ttl should be in (120, 180, 300, 600, 900, 1800, 3600, 7200, 18000, 43200, 86400, 172800, 432000)")
    console.print("  If you don't want to use ttl, just press enter")
    dnsTtl = input("> ").strip()
    try:
        dnsTtl = int(dnsTtl)
    except:
        dnsTtl = 432000

    console.print("\n> Do you want to Using the Cloud option? default is no")
    console.print("  the traffic to your server go through Arvan's edge servers so it will be secured and optimized.")
    console.print("  When the Cloud option is disabled, your origin server address is publicly exposed and is not protected against cyber threats.")
    console.print("  If you don't want to use cloud, just press enter. (yes/no)")
    dnsCloud = input("> ").strip()

    console.print("\n> Please enter your Origin server connection protocol.")
    console.print("  If the value is \"default\", the protocol is determined automatically based on the port number.")
    console.print("  If the value is \"auto\", the protocol is determined automatically based on the port number and the certificate of the origin server.")
    console.print("  If the value is \"http\", the protocol is always HTTP.")
    console.print("  If the value is \"https\", the protocol is always HTTPS.")
    console.print("  If you don't want to use upstream_https, just press enter")
    upstream_https = input("> ").strip()
    
    if upstream_https not in ["default", "auto", "http", "https"]:
        upstream_https = 'default'

    if domain.createDnsARecord(
                            dnsName, 
                            dnsIp, 
                            port=dnsPort, 
                            ttl=dnsTtl,
                            cloud=dnsCloud in ["yes", "y"], 
                            upstream_https=upstream_https
                            ) :
        console.print("[+] DNS record created")
    else:
        console.print("[-] DNS record not created")


def deleteDnsRecord(domain):
    console.print("\nDelete DNS record")
    DNSs = showDnsRecords(domain.DNSs.items(), showindex=True)
    if len(DNSs) == 0:
        console.print("[-] No DNS record found")
        return
    
    console.print(f"\n> Please select your dns record [0, {len(DNSs)-1}]")
    dnsIndex = input("> ").strip()
    try:
        dnsIndex = int(dnsIndex)
    except:
        dnsIndex = -1
    if dnsIndex not in range(len(DNSs)):
        console.print("[-] Invalid dns record index")
        return
    
    console.print(f"\n> Are you sure you want to delete this dns record?")
    console.print(f"\t{DNSs[dnsIndex]}")
    console.print("  (yes/no)")
    sure = input("> ").strip()
    if sure not in ["yes", "y"]:
        return
    if domain.deleteDnsById(DNSs[dnsIndex][-1]):
        console.print("[+] DNS record deleted")
    else:
        console.print("[-] DNS record not deleted")


def deleteDomain(arv, domain):
    console.print(f"\n> Are you sure you want to delete this domain?")
    console.print(f"\t{domain.domain}")
    console.print("  (yes/no)")
    sure = input("> ").strip()
    if sure not in ["yes", "y"]:
        return False
    if arv.deleteDomain(domain.domain):
        console.print("[+] Domain deleted")
    else:
        console.print("[-] Domain not deleted")
    return True


def domainMenu(arv, domain):
    while True:
        console.print(f"\nManaging Domain: {domain.domain} \ttype: {domain.type} \tstatus: {domain.status}")
        if domain.current_ns != domain.ns_keys :
            console.print("[X] Change you ns records from your domain provider to the following records")
            console.print(f"\tns keys = {domain.ns_keys}")
            #exit(1)
        ssl_status = domain.getSslSettings()['data']['ssl_status']
        console.print(f"ssl status: {ssl_status}")

        console.print("\nSelect an action:")
        console.print("\t0 - back to main menu")
        console.print("\t1 - change ssl status")
        console.print("\t2 - show dns records")
        console.print("\t3 - add dns record")
        console.print("\t4 - delete dns record")
        console.print("\t5 - delete domain")

        choice = input("> ")
        clearScreen()

        try:
            choice = int(choice)
        except:
            console.print("[-] Invalid choice")
            continue
        
        if choice == 0:
            return
        elif choice == 1:
            changeSslStatus(domain, ssl_status)
        elif choice == 2:
            console.print("\nDNS Records:")
            showDnsRecords(domain.DNSs.items())
        elif choice == 3:
            createDnsRecord(domain)
        elif choice == 4:
            deleteDnsRecord(domain)
        elif choice == 5:
            if deleteDomain(arv, domain):
                return


def startMenu(arv):
    while True:
        domains = arv.getDomains()
        console.print("\nSelect a domain to manage:")
        console.print("\t0 - exit")
        console.print("\t1 - add new domain")
        for i, domain in enumerate(domains):
            console.print(f"\t{i+2} - {domain.domain}")
        
        choice = input("> ")
        clearScreen()

        try:
            choice = int(choice)
        except:
            console.print("[-] Invalid choice")
            continue
        
        if choice == 0:
            console.print("\nGoodbye!")
            break
        elif choice == 1:
            console.print("\n> Please enter your domain name. For example it like (example.com)")
            domainName = input("> ").strip()
            if arv.createDomain(domainName):
                console.print("[+] Domain created")
            else:
                console.print("[-] Domain not created")
        elif choice < len(domains)+2:
            domain = domains[choice-2]
            domainMenu(arv, domain)
        else:
            console.print("[-] Invalid choice")


def main() -> None:
    console.print("> Welcome to Arvan CDN Manager")
    console.print("> Please enter your Arvan ApiKey. For example it like (Apikey df0bbd86-8f94-5c1e-a6ebasdasd-asdasd)")
    console.print("  If you don't have an ApiKey, you can get it from https://panel.arvancloud.ir/profile/machine-user")
    apikey = input("> ").strip()

    console.print("")
    with console.status("[bold cyan]Checking ApiKey...") as status:
        arv = Arvan(apikey, debug=False)
        if arv._domainsDict == False :
            exit(1)
        console.print("[bold green]> ApiKey authenticated")
    
    startMenu(arv)


if __name__ == "__main__":
    main()

