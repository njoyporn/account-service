# nJoy
**With nJoy its all about enjoying the movies and or series you watch.**
## Disclaimer
**Running this application is not easy at the moment - Its open source so GFIY**
## Running the application (from Source /w Docker & Docker-Compse)
**This is how I would run it without an CI/CD integration and before I have worked on the setup wizard.**

**Clone the repository to your host**
```bash
git clone https://github.com/njoy/njoy-account-service.git
# change directory
cd njoy-account-service
```
**Create Volumes**
```bash
#those should already exist because this service depends on the njoy-backend
mkdir -p /opt/njoy-backend/data/videos
mkdir /opt/njoy-backend/data/thumbnails
mkdir /opt/njoy-backend/config
mkdir /opt/njoy-backend/keys
mkdir /opt/njoy-backend/logs
```
**Create Key-Pair**
```bash
#those should already exist because this service depends on the njoy-backend
mv backend-shared/security/.keys/temp.py
python3 temp.py
mv temp.py /backend-shared/security.keys/temp.py
```
**Move keys to volume**
```bash
#those should already exist because this service depends on the njoy-backend
mv *.pem /opt/njoy-backend/keys
```
**Copy config to volume**
```bash
#the config should already exist because this service depends on the njoy-backend
mv config/example.config.json /opt/njoy-backend/config/config.json
# open config to edit
nano config.json
```
**Edit config to your needs**
```json
{
    ...
    "account_service" {
        "hostname":"0.0.0.0",
        "port": 8621
    }
    ...
}
```
**Build Docker-Image**
```bash
docker build -f dockerfile . -t njoy-account-service
```
**Spin up container**
```bash
docker compose -p njoy-account-service -f docker-compose.yaml up -d
```
### Behind the scenes
**There is some magic or logic working in the background**
- Nothing special... The service depends on the njoy-backend
**Username and password are defined in the config.json**
*If you change the config.json you need to restart the container*
```bash
docker restart njoy-account-service
```
**API-Health-Check**
```bash
#copy and open address
http://localhost:6695/api/v1/healthz
#should return '200 OK'
```
## Next Steps
### 1 Connect the Frontend-Application
- **Follow this [Guide](https://google.de) to host the frontend**
### 2 Preparation for Production
- **DNS:**
    - Domain: yourdomain.com
    - Subdomain: api.yourdomain.com
    - *Optional:* acquire a certificate for TSL
- **Server**
    - **CPU-Cores:**    2
    - **RAM:**          4 GB
    - **HDD:**          20 GB
    - **SSD:**          120 GB (depending on your file size)
##### Webserver
- #### *Apache2*
- #### *Gunicorn*
### **INFO:** You need to enable the headers module
```bash
a2enmod headers
```
```bash
#In order to acces the video service update the virtual host entry of the api
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ...
    ProxyPreserveHost   On
    RewriteEngine       On

    RewriteRule         ^/account-service/(.*) http://localhost:8621/$1 [P,L]
    ProxyPassReverse    /account-service/ http://localhost:8621/
    
    #ProxyPass /video-service http://localhost:6695/video
    #ProxyPassReverse /video-service http://localhos:6695/video
    ...
</VirtualHost>
</IfModule>
```
After you configured everything correct you can check the settings
```bash
apachectl -t
```
If everythig is ok restart Apache2
```bash
service apache2 restart
```
Else you can start investigating your errors with:
```bash
systemctl restart apache2
```
## Known Issues
### Docker
#### Work-Around