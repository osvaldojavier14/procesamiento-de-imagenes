import math, random

class Procesamiento:
	def __init__(self, pixeles, ancho, alto):
		self.pixeles = pixeles
		self.ancho = ancho
		self.alto = alto
		self.MINN = 1000
		self.MAXN = 1

	def convertirGris(self):
		print "conviertiendo a grises"
		imagenGris = list()
		# recorremos la lista de bites para modificarlos  
		for bite in self.pixeles:
			# agregamos a la "nueva" imagen
			imagenGris.append((max(bite), max(bite), max(bite)))  
		print "listo"
		return imagenGris

	def aplicarFiltro(self):
		print "aplicando filtro"
		imagenFiltrada = list()
	 
		for indice in range(len(self.pixeles)):
			vecinosCruz = calcularVecinosCruz(self.pixeles, indice, self.ancho)
			nuevoPixel = max(vecinosCruz)
			imagenFiltrada.append((nuevoPixel, nuevoPixel, nuevoPixel))
		print "listo"
		return imagenFiltrada

	def aplicarConvolucion(self):
		print "aplicando convolucion"
		imagenConvolucion = list()
		(mascaraX, mascaraY) = sobel()

		for indice in range(len(self.pixeles)):
			# sacamos los vecinos en cruz = (vecinoIzq, vecinoDer, vecinoAbajo, vecinoArriba)
			vecinosCruz = calcularVecinosCruz(self.pixeles, indice, self.ancho)
			# sacamos los vecinos en diagonal = (vecinoIzqArriba, vecinoDerArriba, vecinoIzqAbajo, vecinoDerAbajo) 
			vecinosDiagonales = calcularVecinosDiagonales(self.pixeles, indice, self.ancho)
			# sumamos todos los vecinos
			vecinosTotales = vecinosCruz + vecinosDiagonales
			# y ordenamos para multiplicar por la mascara centralizada
			vecinosOrdenados = ordenarVecinos(vecinosTotales, self.pixeles[indice])

			sumaX = 0
			sumaY = 0
			# multiplicaciones de matrices
			for i in range(len(vecinosOrdenados)):

				sumaX = (vecinosOrdenados[i] * mascaraX[i]) + sumaX
				sumaY = (vecinosOrdenados[i] * mascaraY[i]) + sumaY

				# Forma 1
				nuevoPixel = int(math.sqrt((sumaX ** 2) + (sumaY ** 2)))
				# Forma 2
				#nuevoPixel = sumaX + sumaY

			imagenConvolucion.append((nuevoPixel, nuevoPixel, nuevoPixel))

			if nuevoPixel < self.MINN:
				self.MINN = nuevoPixel
			if nuevoPixel > self.MAXN:
				self.MAXN = nuevoPixel
		print "listo"
		return (imagenConvolucion)

	def aplicarNormalizacion(self, imagenConvolucion):
		print "aplicando normalizacion"
		imagenNormalizada = list()
		rango = self.MAXN - self.MINN
		prop = 255.0 / rango
		for pixelActual in imagenConvolucion:
			nuevoPixel = int(math.floor((max(pixelActual) - self.MINN) * prop))
			imagenNormalizada.append((nuevoPixel, nuevoPixel, nuevoPixel))
		print "listo"
		return imagenNormalizada

	def aplicarBinarizacion(self, imagenConvolucion, RANGO_BINARIZACION):
		print "aplicar binarizacion"
		imagenBinarizada = list()
		pixelesVisitar = {}
		for indice, pixelActual in enumerate(imagenConvolucion):
			if min(pixelActual) > RANGO_BINARIZACION:
				pixelActual = 255 # pixel a blanco
				pixelesVisitar[indice] = (255,255,255) # los bordes no los tomamos en cuenta
			else:
				pixelActual = 0 # pixel a Negro
				pixelesVisitar[indice] = (0,0,0) # agregamos al dict pero aun no este visitado
			imagenBinarizada.append((pixelActual, pixelActual, pixelActual))
		print "listo"
		return(imagenBinarizada, pixelesVisitar)

	def buscarObjetos(self, imagenBinarizada, pixelesVisitar):
		print "buscando objetos...."
		imagenObjetos = list() 
		pixelesCola = {} # lista de los pixeles candidatos
		objetosDetectados = 0 # objetos totales en la imagen
		etiquetas = list()

		negros = (0,0,0)
		ultimoValor = 0 # un contador para no buscar siempre desde la posicion 0


		while negros in pixelesVisitar.values():
			# agregamos un nuevo elemento en la cola
			for valor in (range(ultimoValor, len(pixelesVisitar))):
				if negros == pixelesVisitar[valor]:
					nuevoColor = random.randrange(0,255)
					nuevoColor2 = random.randrange(0,255)
					nuevoColor3 = random.randrange(0,255)
					pixelesCola[valor] = ((nuevoColor, nuevoColor2, nuevoColor3))
					ultimoValor += 1
					pixelesObjeto = {}
					objetosDetectados += 1
					pixelesUsados = 1
					break # ya encontramos uno
				ultimoValor += 1

			while pixelesCola > 0:
				try:
					pixelActual = pixelesCola.keys()[0]
				except:
					break
				# calculamos vecinos para el pixel actual
				vecinos = {}
				vecinos = vecinosCruz(imagenBinarizada, pixelActual, self.ancho)
				valores = vecinos.items()
				for i in range(len(vecinos)): # recorremos la vecindad
					# si hay negros en la lista de vecinosVisitar y no esta en la cola
					# y no es borde = agregamos
					try:
						if (negros == pixelesVisitar[valores[i][0]] and \
									not pixelesCola.has_key(valores[i][0]) and \
										(valores[i][1] != 255)):
							pixelesCola[valores[i][0]] = \
								((nuevoColor, nuevoColor2, nuevoColor3)) #agregamos a la cola	
							pixelesVisitar[valores[i][0]] = \
								((nuevoColor, nuevoColor2, nuevoColor3))						
					except:
						pass # No existe el vecino a insertar

				pixelesUsados += 1
				pixelesVisitar[pixelActual] = ((nuevoColor, nuevoColor2, nuevoColor3))
				pixelesObjeto[pixelActual] = ((nuevoColor, nuevoColor2, nuevoColor3))
				del pixelesCola[pixelActual] # y los eliminamos de la cola
			dimension = (pixelesUsados * 100.0) / len(pixelesVisitar)
			if objetosDetectados == 1:
				print "dimension para el objeto 1(fondo) = ", dimension, "%"
			else:
				print "dimension para el objeto", objetosDetectados, "=", dimension, "%"
			centroMasa = pixelesObjeto.keys()[len(pixelesObjeto.keys()) / 2: len(pixelesObjeto.keys()) / 2 + 1]
			centroMasa = centroMasa.pop()
			etiquetas.append(centroMasa)
			pixelesVisitar[centroMasa] = ((1, 1, 1))


		# armamos la imagen
		for i in pixelesVisitar.values():
			imagenObjetos.append(i)

		print "listo"
		return(imagenObjetos, etiquetas)

	def detectarLineas(self):
		print "Detectando lineas..."
		imagenLineas = list()

		imagenConvolucion = list()
		(mascaraX, mascaraY) = sobel()

		CERO = 0.00001
		largoMatriz = self.alto
		x = -1
		y = 0
		datos = list()
		seleccionados = dict()

		for indice in range(len(self.pixeles)):
			if x <= largoMatriz:
				x += 1
			else:
				x = 0
				y += 1
				largoMatriz += self.alto
			
			# sacamos los vecinos en cruz = (vecinoIzq, vecinoDer, vecinoAbajo, vecinoArriba)
			vecinosCruz = calcularVecinosCruz(self.pixeles, indice, self.ancho)
			# sacamos los vecinos en diagonal = (vecinoIzqArriba, vecinoDerArriba, vecinoIzqAbajo, vecinoDerAbajo) 
			vecinosDiagonales = calcularVecinosDiagonales(self.pixeles, indice, self.ancho)
			# sumamos todos los vecinos
			vecinosTotales = vecinosCruz + vecinosDiagonales
			# y ordenamos para multiplicar por la mascara centralizada
			vecinosOrdenados = ordenarVecinos(vecinosTotales, self.pixeles[indice])

			gx = 0 # reiniciamos
			gy = 0 # reiniciamos
			# multiplicaciones de matrices
			for i in range(len(vecinosOrdenados)):
				gx = (vecinosOrdenados[i] * mascaraX[i]) + gx 
				gy = (vecinosOrdenados[i] * mascaraY[i]) + gy

			if math.fabs(gx) > CERO:
				angulo = math.atan(gy / gx)

				print math.degrees(angulo)
				raw_input()
			else: 
				if math.fabs(gx) + math.fabs(gy) < CERO:
					angulo = None # aqui no hay nada en ninguna direccion
				elif math.fabs(gy - gx) < CERO: # casi iguales
					angulo = math.atan(1.0)
				elif gx * gy > 0.0: # mismo signo
					angulo = math.pi 
				else: # negativo -> -pi
					angulo = 0.0
			# eje vertical volteado y origen al centro
			if angulo is not None:
				#seleccionados.append(indice)
				 #asegurar que este entre cero y pi (0 y 180)
				while angulo < CERO:
					angulo += math.pi
				while angulo > math.pi:
					angulo -= math.pi
				rho = (x - self.ancho/2) * math.cos(angulo) + (self.alto/2 - y) * \
																math.sin(angulo) # RELEVANTE
				angulo = (int(180 * (angulo / math.pi)) / 18) # hay que discretizar - RELEVANTE
				seleccionados[rho, angulo] = indice
				datos.append((rho, angulo, indice)) 
			else:
				seleccionados[None, None] = indice
				datos.append((None, None, indice))

		comb = dict()
		# recorre todo los resultados arrojados por los pixeles y suma los frecuentes
		for i in range(len(self.pixeles)):
			if i == datos[i][2]:
				(rho, angulo) = datos[i][:2]
			combinacion = (rho, angulo)
			if combinacion in comb:
				comb[combinacion] += 1
			else:
				comb[combinacion] = 1

		incluir = 0.7

		frec = frecuentes(comb, int(math.ceil(len(comb) * incluir))) # RELEVANTE

		pixelesPintar = list()
		for i in frec:
			if seleccionados.has_key(i):
				pixelesPintar.append(seleccionados[i])

		pixelesPintar.sort()

		#armar la imagen
		sig = 0
		for i in range(len(self.pixeles)):
			try:
				if i == pixelesPintar[sig]:
					sig += 1
					imagenLineas.append((255, 0, 0))
				else:
					pixelNormal = self.pixeles[i] 
					imagenLineas.append(pixelNormal)
			except:
				pass # no existe borde en este pixel
		print "listo"
		return imagenLineas


def frecuentes(histo, cantidad):
    frec = list()
    for valor in histo:
        if valor is None:
            continue
        frecuencia = histo[valor]
        acepta = False
        if len(frec) <= cantidad:
            acepta = True
        if not acepta:
            for (v, f) in frec:
                if frecuencia > f:
                    acepta = True
                    break
        if acepta:
            frec.append((valor, frecuencia))
            frec = sorted(frec, key = lambda tupla: tupla[1])
            if len(frec) > cantidad:
                frec.pop(0)
    incluidos = list()

    for (valor, frecuencia) in frec:
        incluidos.append(valor)
        #print frecuencia
    return incluidos

def sobel(): 
	return([-1, 0, 1, -2, 0, 2, -1, 0, 1], \
		[1, 2, 1, 0, 0, 0, -1, -2, -1])

def prewiit():
	return([-1, 0, 1, -1, 0, 1, -1, 0, 1], \
	 	[1, 1, 1, 0, 0, 0, -1, -1, -1])

def vecinosCruz(pixeles, pixelActual, ancho):
	vecinos = {}
	# izquierdo
	try:
		vecinos[pixelActual - 1] = pixeles[pixelActual - 1]
	except:
		#print "E"
		vecinos[pixelActual - 1] = 0
	# derecho
	try:
		vecinos[pixelActual + 1] = pixeles[pixelActual + 1]
	except:
		#print "E2"
		vecinos[pixelActual + 1] = 0
	# arriba
	try:
		#print "E3"
		vecinos[pixelActual - ancho] = pixeles[pixelActual - ancho]
	except:
		vecinos[pixelActual - ancho] = 0
	# abajo
	try:
		#print "E4"
		vecinos[pixelActual + ancho] = pixeles[pixelActual + ancho]
	except:
		vecinos[pixelActual + ancho] = 0
	return vecinos

def calcularVecinosCruz(pixeles, pixelActual, ancho):
	# izquierdo
	try:
		vecinoIz = max(pixeles[pixelActual - 1])
	except:
		vecinoIz = 0
	# derecho
	try:
		vecinoDe = max(pixeles[pixelActual + 1])
	except:
		vecinoDe = 0
	# arriba
	try:
		vecinoArri = max(pixeles[pixelActual - ancho])
	except:
		vecinoArri = 0
	# abajo
	try:
		vecinoAba = max(pixeles[pixelActual + ancho])
	except:
		vecinoAba = 0
	return(vecinoIz, vecinoDe, vecinoAba, vecinoArri)

def calcularVecinosDiagonales(pixeles, pixelActual, ancho):
	# izquierdo arriba
	try:
		vecinoIzArri = max(pixeles[pixelActual - (ancho + 1)])
	except:
		vecinoIzArri = 0
	# derecha arriba
	try:
		vecinoDeArri = max(pixeles[pixelActual - (ancho - 1)])
	except:
		vecinoDeArri = 0
	# izquierdo abajo
	try:
		vecinoIzAb = max(pixeles[pixelActual + (ancho - 1)])
	except:
		vecinoIzAb = 0
	# derecha abajo
	try:
		vecinoDeAb = max(pixeles[pixelActual + (ancho + 1)])
	except:
		vecinoDeAb = 0
	return(vecinoIzArri, vecinoDeArri, vecinoIzAb, vecinoDeAb)

def ordenarVecinos(vecinosTotales, pixelActual):
	vecinosTotales = list(vecinosTotales)
	vecinosOrdenados = list()

	vecinosOrdenados.append(vecinosTotales.pop(4)) # izq arriba
	vecinosOrdenados.append(vecinosTotales.pop(3)) # arriba
	vecinosOrdenados.append(vecinosTotales.pop(3)) # der arriba
	vecinosOrdenados.append(vecinosTotales.pop(0)) # izq
	vecinosOrdenados.append(max(pixelActual) )     # actual
	vecinosOrdenados.append(vecinosTotales.pop(0)) # der
	vecinosOrdenados.append(vecinosTotales.pop(1)) # izq abajo
	vecinosOrdenados.append(vecinosTotales.pop(0)) # abajo
	vecinosOrdenados.append(vecinosTotales.pop(0)) # der abajo

	return vecinosOrdenados
