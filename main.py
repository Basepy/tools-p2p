import telebot
import configbot
from threading import Thread
import datetime
import requests
import time
import qrcode
from PIL import Image
import crcmod
from telebot import types
from payload import Payload

import botoes
import gerarid

response = requests.get('https://api.telegram.org', timeout=35)
token_bot = configbot.bot_principal_token
perc_btccred = float(configbot.taxa_porcentagem / 100)
taxa_servico = configbot.taxa_servico_config
parcelas = configbot.parcelas_config
acrescimo_price = configbot.spread_cotacao
par01 = "BTCBRL"



bot = telebot.TeleBot(token_bot)


# Comando /start
@bot.message_handler(commands=['start'])
def handle_pix_command(message):

    mensagem_resposta = f"*Bem-vindo, escolha uma das opções abaixo!*\n\n"
    mensagem_resposta += f"• *[BTC]* - Faça uma simulação de preço.\n"
    mensagem_resposta += f"• *[Fees]* - Veja a taxa estimada da rede Bitcoin\n"
    mensagem_resposta += f"• *[Informações]* - Veja as nossas informações principais\n"
    mensagem_resposta += f"• *[Empréstimo]* - Simule um empréstimo colateralizado em BTC\n"
        
    bot.send_message(message.chat.id,
                    mensagem_resposta,
                    parse_mode="Markdown",
                    reply_markup=botoes.menu_01())
        
# Função para responder a qualquer mensagem recebida com uma mensagem padrão
@bot.message_handler(func=lambda message: True)
def responder_mensagem_padrao(message):
    mensagem_resposta = f"*Bem-vindo, escolha uma das opções abaixo!*\n\n"
    mensagem_resposta += f"• *[BTC]* - Faça uma simulação de preço.\n"
    mensagem_resposta += f"• *[Fees]* - Veja a taxa estimada da rede Bitcoin\n"
    mensagem_resposta += f"• *[Informações]* - Veja as nossas informações principais\n"
    mensagem_resposta += f"• *[Empréstimo]* - Simule um empréstimo colateralizado em BTC\n"
    bot.send_message(message.chat.id,
                     mensagem_resposta,
                     parse_mode="Markdown",
                     reply_markup=botoes.menu_01())
    
    
    
@bot.callback_query_handler(func=lambda call: call.data == 'btn_btc')
def btn_chamar_pricebtc(call):
    ask_for_value(call.message)

def ask_for_value(mensagem):
    mensagem00 = f'💯 *Informe um valor que deseja comprar em BRL e a taxa %.*\n'
    mensagem00 += f'*Ex:* _100.99 10_\n'
    bot.send_message(mensagem.chat.id,
                    mensagem00,
                    parse_mode="Markdown")

    # Utilize 'mensagem' diretamente ao invés de 'mensagem.chat' para acessar as informações corretas.
    bot.register_next_step_handler(mensagem, lambda msg: responder_BTC(msg, mensagem.chat.id, mensagem.chat.username))

def responder_BTC(mensagem, user_id, username):
    try:
        a, b = mensagem.text.split()
        valor_compra = float(a)
        taxa_perc = float(b)

        if not b.replace('.', '').isdigit():
            # 'isdigit()' não permite pontos decimais, por isso, removemos os pontos e verificamos se é numérico.
            raise ValueError()

        if taxa_perc < 0:
            # Se a taxa for negativa, levanta um erro para tratamento.
            raise ValueError()

        url = f"https://www.binance.com/api/v3/ticker/price?symbol={par01}"
        requisicao = requests.get(url)

        if requisicao.status_code == 200:
            resposta = requisicao.json()
            data = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            cotacao01 = float(resposta["price"])

            # O cálculo da cotação P2P estava incorreto, substituí pelo valor correto.
            price_compra = cotacao01 + (cotacao01 * configbot.spread_cotacao_p2p / 100)
            comprar = valor_compra - (valor_compra * taxa_perc / 100)
            quantidade = comprar / price_compra
            taxa_plataforma_brl = valor_compra - comprar
            p2p_receive = (taxa_plataforma_brl - (taxa_plataforma_brl - (taxa_plataforma_brl * configbot.PERC_P2P_RECEIVE / 100)) )
            received = taxa_plataforma_brl - p2p_receive
            taxas_totais = received + p2p_receive

            nome_pix = "Kawan Andrade De Souza Dias"
            chave_pix = "f82bd1dc-99bc-4eb5-9def-4f11f520cea0"


            valor_convert = f"{received:.2f}"
            cidade = 'Bitcity'
            identificador = f"{gerarid.gerar_identificador()}"
            valorstr = str(valor_convert)
            pay = Payload(nome_pix, chave_pix, valorstr, cidade, identificador)
            pay.gerarPayload()

            pay.gerarCrc16(pay.payload)
           

            mensagem_resposta = "   🟢    *Dados da consulta*   🟢   \n\n\n"
            mensagem_resposta += f"• *Consultor:* _@{username}_\n"
            mensagem_resposta += f"• *Cotação MMK:* R$ `{cotacao01:.2f}`\n"
            mensagem_resposta += f"• *Cotação casa:* R$ `{price_compra:.2f}`\n"
            mensagem_resposta += f"• *Valor de compra R$:* `{valor_compra:.2f}`\n"
            mensagem_resposta += f"• *Taxa plataforma R$:* `{received:.2f}`\n"
            mensagem_resposta += f"• *P2P receive R$:* `{p2p_receive:.2f}`\n"
            mensagem_resposta += f"• *Taxas totais:* `{taxas_totais:.2f}`\n"
            mensagem_resposta += f"• *Total a Comprar R$:* `{comprar:.2f}`\n"
            mensagem_resposta += f"• *Qtd. BTC:* `{quantidade:.8f}`\n"
            mensagem_resposta += f"• *Taxa P2P %:* `{taxa_perc:.2f}`\n"
            mensagem_resposta += f"• *Data:* `{data}`\n"
            mensagem_resposta += f"• *ID:* `{identificador}`\n\n"
            mensagem_resposta += f"• _Endereço de PIX para enviar os fundos:_"
            mensagem_resposta += f"`{pay.payload_completa}`\n\n"
            mensagem_resposta += f"• *Para fazer uma nova consulta, clique em um dos botões abaixo!*"

            # Utilize 'user_id' ao invés de 'mensagem.chat.id', pois 'mensagem' agora é uma Message, não um Chat.
            bot.send_message(mensagem.chat.id,
                         mensagem_resposta,
                         parse_mode="Markdown",
                         reply_markup=botoes.menu_01())
            
            MSG = f"*ORDEM P2P GERADA* - Dados para acompanhar\n\n"
            MSG += f"• *Consultor:* _@{username}_\n"
            MSG += f"• *Cotação MMK:* R$ `{cotacao01:.2f}`\n"
            MSG += f"• *Cotação casa:* R$ `{price_compra:.2f}`\n"
            MSG += f"• *Valor de compra R$:* `{valor_compra:.2f}`\n"
            MSG += f"• *Taxa plataforma R$:* `{received:.2f}`\n"
            MSG += f"• *P2P receive R$:* `{p2p_receive:.2f}`\n"
            MSG += f"• *Taxas totais:* `{taxas_totais:.2f}`\n"
            MSG += f"• *Total a Comprar R$:* `{comprar:.2f}`\n"
            MSG += f"• *Qtd. BTC:* `{quantidade:.8f}`\n"
            MSG += f"• *Taxa P2P %:* `{taxa_perc:.2f}`\n"
            MSG += f"• *Data:* `{data}`\n"
            MSG += f"• *ID:* `{identificador}`\n\n"
            MSG += f"• _Endereço de PIX de destino:_\n"
            MSG += f"`{pay.payload_completa}`\n\n"
            MSG += f"• *Conta:* `{nome_pix}`\n"
            MSG += f"• *Chave PIX:* `{chave_pix}`\n"

            bot.send_message(configbot.ID_GRUPO,
                         MSG,
                         parse_mode="Markdown")


        else:
            bot.send_message(mensagem.chat.id,
                         "*🚫 Desculpe-me, não consegui acessa a API*",
                         parse_mode="Markdown",
                         reply_markup=botoes.menu_01())

    except ValueError:
        bot.send_message(user_id,
                         "\nValor inválido!\n\n✅ Forma correta ex: R$ 10.00\n- Exemplos: 10 | 10.00 | 10.50\n\n❌ Forra errada ex: R$ 10,00\n- Exemplos: 10,00 | 10,50 \n\n👉🏼 Clique em um dos botões para recomeçar\n",
                         parse_mode="Markdown",
                         reply_markup=botoes.menu_01())






bot.polling(non_stop=True)
    