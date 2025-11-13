import qrcode

texto = "nombre: zuka numero: 23130705 Area: Linea de produccion"
img = qrcode.make(texto)  # por defecto usa corrección M (buena para la mayoría)
img.save("qr_texto.png")
