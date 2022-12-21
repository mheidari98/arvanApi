# arvanApi

## General info
Simple ArvanCloud API for python

## Requirements
- [python 3](https://www.python.org/downloads)
- install packages
  ```console
  pip install --upgrade git+https://github.com/mheidari98/arvanApi.git
  ```
- [ArvanCloud API key](https://panel.arvancloud.ir/profile/api-keys)


## Usage
```python
from arvanApi import Arvan

api_key = 'dfbeaaf2-a653-47f7-ad42-caf052d4a2b0'  # this is fake UUID, put your api key here
arv = Arvan(api_key, debug=False)

domain = "myDomain.com"
arv.createDomain(domain)

myDomain = arv.getDomain(domain)
myDomain.changeSsl(ssl_status=True)

ipAddr = '127.0.0.1'  # this is fake ip address, put your server ip address here
dirId = myDomain.createDnsARecord('dir', ipAddr, cloud=False)
cdnId = myDomain.createDnsARecord('cdn', ipAddr, port=80, cloud=True, upstream_https='http')

for key, dns in myDomain.DNSs.items():
    print(dns)
```

## Methods
- [x] create Domain
- [x] get Domain
- [x] delete Domain
- [x] create DNS Record
- [x] get DNS Record
- [x] delete DNS Record
- [x] get SSL status
- [x] change SSL status


## Status
Project is: _in progress_

## License
[MIT](https://choosealicense.com/licenses/mit)

## Contact
Created by [@mheidari98](https://github.com/mheidari98)

## Support
If you like this project, please consider supporting it by donating to the following bitcoin address:



