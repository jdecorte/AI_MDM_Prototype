#/bin/sh

# This is a script that installs the AI-MDM tool on a Linux Alma server using Vagrant
# This assumes that there is a nginx.conf file in the shared folder /vagrant

sudo dnf -y install git nginx java-1.8.0-openjdk wget pip

# Download external files 
wget https://github.com/zinggAI/zingg/releases/download/v0.3.4/zingg-0.3.4-SNAPSHOT-spark-3.1.2.tar.gz
wget https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz
tar xf zingg-0.3.4-SNAPSHOT-spark-3.1.2.tar.gz
mv zingg-0.3.4-SNAPSHOT zingg-0.3.4
tar xf spark-3.1.2-bin-hadoop3.2.tgz
git clone https://github.com/hogent-cads/AI_MDM_Prototype.git

# Copy external files and create symlinks with simpler names
mkdir AI_MDM_Prototype/external
cp -r zingg-0.3.4 AI_MDM_Prototype/external/
cp -r spark-3.1.2-bin-hadoop3.2 AI_MDM_Prototype/external/
ln -s AI_MDM_Prototype/external/zingg-0.3.4 AI_MDM_Prototype/external/zingg
ln -s AI_MDM_Prototype/external/spark-3.1.2-bin-hadoop3.2 AI_MDM_Prototype/external/spark 



cd AI_MDM_Prototype
# Do not use virtual environment for now. This causes problems with Popen
#mkdir envs
#python -m venv envs/ai-mdm
#source envs/ai-mdm/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configure and start nginx
# Note: root is set as /usr/share/nginx/html in nginx.conf
sudo mkdir  -p /usr/share/nginx/html/reports
sudo chmod a+rw /usr/share/nginx/html/reports
sudo cp /vagrant/nginx.conf /etc/nginx/
sudo systemctl enable nginx
sudo systemctl start nginx

# Allow forwarding in SELinux
sudo setsebool -P httpd_can_network_connect 1

