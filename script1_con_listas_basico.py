import random
import threading
import time
import pylint

#Variables heladera
cantHeladeras = 9
maximoLatas = 15
maximoBotellas = 10
listaDeHeladeras = []

#variables proveedores
cantProveedores = 15
semaforoProveedor = threading.Semaphore(1)

#tiempo de espera
def tiempoEspera(maximo):
    time.sleep(random.randrange(1,maximo))


class Deposito():
    depositoLatas = []
    depositoBotellas = []

    def cantidadLatas(self):
        return len(self.depositoLatas)
    
    def cantidadBotellas(self):
        return len(self.depositoBotellas)

    def depositarLatas(self,cantLatas,unProveedor):
        if cantLatas > 0:
            for i in range(cantLatas):
                self.depositoLatas.append(0)
            unProveedor.cajonLatas[:] = []
    
    def depositarBotellas(self,cantBotellas,unProveedor):
        if cantBotellas > 0:
            for i in range(cantBotellas):
                self.depositoBotellas.append(0)
            unProveedor.cajonBotellas[:] = []
    
    def sacarLataYPonerlaEn(self,unaHeladera):
        if len(self.depositoLatas) > 0:
            self.depositoLatas.remove(0)
            unaHeladera.contenedorLatas.append(0)
        else:
            print("Deposito: no hay mas latas")    


    def sacarBotellaYPonerlaEn(self,unaHeladera):
        if len(self.depositoBotellas) > 0:
            self.depositoBotellas.remove(0)
            unaHeladera.contenedorBotellas.append(0)
        else:
            print("Deposito: no hay mas botellas")  
    

class Heladera(threading.Thread):
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.contenedorLatas = []
        self.contenedorBotellas = []

    def hayEspacioContenedorLatas(self):
        return(len(self.contenedorLatas) < maximoLatas)

    def hayEspacioContenedorBotellas(self):
        return(len(self.contenedorBotellas) < maximoBotellas)

    def estaLlena(self):
        return(not(self.hayEspacioContenedorLatas()) and not(self.hayEspacioContenedorBotellas()))
    
    def faltanLatas(self):
        return(len(self.contenedorLatas) < maximoLatas)

    def faltanBotellas(self):
        return(len(self.contenedorBotellas) < maximoBotellas)
    

class Proveedor(threading.Thread):
    def __init__(self,latas,botellas,name):
        super().__init__()
        self.latas = latas
        self.botellas = botellas
        self.name = name
        self.cajonLatas = []
        self.cajonBotellas = []

    def cargarCajones(self):
        latasACargar = self.latas 
        for i in range(latasACargar):
            self.cajonLatas.append(0) 
        
        botellasACargar = self.botellas
        for i in range(botellasACargar):
            self.cajonBotellas.append(0) 

    def cantidadLatas(self):
        return len(self.cajonLatas)

    def cantidadBotellas(self):
        return len(self.cajonBotellas)        
            
    def sinMecaderia(self):
        return(self.cajonBotellasVacio() and self.cajonLatasVacio())

    def cajonLatasVacio(self):
        return(len(self.cajonLatas) == 0)

    def cajonBotellasVacio(self):
        return(len(self.cajonBotellas) == 0)
    
    def impresionDeposito(self):
        print("Deposito:",Deposito().cantidadLatas(), "Lata/s",Deposito().cantidadBotellas(), "Botella/s")
        self.impresionSeparador()

    def impresionProveedor(self):
        print(self.name,": tengo", len(self.cajonLatas), "Latas y ", len(self.cajonBotellas), "Botellas")
        self.impresionSeparador()

    def impresionSeparador(self):
        print("--------------------------------------------------------------------------------------------------")

    def run(self):
        self.cargarCajones()
        semaforoProveedor.acquire() #el proveedor toma el semaforo de proveedores
        while  not self.sinMecaderia():
            self.impresionProveedor() 
            Deposito().depositarLatas(self.cantidadLatas(),self)
            Deposito().depositarBotellas(self.cantidadBotellas(),self)
            self.impresionDeposito() 
            tiempoEspera(10)       
        else:
            print(self.name,": no tengo mas mercaderia, me voy")
            self.impresionSeparador()
            semaforoProveedor.release()
            tiempoEspera(2)
            exit()


class Empleado(threading.Thread):
    def __init__(self,name):
        super().__init__()
        self.name = name
    
    def recorridoHeladeras(self, indice = 0):
        heladera = listaDeHeladeras[indice]
        if not heladera.estaLlena():
            return heladera
        elif indice < (len(listaDeHeladeras) - 1):
            return self.recorridoHeladeras(indice + 1)

    def impresionCargaHeladera(self,heladeraActual):
        print(self.name, ": Tengo", Deposito().cantidadLatas(), "latitas y", Deposito().cantidadBotellas(), 
            "botellas. Cargando:", heladeraActual.name, ": Tengo", len(heladeraActual.contenedorLatas), 
            "latitas y", len(heladeraActual.contenedorBotellas), "botellas")
        self.impresionSeparador() 

    def impresionSeparador(self):
        print("--------------------------------------------------------------------------------------------------")

    def run(self):
        heladeraActual = self.recorridoHeladeras()
        while True:
            while heladeraActual != None and not heladeraActual.estaLlena():
                
                self.impresionCargaHeladera(heladeraActual)
                
                if heladeraActual.hayEspacioContenedorLatas():
                    Deposito().sacarLataYPonerlaEn(heladeraActual)
                
                if heladeraActual.hayEspacioContenedorBotellas():
                    Deposito().sacarBotellaYPonerlaEn(heladeraActual)
                
                self.impresionCargaHeladera(heladeraActual)
                time.sleep(1)

            heladeraActual = self.recorridoHeladeras()

            
#run
for i in range(1,cantHeladeras+1):
    nombre = 'Heladera' + str(i)
    listaDeHeladeras.append(Heladera(name=nombre))

for i in range(1,cantProveedores+1):
    latas = random.randint(1,20)
    botellas = random.randint(1,15)
    nombre = 'Proveedor ' + str(i)
    Proveedor(latas,botellas,nombre).start()

Empleado(name='Empleado1').start()