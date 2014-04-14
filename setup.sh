echo "Pokud nemáte administrátorská oprávnění skript selže!"
echo "Zadejte vaše heslo pro instalaci smssender"
sudo apt-get install sqlite python-sqlite 
sudo mkdir /usr/bin/smssender
echo "Probíhá registrace do /usr/bin"
sudo cp ./usr/bin/smssender /usr/bin/smssender
sudo mkdir /usr/share/smssender
echo "Probíhá kopírování knihoven"
sudo cp -r ./usr/share/smssender /usr/share/smssender

