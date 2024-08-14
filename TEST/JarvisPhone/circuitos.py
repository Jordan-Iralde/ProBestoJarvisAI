print("inicio")
print("en este programa te solucionaremos la vida y te resolveremos los circuitos electricos bro")

tipo_circuito = str(input("ingrese que tipo de circuito quiere resolver(Mixto, Serie, Paralelo): "))

def circuito_serie(): 
    try:
        voltaje = int(input("ingrese la cantidad de voltaje que tiene tu circuito: "))
        cantidad_resistencias = int(input("ingrese la cantidadde resistencias que tiene su circuito: "))
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
        voltaje = int(input("ingrese la cantidad de voltaje que tiene tu circuito: "))
        cantidad_de_resistencias = int(input("Ingrese la cantidad de resistencias"))
        resistencias = []
        
        for i in range(cantidad_de_resistencias):
            valor = int(input(f"ingrese el valor de R{i+1}: "))
            resistencias.append(valor)

        suma_inversos = sum(1 / r for r in resistencias)
        RT = 1 / suma_inversos
        print(f"La resistencia total del circuito es de {RT} ohmios")
    except ValueError:
        print("ingrese un valor en numerico :b")




while True: 
    if tipo_circuito == "serie" or "Serie":
        circuito_serie()
        break
    elif tipo_circuito == "paralelo" or "Paralelo":
        circuito_paralelo()