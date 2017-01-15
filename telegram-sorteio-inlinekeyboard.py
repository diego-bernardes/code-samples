import telebot
import sqlite3
from string import punctuation
import random

token = ''
bot = telebot.TeleBot(token, skip_pending = True)
chat_id= 
dados = 'base.db'
sql_consulta = '''
SELECT * FROM users
WHERE user_id = {user_id}'''
sql_select_ids = 'SELECT user_id FROM users'
sql_insert ='''
INSERT INTO users
VALUES({id_user},"{nome}", "@{username}")'''
sql_update = '''
UPDATE users
SET  nome = "{nome}", username = "{username}"
WHERE user_id = {id_user}'''

#CRIAR INLINE KEYBOARD
#keyboard = telebot.types.InlineKeyboardMarkup()
#btn = telebot.types.InlineKeyboardButton(text='Inscrição', callback_data='inscricao')
#keyboard.add(btn)
#bot.send_message(chat_id, 'Realize sua inscrição para o sorteio do livro', reply_markup=keyboard)

def sorteio():
    cadastrados = [i[0] for i in query(sql_select_ids)]
    ganhador = random.choice(cadastrados)
    try:
        user = bot.get_chat_member(chat_id, ganhador)
        if not 'left' in user.status and not 'kicked' in user.status:
            return([True,ganhador])
        else:
            return([False])
    except:
        return([False])
        
def query(sql,operacao = 'consulta'):
    try:
        db = sqlite3.connect(dados)
        db_cursor = db.cursor()
        if operacao == 'consulta':         
            resultado = db_cursor.execute(sql).fetchall()
            db_cursor.close()
            return(resultado)
        else:
            db_cursor.execute(sql)
            db.commit()
            db_cursor.close()
    except Exception as erro:
        log_erros('query', erro, sql)

def log_erros(func, erro, mensagem):
    try:
        with open('error.log', 'a') as logs:
            erro = '''

#Erro! Funcao {fun} {data}
Mensagem de erro:
{log_erro}
Mensagem que originou o erro:
{mensagem}
--------------------------------------------'''.format(fun = func, data = str(datetime.today()), log_erro = erro,
                                                       mensagem = mensagem)
        logs.write(erro)
        bot.send_message(-1001087248722, erro)
    except:
        pass
def remove_caracteres(texto):
    for caractere in punctuation: texto = texto.replace(caractere, ' ')
    return(texto)


def inscricao(mensagem):
    username = remove_caracteres(mensagem.from_user.username) if mensagem.from_user.username else 'sem_usuario'
    nome = remove_caracteres(mensagem.from_user.first_name)
    user_id = mensagem.from_user.id
    dados = query(sql_consulta.format(user_id=user_id))
    if not dados:
        query(sql_insert.format(id_user=user_id, nome=nome, username=username), operacao='cad')
    else:
        query(sql_update.format(id_user=user_id, nome=nome, username=username), operacao='up')
        
@bot.message_handler(commands=['cadastrados'])
def get_cadastrados(mensagem):
    list_admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
    if mensagem.from_user.id in list_admins:
        bot.reply_to(mensagem, len([i[0] for i in query(sql_select_ids)]))

@bot.message_handler(commands=['sortear'])
def get_cadastrados(mensagem):
    list_admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
    if mensagem.from_user.id in list_admins:
        while True:
            resultado = sorteio()
            if resultado[0] == True:
                bot.reply_to(mensagem, '''
Ganhador! 
Nome: {1}
Username: {2}
User_ID: {0}'''.format(*query(sql_consulta.format(user_id=resultado[1]))[0]))
                break
            else:
                bot.reply_to(mensagem, 'O usuário ganhador não está no grupo, irei realizar um novo sorteio')


        
@bot.callback_query_handler(func=lambda call: True)
def get_callback(mensagem):
    if mensagem.data == 'inscricao':
        inscricao(mensagem)
        
bot.polling()
