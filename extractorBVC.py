from playwright.sync_api import sync_playwright
import pandas as pd
import openpyxl
from datetime import date

#Testing place

def clean_numeric(value):
    if not value:
        return 0.0
    try:
        clean_val = value.strip().replace('.', '').replace(',', '.')
        return float(clean_val)
    except ValueError:
        return 0.0

## Part 1 - Price extraction

hoy = date.today().strftime("%d-%m-%Y") #Obtenemos la fecha de hoy para incluirla en el archivo
pw = sync_playwright().start() #Iniciamos el objeto playwright

browser = pw.firefox.launch( #Creo la pagina con toda la informacion.
    headless=True,
    slow_mo=2000
)

## Part 1.1 Accesing to the website 
print("Accediendo a la pagina de la Bolsa de Caracas")

page = browser.new_page() #Activo la pagina
pagina = page.goto(r"https://www.bolsadecaracas.com",
                   timeout= 0) #Creando la conexion a la pagina

elements = page.query_selector_all('xpath=//*[@data-simb]') #Extraemos la lista de atributos

print("Extrayendo los Tickers de las empresas")

## Part 1.2 Extracting tickers

tickers = [] 
for element in elements:
    data_simb = element.get_attribute('data-simb') #This brings the data-simb
    if data_simb:
        tickers.append(data_simb) #this way I just append if the value is not None
    
Tabla_cotizaciones = [] #Inicializamos una lista para las cotizaciones que recorreremos

print("Extrayendo los valores de las cotizaciones")
for empresa in tickers:
    try:
        base_xpath = f'//tr[@data-simb="{empresa}"]'
        
        # Tu código de extracción modificado:
        data = {
            'Fecha Cotizacion': hoy if len(Tabla_cotizaciones) == 0 else "",
            'Ticker': page.text_content(f'xpath={base_xpath}/td[3]').strip(),
            'Precio Compra': clean_numeric(page.text_content(f'xpath={base_xpath}/td[4]')),
            'Volumen Compra': clean_numeric(page.text_content(f'xpath={base_xpath}/td[5]')),
            'Precio Venta': clean_numeric(page.text_content(f'xpath={base_xpath}/td[6]')),
            'Volumen Venta': clean_numeric(page.text_content(f'xpath={base_xpath}/td[7]'))
        }
        Tabla_cotizaciones.append(data)
    except Exception as e:
        print("la empresa " + empresa + " no contiene datos") #Indicamos cuando una empresa no contenga datos

browser.close() #Cerramos la conexion

print("Cerrando la conexion a la pagina web")
#From here the process may change depending on the output destination 

path = 'C:/Users/nombr/Downloads/Cotizaciones BCV/'
filename = hoy + " - cotizaciones BCV.xlsx"
path = path + filename

# Part 2.A - Dataframe creation and CSV export
def create_excel(data,path):
    df = pd.DataFrame(Tabla_cotizaciones) #Creo un dataframe para alojar las cotizaciones
    # df.to_csv(path,index=False) 
    # df.to_excel(path,index=False) #Exportamos el archivo CSV
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.style.set_properties(**{
            'text-align': 'center',
            'font-size':'12pt',
            'font-family':'Helvetica',
            'cell-align':'center'}).to_excel(writer,index=False)
    print("Generacion Finalizada") 

create_excel(Tabla_cotizaciones,path)

