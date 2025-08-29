from xml.dom import minidom

conf_procesador = minidom.parse("configuracion.xml")
item_procesador = conf_procesador.getElementsByTagName("procesador")[0]
procesador = item_procesador.firstChild.data
print('----> ', procesador)

item_params = item_procesador.getElementsByTagName("param")

params = []
for param in item_params:
    params.append(param.firstChild.data)

print(params)



