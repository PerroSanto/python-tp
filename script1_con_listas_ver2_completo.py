import random
import threading
import time
import pylint

#Variables heladera
cantHeladeras = 10
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

    def cantidadLatasEnDeposito(self):
        return len(self.depositoLatas)
    
    def cantidadBotellasEnDeposito(self):
        return len(self.depositoBotellas)

    def depositarLatas(self,cantLatas):
        if cantLatas > 0:
            for i in range(cantLatas):
                self.depositoLatas.append(0)
    
    def depositarBotellas(self,cantBotellas):
        if cantBotellas > 0:
            for i in range(cantBotellas):
                self.depositoBotellas.append(0)
    
    def sacarLatasDelDeposito(self,unProveedor):
        if len(self.depositoLatas) > 0:
            cant =  self.cantidadLatasEnDeposito()
            self.depositoLatas[:] = []
            unProveedor.recargarCajonLatas(cant)
    
    def sacarBotellasDelDeposito(self,unProveedor):
        if len(self.depositoBotellas) > 0:
            cant = self.cantidadBotellasEnDeposito()
            self.depositoBotellas[:] = []
            unProveedor.recargarCajonBotellas(cant)
    

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

    def siPuede_MeterLata(self,unProveedor):
        if (self.hayEspacioContenedorLatas() and unProveedor.tengoLatas()):
            self.contenedorLatas.append(1)
            unProveedor.siPuede_SacarLata()

    def siPuede_MeterBotella(self,unProveedor):
        if (self.hayEspacioContenedorBotellas() and unProveedor.tengoBotellas()):
            self.contenedorBotellas.append(1)
            unProveedor.siPuede_SacarBotella()

    def estaLlena(self):
        return(not(self.hayEspacioContenedorLatas()) and not(self.hayEspacioContenedorBotellas()))

    def tieneLugar(self):
        return(self.hayEspacioContenedorLatas() or self.hayEspacioContenedorBotellas())
    
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

    def recargarCajonLatas(self, cantLatas):
        for i in range(cantLatas):
            self.cajonLatas.append(0) 

    def recargarCajonBotellas(self,cantBotellas):    
        for i in range(cantBotellas):
            self.cajonBotellas.append(0)
            
    def sinMecaderia(self):
        return(self.cajonBotellasVacio() and self.cajonLatasVacio())

    def recorridoHeladeras(self, indice = 0):
        heladera = listaDeHeladeras[indice]
        if heladera.tieneLugar():
            return heladera
        elif indice < (len(listaDeHeladeras) - 1):
            return self.recorridoHeladeras(indice + 1)

    def siPuede_SacarBotella(self):
        if self.tengoBotellas():
            self.cajonBotellas.remove(0)

    def siPuede_SacarLata(self):
        if self.tengoLatas():
            self.cajonLatas.remove(0)


    def mercaderiaIncorrectaBotellas(self, unaHeladera):
        return(self.tengoSoloBotellas() and unaHeladera.hayEspacioContenedorLatas() and not unaHeladera.faltanBotellas())

    def mercaderiaIncorrectaLatas(self,unaHeladera):
        return(self.tengoSoloLatas() and unaHeladera.hayEspacioContenedorBotellas() and not unaHeladera.faltanLatas())    
    
    def tengoSoloLatas(self):
        return(self.cajonBotellasVacio() and self.tengoLatas())
    
    def tengoSoloBotellas(self):
        return(self.cajonLatasVacio() and self.tengoBotellas())
    
    def tengoLatas(self):
        return(len(self.cajonLatas) > 0)

    def tengoBotellas(self):
        return(len(self.cajonBotellas) > 0)

    def cajonLatasVacio(self):
        return(len(self.cajonLatas) == 0)

    def cajonBotellasVacio(self):
        return(len(self.cajonBotellas) == 0)
    
    def impresionCargaHeladera(self,heladeraActual):
        print(self.name, ": Tengo", len(self.cajonLatas), "latitas y", len(self.cajonBotellas), 
            "botellas. Cargando:", heladeraActual.name, ": Tengo", len(heladeraActual.contenedorLatas), 
            "latitas y", len(heladeraActual.contenedorBotellas), "botellas")
        self.impresionSeparador()

    def impresionDeposito(self):
        print("Deposito:",Deposito().cantidadLatasEnDeposito(), "Lata/s",Deposito().cantidadBotellasEnDeposito(), "Botella/s")
        self.impresionSeparador()

    def impresionProveedor(self):
        print(self.name,": tengo", len(self.cajonLatas), "Latas y ", len(self.cajonBotellas), "Botellas")
        self.impresionSeparador()

    def impresionSeparador(self):
        print("--------------------------------------------------------------------------------------------------")

    def impresionEnchufar(self,heladeraActual):
        print(self.name,": Enchufando", heladeraActual.name)
        self.impresionSeparador()

    def impresionBotonFrio(self,heladeraActual):
        print(self.name,": Presionando boton frio", heladeraActual.name)
        self.impresionSeparador()


    def run(self):
        self.cargarCajones()
        semaforoProveedor.acquire() #el proveedor toma el semaforo de proveedores
        heladeraActual = self.recorridoHeladeras()
        while  not self.sinMecaderia() and heladeraActual != None: 
            self.impresionCargaHeladera(heladeraActual)
            
            Deposito().sacarBotellasDelDeposito(self)
            Deposito().sacarLatasDelDeposito(self)

            heladeraActual.siPuede_MeterBotella(self)
            heladeraActual.siPuede_MeterLata(self)
            tiempoEspera(2)
    
            if self.mercaderiaIncorrectaLatas(heladeraActual) or self.mercaderiaIncorrectaBotellas(heladeraActual):
                print(self.name,": Tengo mercaderia pero no es la correcta, la dejo en el deposito.")
                self.impresionSeparador()
                Deposito().depositarBotellas(len(self.cajonBotellas))
                Deposito().depositarLatas(len(self.cajonLatas))

                self.cajonLatas[:] = []
                self.cajonBotellas[:] = [] 
                self.impresionDeposito()
                tiempoEspera(2)  

            if heladeraActual.estaLlena():
                self.impresionCargaHeladera(heladeraActual)
                heladeraActual = self.recorridoHeladeras()
                self.impresionBotonFrio(heladeraActual)
                self.impresionEnchufar(heladeraActual)
                    
        else:
            print(self.name,": no tengo mas mercaderia o todas las heladeras estan llenas, me voy")
            self.impresionSeparador()
            semaforoProveedor.release()
            tiempoEspera(2)
            exit()
        



                    

#run

for i in range(1,cantHeladeras+1):
    nombre = 'Heladera' + str(i)
    listaDeHeladeras.append(Heladera(name=nombre))

for i in range(1,cantProveedores+1):
    latas = random.randint(1,20)
    botellas = random.randint(1,15)
    nombre = 'Proveedor ' + str(i)
    Proveedor(latas,botellas,nombre).start()