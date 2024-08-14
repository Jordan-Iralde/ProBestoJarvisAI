print("inicio")
print("en este programa te solucionaremos la vida y te resolveremos los circuitos electricos bro")

def eleccion():
        try:

            tipo_circuito = input("ingrese que tipo de circuito quiere resolver(Mixto, Serie, Paralelo): ")
            
        except ValueError: 
            print("Verifique si la eleccion la escribio bien.")
        
        return tipo_circuito

def circuito_serie(): 
    try:
        voltaje = int(input("ingrese la cantidad de voltaje que tiene tu circuito: "))
        cantidad_resistencias = int(input("ingrese la cantidad de resistencias que tiene su circuito: "))
        resistencias = []
        for i in range(cantidad_resistencias):
            valor = float(input(f"ingrese el valor de R{i+1} en ohmios: "))
            resistencias.append(valor)
            
        RT = sum(resistencias)
        IT = voltaje / RT
        print(f"La Resistencia total del circuito es: {RT} Ohmios.\n")
        print(f"La Corriente total del circuito es de {IT} Amperes.\n ")
        print(f"El Voltaje total del circuito es de {voltaje} Volts.\n")
        return resistencias, valor, RT, IT, voltaje 
    except ValueError:
        print("Ingrese valores numericos :b")

def circuito_paralelo():
    try:
        voltaje_2 = int(input("ingrese la cantidad de voltaje que tiene tu circuito: "))
        cantidad_de_resistencias_2 = int(input("Ingrese la cantidad de resistencias: "))
        resistencias_2 = []
        
        for i in range(cantidad_de_resistencias_2):
            valor_2 = int(input(f"ingrese el valor de R{i+1}: "))
            resistencias_2.append(valor_2)

        suma_inversos = sum(1 / r for r in resistencias_2) 
        RT_2 = 1 / suma_inversos
       
        print(f"La resistencia total del circuito es de {RT_2} ohmios")
    except ValueError:
        print("ingrese un valor en numerico :b")


eleccion_valor = eleccion()



  
if eleccion_valor == 'paralelo' or eleccion_valor == 'Paralelo':
        circuito_paralelo()
elif eleccion_valor == 'serie' or  eleccion_valor ==  'Serie':
        circuito_serie()
        
        
        
        