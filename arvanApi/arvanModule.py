#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Doc @ https://www.arvancloud.ir/docs/api/cdn/4.0
# Api Key @ https://panel.arvancloud.ir/profile/api-keys
import json
import logging
from time import time
import requests


class ArvanDNS:
    def __init__(self, data, domain, debug=False):
        # for key in data:
        #     setattr(self, key, data[key])
        self.domain = domain
        self.id = data.get('id', None)
        self.type = data.get('type', None)
        self.name = data.get('name', None)
        self.value = data.get('value', None)
        self.ttl = data.get('ttl', None)
        self.cloud = data.get('cloud', None)
        self.upstream_https = data.get('upstream_https', None)
        self.ip_filter_mode = data.get('ip_filter_mode', None)
        self.can_delete = data.get('can_delete', None)
        self.is_protected = data.get('is_protected', None)
        self.health_check_status = data.get('health_check_status', None)
        self.health_check_setting = data.get('health_check_setting', None)
        self.created_at = data.get('created_at', None)
        self.updated_at = data.get('updated_at', None)
        self.monitoring_status = data.get('monitoring_status', None)
        self.health_check = data.get('health_check', None)

    def __repr__(self) -> str:
        if self.type == 'a':
            port  = f":{self.value[0]['port']}" if self.value[0]['port'] else ""
            if self.name == '@':
                return f"[{self.type}] {self.domain} -> {self.value[0]['ip']}{port}\t ID: {self.id}"
            else:
                return f"[{self.type}] {self.name}.{self.domain}  -> {self.value[0]['ip']}{port}\t ID: {self.id}"
        else:
            return f"[{self.type}] {self.name}\t ID: {self.id}"


class ArvanDomain:
    def __init__(self, api_key, data, debug=False):
        self.API_KEY = f"{api_key}"
        self.HEADERS = {
                    'Authorization': f'{self.API_KEY}',
                    'Content-Type': 'application/json'
                }
        
        self.id = data.get('id', None)
        self.user_id = data.get('user_id', None)
        self.domain = data.get('domain', None)
        self.name = data.get('name', None)
        self.services = data.get('services', {})
        self.dns_cloud = data.get('dns_cloud', None)
        self.plan_level = data.get('plan_level', None)
        self.features = data.get('features', None)
        self.smart_routing_status = data.get('smart_routing_status', None)
        self.ns_keys = data.get('ns_keys', [])
        self.current_ns = data.get('current_ns', [])
        self.status = data.get('status', None)
        self.parent_domain = data.get('parent_domain', None)
        self.is_paused = data.get('is_paused', None)
        self.is_suspended = data.get('is_suspended', None)
        self.type = data.get('type', None)
        self.cname_target = data.get('cname_target', None)
        self.custom_cname = data.get('custom_cname', None)
        self.transfer = data.get('transfer', None)
        self.created_at = data.get('created_at', None)
        self.updated_at = data.get('updated_at', None)
        self.DEBUG = debug
        self.BASE_URL = f"https://napi.arvancloud.ir/cdn/4.0/domains/{self.domain}"
        self.DNSs = self._getDNS()

    def _getDNS(self, search='', page=1, rType=None, per_page=300):
        url = f'{self.BASE_URL}/dns-records'
        params = {
                    'search':   f'{search}',
                    'page':     f'{page}',
                    'type':     f'{rType}',
                    'per_page': f'{per_page}'
                }
        r = requests.get(url, params=params, headers=self.HEADERS)
        DnsList ={}
        if r.status_code == 200 :
            res = r.json()
            for record in res['data']:
                rec = ArvanDNS(record, self.domain, self.DEBUG)
                if rec.type == 'a':
                    DnsList[(rec.type, rec.name)] = rec
                if self.DEBUG:
                    logging.debug(f"\t{rec}")
            if res['links']['next'] :
                DnsList.update(self._getDNS(search, page+1, rType, per_page))
        elif r.status_code == 401:
            logging.error("[_getDNS] Access token is missing or invalid")
        elif r.status_code == 404:
            logging.error("[_getDNS] Domain not found")
        else:
            logging.error(f"[_getDNS] Err with status code {r.status_code}")
        return DnsList

    def getDnsRecords(self, type, name):
        return self.DNSs.get((type, name), None)

    def createDnsARecord(self, name, ipAddr, port=None, ttl=432000, cloud=False, upstream_https='default'):
        url = f'{self.BASE_URL}/dns-records'

        acceptTtl = [120, 180, 300, 600, 900, 1800, 3600, 7200, 18000, 43200, 86400, 172800, 432000]
        ttl = ttl if ttl in acceptTtl else 432000

        payload = {
                    'type': 'a',
                    'name': f'{name}',
                    'value':[
                        {
                            'ip': f'{ipAddr}',
                            'port': port
                        }
                    ],
                    'ttl':ttl,
                    'cloud': cloud,
                    'upstream_https': f'{upstream_https}'
                }

        r = requests.post(url, data=json.dumps(payload), headers=self.HEADERS )

        if r.status_code == 201 :
            rec = ArvanDNS(r.json()['data'], self.domain, self.DEBUG)
            self.DNSs[(rec.type, rec.name)] = rec
            logging.info(f"DNS record created: {rec}")
            return r.json()['data']['id']
        elif r.status_code == 401:
            logging.error("[createDnsARecord] Access token is missing or invalid")
        elif r.status_code == 404:
            logging.error("[createDnsARecord] Resource not found")
        elif r.status_code == 422:
            logging.error("[createDnsARecord] The given data was invalid")
        else:
            logging.error(f"[createDnsARecord] Err with status code {r.status_code}")
        return None
    
    def deleteDnsByName(self, name, type='a'):
        if (type, name) not in self.DNSs:
            logging.error(f"[deleteDnsByName] DNS record {name} not found")
            return False
        
        rId = self.getDnsRecords(type, name).id
        url = f"{self.BASE_URL}/dns-records/{rId}"
        r = requests.delete(url, headers=self.HEADERS )

        if r.status_code == 200 :
            logging.info(f"[delDnsRecord] DNS record deleted") 
            del self.DNSs[(type, name)]
            return True
        elif r.status_code == 401:
            logging.error("[delDnsRecord] Access token is missing or invalid")
        elif r.status_code == 404:
            logging.error("[delDnsRecord] Resource not found")
        else:
            logging.error(f"[delDnsRecord] Err with status code {r.status_code}")
        return False
    
    def deleteDnsById(self, rId):
        url = f"{self.BASE_URL}/dns-records/{rId}"
        r = requests.delete(url, headers=self.HEADERS )

        if r.status_code == 200 :
            logging.info(f"[delDnsRecord] DNS record deleted")
            self.DNSs = self._getDNS()
            return True
        elif r.status_code == 401:
            logging.error("[delDnsRecord] Access token is missing or invalid")
        elif r.status_code == 404:
            logging.error("[delDnsRecord] Resource not found")
        else:
            logging.error(f"[delDnsRecord] Err with status code {r.status_code}")
        return False
    
    def getSslSettings(self):
        url = f'{self.BASE_URL}/ssl'
        r = requests.get(url, headers=self.HEADERS)
        if r.status_code == 200 :
            logging.info(f"Succesfully retrieved SSL settings for {self.domain}")
            return r.json()
        elif r.status_code == 401:
            logging.error("Access token is missing or invalid")
        elif r.status_code == 404:
            logging.error("Resource not found")
        return None
    
    def changeSsl(self, ssl_status=True): # True for enable, False for disable
        url = f'{self.BASE_URL}/ssl'
        payload = { 'ssl_status': ssl_status }
        r = requests.patch(url, data=json.dumps(payload), headers=self.HEADERS  )
        if r.status_code == 200 :
            logging.info(f"Succesfully changed SSL settings for {self.domain}")
            return True
        elif r.status_code == 401:
            logging.error("Access token is missing or invalid")
        elif r.status_code == 404:
            logging.error("Resource not found")
        else:
            logging.error(f"Err with status code {r.status_code}")
        return False

    def _deleteDomain(self):
        url = f'{self.BASE_URL}'
        payload = { 'id': self.id }
        r = requests.delete(url, data=json.dumps(payload), headers=self.HEADERS  )
        if r.status_code//100 == 2:
            logging.info(f"Domain {self.domain} deleted")
            return True
        elif r.status_code == 401:
            logging.error("Access token is missing or invalid")
        elif r.status_code == 404:
            logging.error("Resource not found")
        elif r.status_code == 422:
            logging.error(f"The given data was invalid")
        else:
            logging.error(f"Err with status code {r.status_code}")
        return False
        
    def __repr__(self) -> str:
        return f"Domain: {self.domain} \t Type: {self.type} \t ID: {self.id}"


class Arvan:
    def __init__(self, api_key, debug=False):
        self.BASE_URL = "https://napi.arvancloud.ir/cdn/4.0"
        self.API_KEY = api_key if "Apikey" in api_key else f"Apikey {api_key}" 
        self.HEADERS = {
                    'Authorization': f'{self.API_KEY}',
                    'Content-Type': 'application/json'
                }
        self.DEBUG = debug
        self._domainsDict = self.initDomains()

    def initDomains(self, search='', page=1, per_page=300):
        url = f'{self.BASE_URL}/domains'
        params = {
                    'search':   f'{search}',
                    'page':        page,
                    'per_page':    per_page
                }
        r = requests.get(url, params=params, headers=self.HEADERS )
        DomainList = {}
        if r.status_code == 200 :
            res = r.json()
            for record in res['data']:
                rec = ArvanDomain(self.API_KEY, record, debug=self.DEBUG)
                DomainList[record['domain']] = rec
                if self.DEBUG :
                    logging.debug(f"{rec}")
            if res['links']['next'] :
                DomainList.update(self.GetDomains(search, page+1, per_page))
            return DomainList
        elif r.status_code == 401:
            logging.error("Access token is missing or invalid")
        else:
            logging.error(f"Err with status code {r.status_code}")
        return False

    def createDomain(self, domain):
        if domain in self._domainsDict:
            logging.error(f"Domain {domain} already exists")
            return None
        
        url = f"{self.BASE_URL}/domains/dns-service"
        payload = {
                    'domain': f'{domain}',
                    'domain_type':'full',
                    'plan_level': 1,
                }
        r = requests.post(url, data=json.dumps(payload), headers=self.HEADERS)
        if r.status_code//100 == 2 :
            rec = ArvanDomain(self.API_KEY, r.json()['data'], debug=self.DEBUG)
            self._domainsDict[domain] = rec
            if self.DEBUG :
                logging.debug(f"New domain {domain} created!")
                logging.debug(f"please set ns to {rec.ns_keys}")
            return True
        elif r.status_code == 401:
            logging.error("Access token is missing or invalid")
        elif r.status_code == 422:
            logging.error(f"The given data was invalid")
        else:
            logging.error(f"Err with status code {r.status_code}")
        return False

    def deleteDomain(self, domain):
        if domain in self._domainsDict:
            if self._domainsDict[domain]._deleteDomain():
                del self._domainsDict[domain]
                return True
        return False
    
    def getDomains(self):
        return list(self._domainsDict.values())

    def getDomain(self, Domain):
        return self._domainsDict.get(Domain, None)
    
    def __repr__(self) -> str:
        return f"ArvanApi with api_key: {self.API_KEY}"

