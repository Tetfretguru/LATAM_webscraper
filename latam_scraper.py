import requests
from bs4 import BeautifulSoup
from selenium import webdriver

def _get_vuelos(driver):
	vuelos = driver.find_elements_by_xpath('//li[@class="flight"]')
	return vuelos

def _get_tarifa(vuelo):
	divisas = vuelo.find_elements_by_xpath('.//div[@class="fares-table-container"]//tfoot//td[contains(@class, "fare-")]//span[@class="currency-symbol"]')
	valor = vuelo.find_elements_by_xpath('.//div[@class="fares-table-container"]//tfoot//td[contains(@class, "fare-")]//span[@class="value"]')

	precios = []

	for d in divisas:
		for v in valores:
			precio = d.text + ' ' + v.text
			precios.append(precio)
		break
	

	tarifas = {
		'Light':precios[0],
    	'Plus':precios[1],
    	'Top':precios[2]
		}

	return tarifas

def _get_escalas(vuelo):
	# Segmentos del contenido en donde se ven las escalas
	segmentos = vuelo.find_elements_by_xpath('//div[@class="sc-hZSUBg gfeULV"]/div[@class="sc-cLQEGU hyoued"]')
	escalas = len(segmentos) - 1 # Porque cuenta desde salida/escala y escala/salida
	print(f'El vuelo de MVD a MAD tiene {escalas} escala(s).')

	info_escalas = []
	for segmento in segmentos:
		# Aeropuerto de salida
		airport = segmento.find_element_by_xpath('.//div[@class="sc-iujRgT jEtESl"]/span[@class="sc-eTuwsz eumCTU"]/span[@class="sc-hXRMBi gVvErD"]').text 
		# Hora de salida
		h_salida = segmento.find_element_by_xpath('.//div[@class="sc-bwCtUz iybVbT"]/time').get_attribute('datetime')
		# Duración de vuelo a próxima escala
		duracion = segmento.find_element_by_xpath('.//div[@class="sc-eXEjpC fqUnRK"]/span[@class="sc-esjQYD dMquDU"]/time').get_attribute('datetime')
		# Info de combinación
		try:    
		    combinacion = segmento.find_element_by_xpath('//div[@class="sc-hMFtBS cfwWiO"]/span[@class="connection-label sc-hORach NXcGo"]').text
		    cambio_avion = segmento.find_element_by_xpath('//div[@class="sc-hMFtBS cfwWiO"]/span[@class="connection-changes sc-hORach NXcGo"]').text
		    info = f'{combinacion} -- {cambio_avion}'
		except:
		    print('Revise XPath.')
		    pass
		# Flota
		flota = segmento.find_element_by_xpath('//div[@class="airline-flight-details"]/b').text
		# Modelo de avón
		modelo_avion = segmento.find_element_by_xpath('//div[@class="airline-flight-details"]/span[@class="sc-gzOgki uTyOl"]').text

		data_escalas = {
			'Aeropuerto': airport,
			'Hora de salida': h_salida,
			'Duración p/ escala': duracion,
			'Info de conexión': info,
			'Flota': flota,
			'Avión': modelo_avion
		}
		info_escalas.append(data_escalas)

	return info_escalas

def _get_tiempos(vuelo):
	
	#Hora de partida
	h_salida = vuelo.find_element_by_xpath('.//div[@class="departure"]/time').get_attribute('datetime')
	#Hora de llegada
	h_llegada = vuelo.find_element_by_xpath('.//div[@class="arrival"]/time').get_attribute('datetime')
	# Duración de vuelo
	duracion = vuelo.find_element_by_xpath('.//span[@class="duration"]/time').get_attribute('datetime')

	data_tiempos = {
		'Hora de salida':h_salida,
		'Hora de llegada':h_llegada,
		'Duración':duracion
	}
	return data_tiempos

def main_get_info(driver):
	
	# Extraer informacion de la pagina
	vuelos = _get_vuelos(driver)
	print(f'Se encontraron {len(vuelos)} vuelos.')
	print('Iniciando scraping...')
	info = []
	for vuelo in vuelos:
		tiempos = _get_tiempos(vuelo)
		
		# Click en modal para conocer escalas
		boton_escalas = vuelo.find_element_by_xpath('.//div[@class="flight-summary-stops-description"]/button')
		boton_escalas.click()

		# Obtener escalas
		escalas = _get_escalas(vuelo)
		
		# Cerrar modal
		cerrar_modal = driver.find_element_by_xpath('//div[@class="modal-content sc-iwsKbI eHVGAN"]//button[@class="close"]')
		cerrar_modal.click()
		vuelo.click()

		# Obtener tarifas
		tarifas = _get_tarifa(vuelo)

		data_info = {
			'Tiempos':tiempos,
			'Escalas':escalas,
			'Tarifas':tarifas
		}
		info.append(data_info)

	return info


if __name__ == '__main__':
	url = 'https://www.latam.com/es_uy/apps/personas/booking?fecha1_dia=04&fecha1_anomes=2020-11&from_city1=MVD&to_city1=MAD&ida_vuelta=ida_vuelta&fecha2_dia=21&fecha2_anomes=2020-11&from_city2=MAD&to_city2=MVD&cabina=Y&nadults=1&nchildren=0&ninfants=0&app=deal-finder#/'
	r = requests.get(url)
	soup = BeautifulSoup(r.text, 'lxml')
	# Iniciar navegador automatico
	options = webdriver.ChromeOptions()
	options.add_argument('--incognito')

	driver = webdriver.Chrome(executable_path='/Users/Martin/Documents/Proyectos/Airlines_scrapper/chromedriver', options=options)
	driver.get(url)
	main_get_info(driver)
