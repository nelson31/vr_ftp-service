#!/usr/bin/python3

"""
Aplicacao que simula um servidor FTP em Python que sera usado como um microservico
em containers Docker

Copyright (c) 2021 Universidade do Minho
Perfil GVR - Virtualizacao de Redes 2020/21
Desenvolvido por: Nelson Faria (a84727@alunos.uminho.pt)
"""

from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
#from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.authorizers import AuthenticationFailed
from pyftpdlib.servers import MultiprocessFTPServer
import sys, requests, json, jwt


# Path para a pasta de uploads
UPDIRECTORY = "/usr/src/ftp/"


'''
Fazer o decoding de um token, retornando o nome do user e o seu papel
'''
def decode_token(enctoken):

    try:
        payload = jwt.decode(enctoken, 
            options={"verify_signature": False}, 
            algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


'''
Classe que serve para definir as politicas de autorizacao do servidor ftp
'''
class MyAuthorizer(DummyAuthorizer):

	def validate_authentication(self, username, password, handler):

		#Testa se o user é valido com o auth server
		payload = {'username': username, 'password': password}
		try:
			# Verificar se existe
			x = requests.post('http://auth_container:5000/loginFTP', data=json.dumps(payload))
			if x.status_code == requests.codes.ok:
				f = open("logs.txt", "w")
				f.write("\n")
				f.write(x.text)
				f.write("\n")
				f.close()
				# Descodificar o token
				token_dec = decode_token(x.text)
				valid = True
			else:
				valid = False
		except Exception as e:
			valid = False

		# Verificar se existe
		x = requests.post('http://auth_container:5000/loginFTP', data=json.dumps(payload))
		if x.status_code == requests.codes.ok:
			f = open("logs.txt", "w")
			f.write("\n")
			f.write(x.text)
			f.write("\n")
			f.close()
			# Descodificar o token
			token_dec = decode_token(x.text)
			valid = True
		else:
			valid = False
		# Se for valido
		if valid:
			# adiciona um novo user/admin (perm é usado para definir as permissoes)
			if token_dec["role"] == "admin":
				self.add_user(username, '.', UPDIRECTORY, perm='elradfmwM')
			else:
				# So tem permissoes de leitura
				self.add_user(username, '.', UPDIRECTORY, perm='elr')
			#return True
		else:
			raise AuthenticationFailed("Invalid Token")
			return False


'''
Classe que serve para definir o Handler para o FTP server
'''
class MyHandler(FTPHandler):

	def on_disconnect(self):

		#remove user on disconect as token may no longer be valid
		if authorizer.has_user(self.username):
			print("removing user: "+self.username)
			authorizer.remove_user(self.username)


'''
Configuracoes especiais para o handler FTP como a autenticacao
'''
def configHandler():

	# Objeto responsavel pela autenticação dos utilizadores e suas respectivas permissoes
	authorizer = MyAuthorizer()
	print("Local de acesso do servidor : \n  " + UPDIRECTORY + '\n')
	# Usado para permitir conexoes externas
	MyHandler.permit_foreign_addresses = True

	# objeto que manipula os comandos enviados pelo cliente FTP
	handler = MyHandler
	# Responsavel pela autenticacao do servidor
	handler.authorizer = authorizer

	return handler


def main(arg):
	
	handler = configHandler()
	# porta padrão do servidor
	porta = 2121
	# ip onde o servidor estara a escuta de conexoes
	if len(arg) == 1:
		ip = "0.0.0.0"
	else:
		ip = arg[1]
	
	# servidor
	server = MultiprocessFTPServer((ip,porta),handler)
	#inicia o servidor
	server.serve_forever()



if __name__ == '__main__':
	main(sys.argv)

