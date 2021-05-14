import time
import sys
import pygame as pg
import numpy as np


# hyperparametrii
ADANCIME_MAX = 6
TABLE_DIMENSION = 4

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900

BAR_WIDTH = SCREEN_WIDTH
BAR_HEIGHT = 100

k1 = 2
k2 = 2

# functie care converteste un vector in matrice.
# folosita pentru a ne usura munca cand cautam prin tabla de joc
def vector_in_matrice(vector):
	matrice = []

	for i in range(TABLE_DIMENSION):
		lista = []
		for j in range(TABLE_DIMENSION):
			lista.append(vector[i * TABLE_DIMENSION + j])
		matrice.append(lista)

	return matrice

# functie care ne spune ce punctaj primim dupa o mutare
# ne uitam in submatricea de dimensiune 5x5 cu centru matrice[linie][coloana]
def punctaj_castigat_dupa_mutare(matriceVector, pozitie, jucator):
	punctaj = 0
	matrice = vector_in_matrice(matriceVector)

	linie = pozitie // TABLE_DIMENSION
	coloana = pozitie % TABLE_DIMENSION

	# diagonala principala
	numar_simboluri = 1
	if linie - 1 >= 0 and coloana - 1 >= 0 and matrice[linie - 1][coloana - 1] == jucator:
		numar_simboluri += 1

		if linie - 2 >= 0 and coloana - 2 >= 0 and matrice[linie - 2][coloana - 2] == jucator:
			numar_simboluri += 1

	if linie + 1 <= len(matrice) - 1 and coloana + 1 <= len(matrice[0]) - 1  and matrice[linie + 1][coloana + 1] == jucator:
		numar_simboluri += 1

		if linie + 2 <= len(matrice) - 1 and coloana + 2 <= len(matrice[0]) - 1  and matrice[linie + 2][coloana + 2] == jucator:
			numar_simboluri += 1
	punctaj += max(numar_simboluri - 2, 0)

	# coloana
	numar_simboluri = 1
	if linie - 1 >= 0 and matrice[linie - 1][coloana] == jucator:
		numar_simboluri += 1

		if linie - 2 >= 0 and matrice[linie - 2][coloana] == jucator:
			numar_simboluri += 1

	if linie + 1 <= len(matrice) - 1 and matrice[linie + 1][coloana] == jucator:
		numar_simboluri += 1

		if linie + 2 <= len(matrice) - 1 and matrice[linie - 2][coloana] == jucator:
			numar_simboluri += 1
	punctaj += max(numar_simboluri - 2, 0)

	# diagonala secundara
	numar_simboluri = 1
	if linie - 1 >= 0 and coloana + 1 <= len(matrice[0]) - 1 and matrice[linie - 1][coloana + 1] == jucator:
		numar_simboluri += 1

		if linie - 2 >= 0 and coloana + 2 <= len(matrice[0]) - 1 and matrice[linie - 2][coloana + 2] == jucator:
			numar_simboluri += 1

	if linie + 1 <= len(matrice) - 1 and coloana - 1 >= 0 and matrice[linie + 1][coloana - 1] == jucator:
		numar_simboluri += 1

		if linie + 2 <= len(matrice) - 1 and coloana - 2 >= 0  and matrice[linie - 2][coloana - 2] == jucator:
			numar_simboluri += 1
	punctaj += max(numar_simboluri - 2, 0)

	# linia
	numar_simboluri = 1
	if coloana - 1 >= 0 and matrice[linie][coloana - 1] == jucator:
		numar_simboluri += 1

		if coloana - 2 >= 0 and matrice[linie][coloana - 2] == jucator:
			numar_simboluri += 1

	if coloana + 1 <= len(matrice) - 1 and matrice[linie][coloana + 1] == jucator:
		numar_simboluri += 1

		if coloana + 2 <= len(matrice) - 1 and matrice[linie][coloana + 2] == jucator:
			numar_simboluri += 1
	punctaj += max(numar_simboluri - 2, 0)

	return punctaj


# functie care verifica daca o mutare este valida
def pot_muta_aici(matriceVector, pozitie, jucator):
	# transformam vectorul in matrice pentru a lucra mai usor cu k1 si k2
	matrice = vector_in_matrice(matriceVector)

	linie = pozitie // TABLE_DIMENSION
	coloana = pozitie % TABLE_DIMENSION

	# la prima mutare a fiecarui jucator pot muta oriunde (mai putin peste mutarea altui jucator)
	if len(list(filter(lambda x: x == jucator, matriceVector))) == 0 and matrice[linie][coloana] == Joc.GOL:
		return True

	# zona unde vrem sa mutam trebuie sa fie goala
	if matrice[linie][coloana] != Joc.GOL:
		return False

	# verificam daca exista un simbol similar in vecinatatea zonei unde vrem sa facem mutarea
	# vecinatate <=> distanta trebuie cel putin 2 simboluri sa fie cel putin egala cu linie = k1 si coloana = k2
	for i in range(linie - k1, linie + k1 + 1):
		if i < 0 or i >= len(matrice):
			continue
		for j in range(coloana - k2, coloana + k2 + 1):
			if j < 0 or j >= len(matrice[0]):
					continue

			if matrice[i][j] == jucator:
				return True

	return False

class Joc:
	nr_coloane = TABLE_DIMENSION
	JMIN = None
	JMAX = None
	scor_JMIN = 0
	scor_JMAX = 0
	GOL = '#'

	def __init__(self, tabla = None):
		self.matrice = tabla or [self.__class__.GOL] * TABLE_DIMENSION ** 2

	@classmethod
	def init(cls, display, nr_coloane = TABLE_DIMENSION, dim_celula = int((SCREEN_HEIGHT - 100) / TABLE_DIMENSION)):
		cls.display = display
		cls.dim_celula = dim_celula

		cls.x_img = pg.image.load('ics.png')
		cls.x_img = pg.transform.scale(cls.x_img, (dim_celula, dim_celula))

		cls.zero_img = pg.image.load('zero.png')
		cls.zero_img = pg.transform.scale(cls.zero_img, (dim_celula, dim_celula))

		cls.celuleGrid = []
		for linie in range(nr_coloane):
			for coloana in range(nr_coloane):
				patrat = pg.Rect(coloana * (dim_celula + 1), linie * (dim_celula + 1), dim_celula, dim_celula)
				cls.celuleGrid.append(patrat)

	def deseneaza_grid(self, marcaj = None):
		for ind in range(len(self.matrice)):
			linie = ind // TABLE_DIMENSION
			coloana = ind % TABLE_DIMENSION

			if marcaj == ind:
				culoare = (255, 0, 0) # rosu
			else:
				culoare = (255, 255, 255) # alb

			pg.draw.rect(self.__class__.display, culoare, self.__class__.celuleGrid[ind])

			if self.matrice[ind] == 'x':
				self.__class__.display.blit(
					self.__class__.x_img,
					(coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1))
				)
			elif self.matrice[ind] == '0':
				self.__class__.display.blit(
					self.__class__.zero_img,
					(coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1))
				)
			pg.display.flip()

	@classmethod
	def jucator_opus(cls, jucator):
		return cls.JMAX if jucator == cls.JMIN else cls.JMIN

	def final(self):
		if self.__class__.GOL not in self.matrice:
			if self.__class__.scor_JMIN > self.__class__.scor_JMAX:
				return self.__class__.JMIN
			elif self.__class__.scor_JMIN < self.__class__.scor_JMAX:
				return self.__class__.JMAX
			else:
				return 'remiza'

		return False


	def mutari(self, jucator_opus):
		mutari = []

		# luam toate mutarile posibile
		for i in range(len(self.matrice)):
			if pot_muta_aici(self.matrice, i, jucator_opus):
				matrice_tabla_noua = list(self.matrice)
				matrice_tabla_noua[i] = jucator_opus
				mutari.append(Joc(matrice_tabla_noua))

		return mutari

	# calculam scorul total pentru jucator
	def punctaj_maxim(self, jucator):
		punctaj = 0

		for i in range(len(self.matrice)):
			# ma uit cu o mutare in viitor
			if self.matrice[i] == jucator:
				punctaj += punctaj_castigat_dupa_mutare(self.matrice, i, self.__class__.JMAX)

		return punctaj

	def estimeaza_scor(self, adancime):
		t_final = self.final()

		if t_final == self.__class__.JMAX:
			return (99 + adancime)
		elif t_final == self.__class__.JMIN:
			return (-99 - adancime)
		elif t_final == 'remiza':
			return 0
		else:
			# calculatorul alege mutarea care ii aduce cele mai multe puncte
			return self.punctaj_maxim(self.__class__.JMAX) - self.punctaj_maxim(self.__class__.JMIN)

	def __str__(self):
		sir = ''
		for i in range(TABLE_DIMENSION):
			sir += ' '.join([str(x) for x in self.matrice[i * TABLE_DIMENSION : (i + 1) * TABLE_DIMENSION]]) + '\n'

		return sir


class Stare:
	def __init__(self, tabla_joc: Joc, jucator_curent, adancime, parinte = None, estimare = None):
		self.tabla_joc = tabla_joc
		self.jucator_curent = jucator_curent

		# adancimea in arborele de stari
		self.adancime = adancime

		# estimarea favorabilitatii starii
		self.estimare = estimare

		# lista de mutari posibile din starea curenta
		self.mutari_posibile = []

		# cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
		self.starea_aleasa = None

	def mutari(self):
		mutari = self.tabla_joc.mutari(self.jucator_curent)
		jucator_opus = Joc.jucator_opus(self.jucator_curent)
		stari_mutari = [Stare(mutare, jucator_opus, self.adancime - 1, parinte = self) for mutare in mutari]

		return stari_mutari

	def __str__(self):
		return str(self.tabla_joc) + '(Jucator curent: ' + self.jucator_curent + ')\n'

def minimax(stare):
	if stare.adancime == 0 or stare.tabla_joc.final():
		stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
		return stare

	stare.mutari_posibile = stare.mutari()

	# aplic minimax pe toate mutarile posibile (calculand astfel subarborii lor)
	mutariCuEstimare = [minimax(mutare) for mutare in stare.mutari_posibile]

	if stare.jucator_curent == Joc.JMAX:
		stare.stare_aleasa =  max(mutariCuEstimare, key = lambda x: x.estimare)
	else:
		stare.stare_aleasa = min(mutariCuEstimare, key = lambda x: x.estimare)
	stare.estimare = stare.stare_aleasa.estimare
	return stare

def alpha_beta(alpha, beta, stare, JMIN = None, JMAX = None):

	if not(JMIN):
		JMIN = Joc.JMIN

	if not(JMAX):
		JMAX = Joc.JMAX

	if stare.adancime==0 or stare.tabla_joc.final() :
		stare.estimare=stare.tabla_joc.estimeaza_scor(stare.adancime)
		return stare

	if alpha>beta:
		return stare #este intr-un interval invalid deci nu o mai procesez

	stare.mutari_posibile=stare.mutari()


	if stare.jucator_curent == JMAX:
		estimare_curenta=float('-inf')

		for mutare in stare.mutari_posibile:
			#calculeaza estimarea pentru starea noua, realizand subarborele
			stare_noua=alpha_beta(alpha, beta, mutare)

			if (estimare_curenta<stare_noua.estimare):
				stare.stare_aleasa=stare_noua
				estimare_curenta=stare_noua.estimare
			if(alpha<stare_noua.estimare):
				alpha=stare_noua.estimare
				if alpha>=beta:
					break

	elif stare.jucator_curent == JMIN :
		estimare_curenta=float('inf')

		for mutare in stare.mutari_posibile:

			stare_noua=alpha_beta(alpha, beta, mutare)

			if (estimare_curenta>stare_noua.estimare):
				stare.stare_aleasa=stare_noua
				estimare_curenta=stare_noua.estimare

			if(beta>stare_noua.estimare):
				beta=stare_noua.estimare
				if alpha>=beta:
					break
	stare.estimare=stare.stare_aleasa.estimare

	return stare

def afisare_daca_final(stare_curenta):
	final = stare_curenta.tabla_joc.final()

	if final:
		if final == 'remiza':
			print('Remiza')
		else:
			print('A castigat ' + str(final))

		return True

	return False

# returneaza butonul
def set_titlu(ecran, titlu):
	color = (255, 255, 255)
	font = pg.font.SysFont('Corbel', 48)
	text = font.render(titlu, True, color)
	ecran.blit(text, (15, SCREEN_HEIGHT / 2 - 100))
	pg.display.update()

def set_bar(ecran, stare_curenta):
	barBg = pg.Rect(0, SCREEN_HEIGHT - BAR_HEIGHT, SCREEN_WIDTH, BAR_HEIGHT)
	pg.draw.rect(ecran, (23, 180, 23), barBg)


	color = (255, 255, 255)
	font = pg.font.SysFont('Corbel', 48)

	castigator = stare_curenta.tabla_joc.final()
	if castigator != False :
		if (castigator == 'remiza'):
			text = font.render('REMIZA!', True, color)
		else:
			text = font.render('A castigat ' + castigator, True, color)
		ecran.blit(text, (15, SCREEN_HEIGHT - BAR_HEIGHT + 15))
		pg.display.update()
		return False

	text = font.render(f'Scor {Joc.JMIN} : {Joc.scor_JMIN}', True, color)

	ecran.blit(text, (15, SCREEN_HEIGHT - BAR_HEIGHT + 15))

	text = font.render(f'Scor {Joc.JMAX} : {Joc.scor_JMAX}', True, color)
	text_width = text.get_width()
	text_height = text.get_height()

	ecran.blit(text, (15, SCREEN_HEIGHT - BAR_HEIGHT + text_height + 15))

	pg.display.update()

def deseneaza_button(ecran, text, pos_x, pos_y):
	padding = 15
	smallfont = pg.font.SysFont('Corbel', 35)
	color = (255, 255, 255)
	smallfont = pg.font.SysFont('Corbel', 35)

	text = smallfont.render(text, True, color)
	text_width = text.get_width()
	text_height = text.get_height()

	button = pg.Rect(pos_x, pos_y, text_width + 2 * padding, text_height + 2 * padding)

	pg.draw.rect(ecran, (23, 180, 23), button)
	ecran.blit(text, (pos_x + padding, pos_y + padding))
	pg.display.update()

	return button

def alege_algoritm_menu(ecran):
	ecran.fill((0,0,0))

	set_titlu(ecran, 'Ce algoritm sa foloseasca calculatorul?')

	buttons = []
	buttons.append({
		'key': 'min_max',
		'button': deseneaza_button(ecran, 'Algoritmul MinMax', 15, SCREEN_HEIGHT / 2)
	})

	buttons.append({
		'key': 'alpha_beta',
		'button': deseneaza_button(ecran, 'Algoritmul Alpha-beta', 15, SCREEN_HEIGHT / 2 + 100)
	})

	while True:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
			elif event.type == pg.MOUSEBUTTONDOWN:
				click_position = pg.mouse.get_pos()

				for button in buttons:
					if button['button'].collidepoint(click_position):
						key = button['key']

						if key == 'min_max':
							return 'min_max'
						elif key == 'alpha_beta':
							return 'alpha_beta'

						pg.display.flip()

def nivel_dificultate_menu(ecran):
	ecran.fill((0,0,0))

	set_titlu(ecran, 'Nivel de dificultate:')

	buttons = []
	buttons.append({
		'key': 0,
		'button': deseneaza_button(ecran, 'Incepator', 15, SCREEN_HEIGHT / 2)
	})

	buttons.append({
		'key': 1,
		'button': deseneaza_button(ecran, 'Mediu', 15, SCREEN_HEIGHT / 2 + 100)
	})

	buttons.append({
		'key': 2,
		'button': deseneaza_button(ecran, 'Avansat', 15, SCREEN_HEIGHT / 2 + 200)
	})

	while True:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
			elif event.type == pg.MOUSEBUTTONDOWN:
				click_position = pg.mouse.get_pos()

				for button in buttons:
					if button['button'].collidepoint(click_position):
						key = button['key']
						pg.display.flip()
						if key == 0:
							ADANCIME_MAX = 0
						elif key == 1:
							ADANCIME_MAX = 3
						else:
							ADANCIME_MAX = 6
						return key


# returneaza 'x' sau '0'
def x_or_0_menu(ecran):
	ecran.fill((0,0,0))

	set_titlu(ecran, 'Alege cu ce joci:')

	buttons = []
	buttons.append({
		'key': 'x',
		'button': deseneaza_button(ecran, 'X', 15, SCREEN_HEIGHT / 2)
	})

	buttons.append({
		'key': '0',
		'button': deseneaza_button(ecran, '0', 15, SCREEN_HEIGHT / 2 + 100)
	})

	while True:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
			elif event.type == pg.MOUSEBUTTONDOWN:
				click_position = pg.mouse.get_pos()

				for button in buttons:
					if button['button'].collidepoint(click_position):
						key = button['key']
						pg.display.flip()

						return key


def menu(ecran):
	tip_algoritm = None
	jucator = None
	dimensiune_tabla = TABLE_DIMENSION

	set_titlu(ecran, 'Meniu Principal')

	buttons = []
	buttons.append({
		'key': 'jucator_vs_jucator',
		'button': deseneaza_button(ecran, 'Jucator vs. Jucator', 15, SCREEN_HEIGHT / 2)
	})

	buttons.append({
		'key': 'jucator_vs_calculator',
		'button': deseneaza_button(ecran, 'Jucator vs. Calculator', 15, SCREEN_HEIGHT / 2 + 100)
	})

	buttons.append({
		'key': 'calculator_vs_calculator',
		'button': deseneaza_button(ecran, 'Calculator vs. Calculator', 15, SCREEN_HEIGHT / 2 + 200)
	})


	while True:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
			elif event.type == pg.MOUSEBUTTONDOWN:
				click_position = pg.mouse.get_pos()

				for button in buttons:
					if button['button'].collidepoint(click_position):
						key = button['key']
						if key == 'jucator_vs_jucator':
							jucator = 'x'
						elif key == 'jucator_vs_calculator':
							tip_algoritm = alege_algoritm_menu(ecran)
							nivel_dificultate_menu(ecran)
							jucator = x_or_0_menu(ecran)
						elif key == 'calculator_vs_calculator':
							tip_algoritm = alege_algoritm_menu(ecran)
							nivel_dificultate_menu(ecran)
							jucator = 'x'

						ecran.fill((0,0,0))
						pg.display.flip()
						# (algoritm, jucator, tip joc, dimensiune)
						return {
							'tip_algoritm': tip_algoritm,
							'jucator': jucator,
							'tip_joc': key,
							'dimensiune_tabla': dimensiune_tabla
						}

def jucator_vs_jucator(ecran, inputs):
	# initializare tabla de joc
	tabla_curenta = Joc()
	print('Tabla initiala')
	print(str(tabla_curenta))

	# creare stare initiala
	stare_curenta = Stare(tabla_curenta, 'x', ADANCIME_MAX)

	Joc.init(ecran)

	de_mutat = False
	tabla_curenta.deseneaza_grid()

	while True:
		set_bar(ecran, stare_curenta)
		# jucatorul e JMAX
		jucator_curent = Joc.JMIN
		if stare_curenta.jucator_curent == Joc.JMIN:
			jucator_curent = Joc.JMIN
		else:
			jucator_curent = Joc.JMAX

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			elif event.type == pg.MOUSEBUTTONDOWN:
				click_position = pg.mouse.get_pos()

				for np in range(len(Joc.celuleGrid)):
					if Joc.celuleGrid[np].collidepoint(click_position):
						linie = np // TABLE_DIMENSION
						coloana = np % TABLE_DIMENSION

						if not(pot_muta_aici(stare_curenta.tabla_joc.matrice, np, jucator_curent)):
								print('nu poti muta aici!')
								continue

						if jucator_curent == Joc.JMIN:
							Joc.scor_JMIN += punctaj_castigat_dupa_mutare(stare_curenta.tabla_joc.matrice, np, Joc.JMIN)
						else:
							Joc.scor_JMAX += punctaj_castigat_dupa_mutare(stare_curenta.tabla_joc.matrice, np, Joc.JMAX)

						if stare_curenta.tabla_joc.matrice[np] == jucator_curent:
							if (de_mutat and linie == de_mutat[0] and coloana == de_mutat[1]):
								de_mutat = False
								stare_curenta.tabla_joc.deseneaza_grid()
							else:
								de_mutat = (linie, coloana)
								stare_curenta.tabla_joc.deseneaza_grid(np)

						if stare_curenta.tabla_joc.matrice[np] == Joc.GOL:
							if de_mutat:
								stare_curenta.tabla_joc.matrice[de_mutat[0] * TABLE_DIMENSION + de_mutat[1]] = Joc.GOL
								de_mutat = False

							stare_curenta.tabla_joc.matrice[linie * TABLE_DIMENSION + coloana] = jucator_curent

						print('\n Tabla dupa mutarea jucatorului')
						print(str(stare_curenta))

						stare_curenta.tabla_joc.deseneaza_grid()


						stare_curenta.jucator_curent = Joc.jucator_opus(stare_curenta.jucator_curent)

def jucator_vs_calculator(ecran, inputs):
	# initializare tabla de joc
	tabla_curenta = Joc()
	print('Tabla initiala')
	print(str(tabla_curenta))

	# creare stare initiala
	stare_curenta = Stare(tabla_curenta, 'x', ADANCIME_MAX)

	Joc.init(ecran)

	de_mutat = False
	tabla_curenta.deseneaza_grid()

	while True:
		set_bar(ecran, stare_curenta)
		# jucatorul e JMAX
		if stare_curenta.jucator_curent == Joc.JMIN:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()
				elif event.type == pg.MOUSEBUTTONDOWN:
					click_position = pg.mouse.get_pos()

					for np in range(len(Joc.celuleGrid)):
						if Joc.celuleGrid[np].collidepoint(click_position):
							linie = np // TABLE_DIMENSION
							coloana = np % TABLE_DIMENSION

							if not(pot_muta_aici(stare_curenta.tabla_joc.matrice, np, Joc.JMIN)):
									print('nu poti muta aici!')
									continue

							Joc.scor_JMIN += punctaj_castigat_dupa_mutare(stare_curenta.tabla_joc.matrice, np, Joc.JMIN)

							if stare_curenta.tabla_joc.matrice[np] == Joc.JMIN:
								if (de_mutat and linie == de_mutat[0] and coloana == de_mutat[1]):
									de_mutat = False
									stare_curenta.tabla_joc.deseneaza_grid()
								else:
									de_mutat = (linie, coloana)
									stare_curenta.tabla_joc.deseneaza_grid(np)

							if stare_curenta.tabla_joc.matrice[np] == Joc.GOL:
								if de_mutat:
									stare_curenta.tabla_joc.matrice[de_mutat[0] * TABLE_DIMENSION + de_mutat[1]] = Joc.GOL
									de_mutat = False

								stare_curenta.tabla_joc.matrice[linie * TABLE_DIMENSION + coloana] = Joc.JMIN

							print('\n Tabla dupa mutarea jucatorului')
							print(str(stare_curenta))

							stare_curenta.tabla_joc.deseneaza_grid()

							stare_curenta.jucator_curent = Joc.jucator_opus(stare_curenta.jucator_curent)
		# jucatorul e JMAX
		else:
			t1 = int(round(time.time() * 1000))

			matrice_veche = stare_curenta.tabla_joc.matrice[:]
			if inputs['tip_algoritm'] == 'min_max':
				stare_actualizata = minimax(stare_curenta)
			else:
				stare_actualizata = alpha_beta(-500, 500, stare_curenta, JMIN = Joc.JMIN, JMAX = Joc.JMAX)

			print('Tabla dupa mutarea calculatorului')
			print(str(stare_curenta))
			stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
			stare_curenta.tabla_joc.deseneaza_grid()

			for i in range(len(stare_actualizata.tabla_joc.matrice)):
				if stare_actualizata.tabla_joc.matrice[i] != matrice_veche[i]:

					Joc.scor_JMAX += punctaj_castigat_dupa_mutare(stare_curenta.tabla_joc.matrice, i, Joc.JMAX)
					break

			t2 = int(round(time.time() * 1000))

			print('Calculatorul a gandit timp de ' + str(t2 - t1) + 'ms')

			if afisare_daca_final(stare_curenta):
				break

			stare_curenta.jucator_curent = Joc.jucator_opus(stare_curenta.jucator_curent)

def calculator_vs_calculator(ecran, inputs):
	# initializare tabla de joc
	tabla_curenta = Joc()
	print('Tabla initiala')
	print(str(tabla_curenta))

	# creare stare initiala
	stare_curenta = Stare(tabla_curenta, 'x', ADANCIME_MAX)

	Joc.init(ecran)

	de_mutat = False
	tabla_curenta.deseneaza_grid()

	while True:
		set_bar(ecran, stare_curenta)
		# jucatorul e JMIN
		if stare_curenta.jucator_curent == Joc.JMIN:
			t1 = int(round(time.time() * 1000))

			if inputs['tip_algoritm'] == 'min_max':
				stare_actualizata = minimax(stare_curenta)
			else:
				stare_actualizata = alpha_beta(-500, 500, stare_curenta, JMIN = Joc.JMAX, JMAX = Joc.JMIN)

			print('Tabla dupa mutarea calculatorului')
			print(str(stare_curenta))
			stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
			stare_curenta.tabla_joc.deseneaza_grid()

			t2 = int(round(time.time() * 1000))

			print('Calculatorul 1 a gandit timp de ' + str(t2 - t1) + 'ms')

			if afisare_daca_final(stare_curenta):
				return False

			stare_curenta.jucator_curent = Joc.jucator_opus(stare_curenta.jucator_curent)

		# jucatorul e JMAX
		else:
			t1 = int(round(time.time() * 1000))

			if inputs['tip_algoritm'] == 'min_max':
				stare_actualizata = minimax(stare_curenta)
			else:
				stare_actualizata = alpha_beta(-500, 500, stare_curenta, JMIN = Joc.JMIN, JMAX = Joc.JMAX)

			print('Tabla dupa mutarea calculatorului')
			print(str(stare_curenta))
			stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
			stare_curenta.tabla_joc.deseneaza_grid()

			t2 = int(round(time.time() * 1000))

			print('Calculatorul 2 a gandit timp de ' + str(t2 - t1) + 'ms')
			print(not(not(afisare_daca_final(stare_curenta))))
			if afisare_daca_final(stare_curenta):
				return False

			stare_curenta.jucator_curent = Joc.jucator_opus(stare_curenta.jucator_curent)

def main():
	pg.init()
	pg.display.set_caption('x si 0')
	ecran = pg.display.set_mode(size = (SCREEN_WIDTH, SCREEN_HEIGHT))
	inputs = menu(ecran)

	Joc.JMIN = inputs['jucator']
	Joc.JMAX = '0' if Joc.JMIN == 'x' else 'x'

	if inputs['tip_joc'] == 'jucator_vs_calculator':
		jucator_vs_calculator(ecran, inputs)
	elif inputs['tip_joc'] == 'jucator_vs_jucator':
		jucator_vs_jucator(ecran, inputs)
	elif inputs['tip_joc'] == 'calculator_vs_calculator':
		calculator_vs_calculator(ecran, inputs)

if __name__ == '__main__':
	main()
	while True:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pq.quit()
				sys.exit()

