from mutagen.mp3 		import MP3
from mutagen.easyid3 	import EasyID3 
from mutagen.id3 		import ID3, TIT2, TIT3, TALB, TPE1, TRCK, TYER
from shazamio 			import Shazam

import urllib.request
import mutagen.id3
import glob  
import numpy as np
import os
import json
import asyncio

def removeSpecialChars(texto):
	caracteres_especiales=['@','#','$','*','&',':','\n', '/', '\\','?','(',')','^','\"']
	for caracter in caracteres_especiales:
		if( caracter == '&'):
			texto = texto.replace(caracter,",")
		else:
			texto=texto.replace(caracter,"")
	return texto

def get_value_of(key, jsonObject, sanitize = True):
	for attribute, value in jsonObject.items():
		if( attribute == key):
			if( sanitize ):
				return removeSpecialChars( str.title(value) )
			else:
				return value
		
def getMetadata(key, jsonDocument):
	for jsonObject in jsonDocument:
		if( jsonObject["title"] == key):
			return jsonObject["text"]
			
async def main():
	shazam = Shazam()
	directorio_de_musica = "C:\\Users\\bayro\\Music\\PENDIENTE"
	
	for nombre_del_archivo in os.listdir(directorio_de_musica):

		archivo   = os.path.join(directorio_de_musica, nombre_del_archivo)
		extension = os.path.splitext(nombre_del_archivo)[1]
		
		if( os.path.isfile(archivo) ):
			if( extension == ".mp3" ):
				print("Reading ... " + archivo)

				try:
					jsonSongData = await shazam.recognize_song(archivo)

					titulo_de_la_cancion  = get_value_of("title",    jsonSongData["track"])
					artista_de_la_cancion = get_value_of("subtitle", jsonSongData["track"])
					foto_del_album        = get_value_of("coverart", jsonSongData["track"]["images"], False)
					# sAlbum  = getValue("Album",     jsonSongData["track"]["sections"][0]["metadata"])
					# sYear   = getValue("Realeased", jsonSongData["track"]["sections"][0]["metadata"])
					comentario = "www.itm-developers.com"
					nuevo_nombre_del_archivo = artista_de_la_cancion +" - "+ titulo_de_la_cancion + ".mp3"

					mp3file = MP3(archivo, ID3=EasyID3)
					# mp3file['album']  = "album editado"
					mp3file['artist'] = artista_de_la_cancion
					# mp3file['year']   = 2000
					mp3file['title']  = titulo_de_la_cancion
					mp3file.save()

					urllib.request.urlretrieve(foto_del_album, os.path.join(directorio_de_musica, artista_de_la_cancion +" - "+ titulo_de_la_cancion + os.path.splitext(foto_del_album)[1]))

					os.rename(archivo, os.path.join(directorio_de_musica, nuevo_nombre_del_archivo))

				except KeyError:
					print("SHAZAM NO pudo reconocer el archivo: ", nombre_del_archivo)
				except ConnectionResetError:
					print("Ocurrio un Error de Conexion. Omitiendo Archivo: ", nombre_del_archivo)
					continue
				except FileExistsError:
					os.remove(archivo)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
