## 安装系统服务

```bash
sudo cp -r mqtt-gateway /opt/mqtt-gateway
sudo cp /opt/mqtt-gateway/template.service /usr/lib/systemd/system/gateway.service
sudo pip3 install -r requirements.txt
sudo systemctl enable gateway.service
sudo systemctl start gateway.service
```

由于蓝牙硬件的特性所以只能串性查询每个设备信息.

* 日志位置: tail -100f /var/log/syslog