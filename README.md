# Script para descargar información de directores de empresas

Se necesita:
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [MechanicalSoup](https://github.com/MechanicalSoup/MechanicalSoup)
- [Selenium](https://pypi.python.org/pypi/selenium)
- [PhantomJS](http://phantomjs.org/download.html)

Para descragar los datos simplemente hacer

```
python scrap_directores.py -v
```

Esto descarga dos archivos .csv con datos de empresa y directores, y un detalle con una persona por fila seguida de su lista de directorios. El archivo `scrap_directores.py` tiene varias funciones que se pueden utilizar de manera más fina para manejar la descarga.
