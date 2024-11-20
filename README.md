DIME - Dispositivo Inteligente de Monitoramento de Energia

🛠 Descrição do Projeto

O DIME é um dispositivo IoT desenvolvido para monitorar e otimizar o consumo de energia elétrica em ambientes residenciais e comerciais. Utilizando o Raspberry Pi 3 Model B+ e o sensor Tapo P110, o DIME coleta dados de consumo, processa informações e envia alertas e relatórios para os usuários.

⚙️ Funcionamento e Uso

Como funciona:
Monitoramento de Consumo: O sensor Tapo P110 captura os dados de consumo energético.
Processamento: O Raspberry Pi coleta esses dados, processa-os e os armazena localmente.
Comunicação: Dados são enviados e recebidos por meio do protocolo MQTT.
Alertas e Relatórios: Relatórios são gerados e enviados via e-mail para os usuários.
Reprodução:
Clone este repositório:
bash
Copiar código
git clone https://github.com/<seu_usuario>/dime.git
Instale as dependências listadas no arquivo requirements.txt:
bash
Copiar código
pip install -r requirements.txt
Configure os parâmetros no código principal (e-mail do remetente, credenciais do MQTT, etc.).
Inicie o script principal para começar a monitorar o consumo de energia:
bash
Copiar código
python main.py
💻 Software Desenvolvido

O software do DIME foi desenvolvido em Python, utilizando as seguintes bibliotecas:

PyP100: Para comunicação com a tomada Tapo P110.
paho-mqtt: Para implementação do protocolo MQTT.
Flask: Para exposição de serviços REST (caso necessário no futuro).
Matplotlib: Para geração de gráficos de consumo.
smtplib: Para envio de relatórios e notificações via e-mail.
json e datetime: Para manipulação de dados e registros de tempo.
A estrutura do código é modular e contém threads para gerenciar comunicação e processamento em tempo real.

🔧 Hardware Utilizado

Raspberry Pi 3 Model B+: Placa principal para execução do software.
Tapo P110: sensor para medição do consumo de energia.
Fonte de Alimentação: Para o Raspberry Pi.
Cabos Ethernet/Wi-Fi: Para comunicação em rede.
📡 Documentação de Interfaces e Protocolos

Comunicação:
Via Internet: O protocolo TCP/IP é usado para garantir a comunicação entre o dispositivo e os serviços externos.
Entre Dispositivos: O protocolo MQTT é utilizado para troca de mensagens entre o DIME e outros dispositivos.
Protocolos e Serviços Utilizados:
MQTT Broker: Gerencia as mensagens enviadas e recebidas pelo DIME.
SMTP: Para envio de e-mails com relatórios e notificações.
🌐 Configuração de Comunicação/Controle

Requisitos:
Rede Wi-Fi para conectar o Raspberry Pi e a sensor Tapo P110.
MQTT Broker configurado (Mosquitto ou outro de sua preferência).
Conta de e-mail configurada para envio de notificações.
Passos de Configuração:
Instale o broker MQTT no Raspberry Pi (caso necessário):
bash
Copiar código
sudo apt-get install mosquitto mosquitto-clients
mosquitto -v
Configure as credenciais do MQTT e do e-mail no código.
Execute o script principal para iniciar o monitoramento.

