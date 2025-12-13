from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import date

hoy = date.today
pw = sync_playwright().start() #Iniciamos el objeto playwright

browser = pw.chromium.launch( #Creo la pagina con toda la informacion.
    headless=True,
    slow_mo=2000
)

page = browser.new_page() #Activo la pagina
pagina = page.goto("https://www.bolsadecaracas.com",
                   timeout= 0) #Creando la conexion a la pagina

elements = page.query_selector_all('xpath=//*[@data-simb]') #Extraemos la lista de atributos

tickers = [] #inicializamos una lista para alojar los identificadores de las acciones
for element in elements:
    data_simb = element.get_attribute('data-simb') #Con esto extraigo el simbolo de la empresa
    if data_simb:
        tickers.append(data_simb) #incluyo en la lista el valor
    
Tabla_cotizaciones = [] #Inicializamos una lista para las cotizaciones que recorreremos

for empresa in tickers:
    try:
        base_xpath = f'//tr[@data-simb="{empresa}"]'
        
        data = {
            # 'data_simb': empresa, #Este es el ticker de la empresa que se repetira
            # 'company_name': page.text_content(f'xpath={base_xpath}/td[2]').strip(), #Este es el nombre de la empresa que no lo necesito
            'Fecha Cotizacion': hoy, #Fecha para facilitar la lectura final
            'Ticker': page.text_content(f'xpath={base_xpath}/td[3]').strip(),
            'Precio Compra': page.text_content(f'xpath={base_xpath}/td[4]').strip(),
            'Volumen Compra': page.text_content(f'xpath={base_xpath}/td[5]').strip(),
            'Precio Venta': page.text_content(f'xpath={base_xpath}/td[6]').strip(),
            'Volumen Venta': page.text_content(f'xpath={base_xpath}/td[7]').strip()
            
        }
        Tabla_cotizaciones.append(data)
    
    except Exception as e:
        print("la empresa " + empresa + " no contiene datos") #Indicamos cuando una empresa no contenga datos

browser.close() #Cerramos la conexion

df = pd.DataFrame(Tabla_cotizaciones) #Creo un dataframe para alojar las cotizaciones

df.to_csv('cotizaciones BCV.csv',index=False) #Exportmos el archivo CSV