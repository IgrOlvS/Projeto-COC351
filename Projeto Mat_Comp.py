#!/usr/bin/env python
# coding: utf-8

# In[6]:


# definindo a representação binaria
def bin_64(num):
    tipo = type(num) 
    if tipo == 'str':
        num = ord(num)
        
    num = format(num,'064b')
    return num

# polinomio de grau 3
def f(coef, x):
    return coef[0]*x**3 + coef[1]*x**2 + coef[2]*x + coef[3]

# derivada do polinomio
def df(coef, x):
    return 3*coef[0]*x**2 + 2*coef[1]*x + coef[2]

# funcao para gerar os coeficientes e raizes
def roots_gen():
    
    # possiveis valores para as raizes, excluindo 0 (399 possibilidades)
    nums = []
    for a in range(-10,11):
        for b in range(-10,11):
            nums.append(complex(a,b))
    nums.remove(0.0)
    
    # guardar as combinações de coeficientes e raizes geradas
    comb = {}
    
    # obtem os coeficientes e raizes de forma iterativa 
    for x1 in nums:
        for x2 in nums:
            for x3 in nums:
                a1 = 1
                a2 = -(x1+x2+x3)
                a3 = x1*x2 + x2*x3 + x1*x3
                a4 = -(x1*x2*x3)

                coefs = (a1,a2,a3,a4)
                roots = [x1,x2,x3]

                y_pos = 0
                d_sinal = 0
                c_img = 0
                
                # garante que a imagem da funcao seja positiva para o dominio [0,255]
                for x in range(256):
                    if f(coefs, x).real >= 0:
                        y_pos += 1
                        
                # garante que a funcao seja injetora entre 0 e 255, derivada nao muda de sinal nesse intervalo
                for x in range(256):
                    if df(coefs,x).real > 0:
                        d_sinal += 0
                    if df(coefs,x).real == 0:
                        break
                
                # garante que os coeficientes sejam reais, mesmo com raízes complexas
                for coef in coefs:
                    if coef.imag == 0:
                        c_img += 1

                # Aplicando os testes
                if (y_pos == 256) and (c_img == 4) and (d_sinal == 0 or d_sinal == 256):
                    comb[coefs] = roots 
                    return comb
    
    return print('Nenhuma combinação encontrada')


# gerando as chaves publica e privada    
def keys_gen():
    
    # organizando a lista com as combinações
    comb = roots_gen()
    lista_comb = []
    for coef, roots in comb.items():
        lista_comb.append(coef)
        lista_comb.append(roots)
    
    c = lista_comb[0]
    x = lista_comb[1]
    
    # definindo a chave publica
    def public_key(x):
        px = c[0]*x**3 + c[1]*x**2 + c[2]*x + c[3]
        return px
    
    # definindo a chave privada
    def private_key(px):
        x_temp = 0
        px_temp = 0
        while px_temp.real < px:
            px_temp = (x_temp - x[0]) * (x_temp - x[1]) * (x_temp - x[2])   # utiliza as raizes para encontrar a "raiz"
            x_temp += 1                                                     # de forma rapida e com poucas operacoes
            
        return x_temp-1
    
    print(f'Chave Pública: x³+{int(c[1].real)}x²+{int(c[2].real)}x+{int(c[3].real)}')
        
    return public_key, private_key

# definindo o algoritmo para encriptar
def encrypt(public_key, data_decrypted):
    hash_ = []
    for i in range(len(data_decrypted)):            # cada caractere sera codificado separadamente
        encrypted_num = int(public_key(ord(data_decrypted[i])).real)    # transforma em decimal inteiro
        bin_ = bin_64(encrypted_num)                                    # transforma em binario
        size= 8                                    
        for j in range(size):                       # codificado de 8 em 8 bits
            int_ = int(bin_[j*8:(j+1)*8],2)         # re-transforma o os 8 bits separados em um novo inteiro
            hash_.append(chr(int_))                 # transforma esse inteiro em um novo caractere
    hash_ = "".join(hash_)                          # repetindo 8x, obtem-se a hash 1 pra 8
    return hash_

# definindo o algoritmo para decriptar
def decrypt(private_key,data_encrypted):
    text = []
    size = int(len(data_encrypted)/8)               # cada 8 caracteres gerarao 1 
    for i in range(size):
        bin_temp = []
        for j in range(8):
            dec = ord(data_encrypted[j+8*i])        # transforma cada caractere em um decimal
            bin_ = format(dec,'08b')                # transforma o decimal em binario 8 bits
            bin_temp.append(bin_)                   # junta os 8 binarios 8 bits para formar um 64 bits
        bin_full = "".join(bin_temp)
        int_ = int(bin_full,2)                      # re-transforma o binario 64 bits em um numero inteiro
        data_decrypted = private_key(int_)          # aplica a chave privada
        text.append(chr(data_decrypted))            # para obter o inteiro equivalente ao caractere original
    text = "".join(text)                            # cada caractere ira recompor o texto
                
    return text

# método de newton-raphson
def newton(coef, x0, tol, max_iter):
    x = x0
    for i in range(max_iter):
        fx = f(coef,x)
        if abs(fx) < tol:
            return x
        dfx = df(coef,x)
        if dfx == 0:
            return print('Derivada igual a zero')
        x = x - fx / dfx
    return print(f'Não foi encontrada raiz para {max_iter} iterações')

# algoritmo de decriptacao adaptado para o metodo de newton
def decrypt_newton(coef,x0,tol,max_iter,data_encrypted):
    text = []
    size = int(len(data_encrypted)/8)   # cada 8 caracteres gerarao 1 
    c3 = coef[3]
    for i in range(size):
        coef[3] = c3
        bin_temp = []
        for j in range(8):
            dec = ord(data_encrypted[j+8*i])        # transforma cada caractere em um decimal
            bin_ = format(dec,'08b')                # transforma o decimal em binario 8 bits
            bin_temp.append(bin_)                   # junta os 8 binarios 8 bits para formar um 64 bits
        bin_full = "".join(bin_temp)
        int_ = int(bin_full,2)                      # re-transforma o binario 64 bits em um numero inteiro
        coef[3] -= int_                             # P(x) - M = 0
        
        data_decrypted = int(newton(coef, x0, tol, max_iter))                    # aplica o método de newton
        
        text.append(chr(data_decrypted))            # para obter o inteiro equivalente ao caractere original
    text = "".join(text)                            # cada caractere ira recompor o texto
                
    
    return text

# metodo da bisseccao
def bisseccao(coef, a, b, tol):
    if f(coef, a) * f(coef, b) >= 0:
        print("O método da bissecção não pode ser aplicado.")
        return None
    c = a
    while abs((b - a)) / 2.0 > tol:
        c = (a + b) / 2.0
        if f(coef,c) == 0:
            break
        elif f(coef,a) * f(coef,c) < 0:
            b = c
        else:
            a = c
    return c

# algoritmo de decriptacao adaptado para o metodo da bisseccao
def decrypt_bisseccao(coef,a,b,tol,data_encrypted):
    text = []
    size = int(len(data_encrypted)/8)               # cada 8 caracteres gerarao 1 
    c3 = coef[3]
    for i in range(size):
        coef[3] = c3
        bin_temp = []
        for j in range(8):
            dec = ord(data_encrypted[j+8*i])        # transforma cada caractere em um decimal
            bin_ = format(dec,'08b')                # transforma o decimal em binario 8 bits
            bin_temp.append(bin_)                   # junta os 8 binarios 8 bits para formar um 64 bits
        bin_full = "".join(bin_temp)
        int_ = int(bin_full,2)                      # re-transforma o binario 64 bits em um numero inteiro
        coef[3] -= int_                             # P(x) - M = 0
        
        data_decrypted = int(round(bisseccao(coef, a, b, tol)))               # aplica o método da bisseccao
        
        text.append(chr(data_decrypted))            # para obter o inteiro equivalente ao caractere original
    text = "".join(text)                            # cada caractere ira recompor o texto
                
    
    return text

public_key, private_key = keys_gen()

#with open('caminho\\do\\arquivo.txt', 'r') as arquivo:         # inserir caminho do arquivo txt
    # Le o conteudo do arquivo
conteudo = 'Encha seus olhos de admiracao. Viva como se fosse cair morto daqui a dez segundos. Veja o mundo. Ele e mais fantastico do que qualquer sonho que se possa produzir nas fabricas. Nao peca garantias, nao peca seguranca, jamais houve semelhante animal. E se houvesse, seria parente do grande bicho-preguica pendurado de cabeca para baixo numa arvore o dia inteiro, todos os dias, a vida inteira dormindo. Para o inferno com isso. Balance a arvore e derrube o grande bicho-preguica de bunda no chao.'#arquivo.read()

M = conteudo
print('\nMensagem original\n')
print(M)

data_encrypted = encrypt(public_key, M)
print('\nMensagem crirptografada\n')
print(data_encrypted)

data_decrypted = decrypt(private_key,data_encrypted)
print('\nMensagem descriptografada\n')
print(data_decrypted)

coef = [1,30,400,2000]                              # coeficientes do polinomio conhecido
x0 = 5
tol = 10**(-6)
max_iter = 100

data_decrypted = decrypt_newton(coef,x0,tol,max_iter,data_encrypted)
print('\nMensagem descriptografada por newton\n')
print(data_decrypted)

coef = [1,30,400,2000]                              # coeficientes do polinomio conhecido
# Intervalo [a, b] e tolerância
a =  300
b = -300
tol = 10**(-6)

data_decrypted = decrypt_bisseccao(coef,a,b,tol,data_encrypted)
print('\nMensagem descriptografada por bisseccao\n')
print(data_decrypted)


# In[ ]:




