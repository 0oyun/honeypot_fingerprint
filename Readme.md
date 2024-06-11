# 蜜罐指纹识别及检测

识别了两个蜜罐Dionaea、Conpot的指纹，可以用来检测蜜罐。
## 实验环境 

**Dionaea docker**

```bash
docker pull dinotools/dionaea:sha-4e459f1b
```

```bash
docker run -d --name dionaea -p 21:21 -p 42:42 -p 80:80 -p 443:443 -p 445:445 -p 3306:3306 -p 5060:5060 -p 11211:11211 -p 27017:27017 dinotools/dionaea:sha-4e459f1b
```

**Conpot docker**

```bash
docker pull uncleraymondo/conpot_default:1710
```

```bash
docker run -d --name conpot -it -p 80:80 -p 102:102 -p 502:502 -p 161:161/udp  --network=bridge uncleraymondo/conpot_default:1710 /bin/sh 
```
进入容器
```bash
conpot --template default
```

## Dionaea



| Service   | Port  | Request | Response                                                                                                                                                                                                                                                                          |
| --------- | ----- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FTP       | 21    | NULL    | 220 DiskStation FTP server ready                                                                                                                                                                                                                                                  |
| HTTP      | 80    | NULL    | ```<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html><br/><title>Directory listing for /</title><br/><body><br/><h2>Directory listing for /</h2><br/><hr><br/><ul><br/><li><a href="../">../</a><br/></ul><br/><hr><br/></body><br/></html>```   <br />  Server: nginx |
| SSL/Cert  | 443   | NULL    | ssl-cert: Subject: commonName=Nepenthes Development Team/organizationName=dionaea.carnivore.it/countryName=DE                                                                                                                                                                     |
| memcached | 11211 | STAT    | STAT version 1.4.25\r\n<br />STAT rusage_user 0.550000\r\n<br />STAT pointer_size 64\r\n                                                                                                                                                                                          |



## Conpot

| Service | Port | Request                   | Response                                      |
| ------- | ---- | ------------------------- | --------------------------------------------- |
| HTTP    | 80   | GET /HTTP/1.0/ index.html | Last-Modified: Tue, 19 May 1993 09:00:00 GMT  |
| S7      | 102  | NULL                      | S7_ID:88111222                                |
| MODBUS  | 502  | NULL                      | Device Identification: Siemens SIMATIC S7-200 |

## 指纹识别


运行

```bash
python3 main.py [ip]
```
ip 可选，默认为127.0.0.1








