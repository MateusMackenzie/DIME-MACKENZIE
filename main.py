from PyP100 import PyP110
import paho.mqtt.client as mqtt
import time
import threading
from flask import Flask
import smtplib
import email.message
import json
import matplotlib.pyplot as plt
from datetime import datetime


# Configurações do dispositivo e MQTT
device_ip = "DEVICE_IP"
username = "USERNAME"
password = "DEVICE_PASSWORD"
BROKER_IP = "BROKER_IP"
BROKER_PORT = 1883
TOPICO_CONSUMO = "DIME"
TOPICO_ALERTA = "DIME-ALERTA"
LIMITE_CONSUMO = 40
EMAIL_REMETENTE = "EMAIL_REMETENTE"
EMAIL_SENHA = "APP_SENHA_EMAIL"
EMAIL_DESTINATARIO = "EMAIL_DESTINATARIO"

p110 = PyP110.P110(device_ip, username, password)  # Cria o objeto do dispositivo

# Criar servidor Flask
app = Flask(__name__)


# Função para conectar ao broker MQTT
def conectar_broker():
    cliente = mqtt.Client()
    cliente.connect(BROKER_IP, BROKER_PORT, 60)
    return cliente


# Função para publicar o consumo no MQTT
def publicar_consumo_mqtt():
    sensor_name = p110.getDeviceName()
    sensor_energy_info = p110.getEnergyUsage()
    consumo_watts = sensor_energy_info.get("current_power", None) / 1000
    payload = {"sensor": sensor_name, "consumo": consumo_watts}

    cliente = conectar_broker()
    cliente.publish(TOPICO_CONSUMO, str(payload))
    print(f"Publicado consumo: {consumo_watts:.2f} W no tópico {TOPICO_CONSUMO}")

    if consumo_watts > LIMITE_CONSUMO:
        alerta_payload = {"sensor": sensor_name, "consumo atual": consumo_watts, "consumo maximo definido": LIMITE_CONSUMO}
        cliente.publish(TOPICO_ALERTA, str(alerta_payload))
        print(f"Alerta de consumo enviado para {TOPICO_ALERTA}!")



# Função para monitorar o consumo
def monitorar_consumo():
    while True:
        publicar_consumo_mqtt()
        time.sleep(5)





# Variáveis globais para armazenar os dados
consumos = []
timestamps = []

# Função chamada quando uma mensagem é recebida do MQTT
def on_message(client, userdata, msg):
    print(f"Mensagem recebida no tópico {msg.topic}: {msg.payload.decode()}")
    global timestamps, consumos
    """Função chamada ao receber uma mensagem em qualquer tópico assinado."""
    try:
        if msg.topic == TOPICO_ALERTA:
            alerta = json.loads(msg.payload.decode('utf-8').replace("'", '"'))
            sensor_name = alerta['sensor']
            consumo = alerta['consumo atual']
            consumo_maximo_definido = alerta['consumo maximo definido']

            enviar_alerta_email(sensor_name, consumo, consumo_maximo_definido)
            print(
                f"Alerta - Sensor: {sensor_name}, Consumo Atual: {consumo}, Consumo Máximo Definido: {consumo_maximo_definido}")
        elif msg.topic == TOPICO_CONSUMO:

            # Processar os dados recebidos no tópico de consumo
            consumo_data = json.loads(msg.payload.decode('utf-8').replace("'", '"'))
            consumo = consumo_data["consumo"]
            sensor_name = consumo_data["sensor"]

            # Adicionar os dados às listas globais
            timestamps.append(datetime.now())
            consumos.append(consumo)

            # Manter apenas os últimos 50 registros
            if len(consumos) > 50:
                consumos.pop(0)
                timestamps.pop(0)

            # Gerar gráfico
            plt.clf()  # Limpa o gráfico anterior
            plt.plot(timestamps, consumos, marker="o", linestyle="-", color="b")
            plt.title(f"Consumo de Energia - {sensor_name}")
            plt.xlabel("Tempo")
            plt.ylabel("Consumo (W)")
            plt.xticks(rotation=45)
            plt.tight_layout()  # Ajusta os espaçamentos para evitar sobreposição
            plt.pause(0.1)  # Atualiza o gráfico sem bloquear

            print(msg.payload.decode())
        else:
            print(f"Tópico não reconhecido: {msg.topic}")
    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")


# Função para conectar ao broker MQTT e assinar o tópico
def conectar_e_assinar():
    cliente = mqtt.Client()
    cliente.on_message = on_message
    cliente.connect(BROKER_IP, BROKER_PORT, 60)
    cliente.subscribe([(TOPICO_ALERTA, 0), (TOPICO_CONSUMO, 0)])
    cliente.loop_forever()


# Função para enviar o alerta por e-mail com os links de ligar e desligar
def enviar_alerta_email(sensor_name, consumo, consumo_maximo_definido):
    # Links de Ligar e Desligar
    link_ligar = "http://localhost:5000/ligar"
    link_desligar = "http://localhost:5000/desligar"

    mensagem = (f"Alerta! Consumo alto detectado\n"
                f"Nome: {sensor_name} \n"
                f"Consumo Atual: {consumo:.2f} W\n"
                f"Consumo Maximo definido: {consumo_maximo_definido} W\n\n"
                f"Controle de Dispositivo: \n"
                f"<a href='{link_ligar}'>Ligar Dispositivo</a>\n"
                f"<a href='{link_desligar}'>Desligar Dispositivo</a>\n")

    msg = email.message.Message()
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINATARIO
    msg['Subject'] = "Alerta de Consumo Elevado"
    msg.set_payload(mensagem)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        print(f"Alerta de consumo enviado para {EMAIL_DESTINATARIO} com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


# Endpoints Flask para ligar e desligar o dispositivo
@app.route("/ligar")
def ligar_dispositivo():
    p110.turnOn()  # Liga o dispositivo
    print("Dispositivo ligado via link de e-mail!")
    return "Dispositivo ligado com sucesso!"


@app.route("/desligar")
def desligar_dispositivo():
    p110.turnOff()  # Desliga o dispositivo
    print("Dispositivo desligado via link de e-mail!")
    return "Dispositivo desligado com sucesso!"


# Função para iniciar o monitoramento de consumo em uma thread separada
def monitorar_consumo():
    while True:
        publicar_consumo_mqtt()
        time.sleep(30)  # Intervalo de 30 segundos entre as publicações

# Função para iniciar o Flask em uma thread separada
def run_flask():
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)


if __name__ == "__main__":


    # Inicia a thread para monitoramento de consumo
    consumo_thread = threading.Thread(target=monitorar_consumo)
    consumo_thread.daemon = True  # Permite que a thread seja encerrada quando o programa terminar
    consumo_thread.start()

    # Inicia a thread para o servidor Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Inicia o consumidor MQTT
    conectar_e_assinar()
