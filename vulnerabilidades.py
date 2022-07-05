
#importamos librerias
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import rasterio as rst
from rasterio.transform import from_origin


class vul_model:
    ''' modelo de vulnerabilidades con inclucion de sub analisis, la manera de correr el proyecto es guardando los rasters de analisis previamente normalizados en 
    carpetas que seran los subanalisis, para inicializar el proyecto solo hace falta agregar la direccion de la carpeta donde se encuentran las otras carpetas
    de sub analisis'''

    def NormalizeData(data):
        ''' los datos seran normalizados en una escala de 0 a 1 '''
        return (data - np.min(data)) / (np.max(data) - np.min(data))  #normalizamos los datos
        
    def __init__(self, direccion):

        vul_model.direccion = direccion  #guardamos la direccion de las carpetas de los anlisis

        p=os.listdir(direccion)   
        vul_model.carpetas = []  #creamos la variable donde guardamos el nombre de las carpetas

        for i in p: #agregamos las carpetas a lista SOLO SI son carpetas, se ignoran los archivos
            if os.path.isdir(direccion+i): 
                vul_model.carpetas.append(i)
        
        print('Se agregaron las carpetas de analisis: ' ,vul_model.carpetas )

        #creamos los vectores en losque seran guardados los datos
        vul_model.rr =[]  # datos de cada archivo
        vul_model.r_names =[] #nombres de los archivos

        for k in range(0,len(vul_model.carpetas)): #importamos todos lo datos
            print('  ')
            print('cargando capas de: '+ vul_model.carpetas[k])
            print('  ')
            r = []   #se resetea estos vectores en cada iteracion
            r_n = []

            path2 = vul_model.direccion + vul_model.carpetas[k]
            vul_model.archivos = os.listdir( path2)
            for i in range(0,len(vul_model.archivos)):

                print('cargando: '+vul_model.direccion + path2+ '/' +vul_model.archivos[i])
                r_n.append(vul_model.archivos[i])
                r.append( rst.open(path2+ '/' +vul_model.archivos[i]).read(1))

            vul_model.r_names.append(r_n)
            vul_model.rr.append(r)

        print(' ')    
        print('ha terminado la carga')    

        #se filtran los rasters para que todos tengan las mismas medidas y extenciones con los tamaños miniimos de raster
        print('  ')
        print('filtrando rasters...')
        shapes0=[]
        shapes1=[]

        #obtenemos los valores minimos en ambos ejes
        for k in range(0,len(vul_model.rr)):
            for i in vul_model.rr[k]:
                shapes0.append(i.shape[0])
                shapes1.append(i.shape[1])

        min1=min(shapes0)
        min2=min(shapes1)

        #se filtran los rasters
        for k in range(0,len(vul_model.rr)):
            for i in range(0,len(vul_model.rr[k])):

                vul_model.rr[k][i] = vul_model.rr[k][i][0:min1,0:min2]
        print('  ')
        print('rasters filtrados...')    


        #acomodamos los rasters en diferentes dataframes y estos DF en una lista        
        vul_model.frames = []

        for k in range(0,len(vul_model.rr)):
            vul_model.frames.append( pd.DataFrame(index=range(0,len(vul_model.rr[k])), columns = ['rasters','rast_name','pond'] ))
            vul_model.frames[k]['rasters'] = vul_model.rr[k]
            vul_model.frames[k]['rast_name'] = vul_model.r_names[k]    

        print('    ') 
        print('dataframe acomodado')     

        for i in range(0,len(vul_model.frames)):
            vul_model.frames[i]['pond'] = np.zeros(len(vul_model.frames[i]),dtype=float) + int(1) 

        vul_model.frames_sum = pd.DataFrame(columns = ['raster sum', 'pond','categoria'])
        vul_model.frames_sum['pond'] =np.zeros(len(vul_model.frames),dtype=int)   
        vul_model.frames_sum['categoria'] = vul_model.carpetas

        print('   ')
        print('modelo inicializado')
         
    def norm_indiv(self, carp,capa):
        ''' se normalizan individualemnte los preanalisis si es necesario: model.norm_indiv(carp,capa) 
        parametros: 
        carp (int)-> es el la carpeta que sera normalizada
        capa (int)-> es la capa que sera normalizada
        '''
        vul_model.frames[carp]['rasters'][capa] = vul_model.NormalizeData(vul_model.frames[carp]['rasters'][capa][0])

    def norm_sum(self):
        '''se normalizan los pre analisis de ser necesario: model.norm_sum().'''
        for i in range(0, len(vul_model.frames_sum)):
            vul_model.frames_sum['raster sum'][i] = vul_model.NormalizeData( vul_model.frames_sum['raster sum'][i])

    def add_pond(self, frame, pond_list):
        '''Se agrega la ponderacion a los diferentes analisis: model.add_pond(frame, pond_list)
        parametros:
        frame (int)       -> la carpeta de subproceso a la que se le agrega la lista de ponderacion
        pond_list (lista) -> lista de ponderaciones en el orden en el que se encuentra en el data frame
        '''
        vul_model.frames[frame]['pond']= pond_list
        print('   ')
        print('ponderacion agregada... ')

    def add_gen_pond(self,pond_list):
        '''Se agrega la ponderacion general para el analisis final: model.add_gen_pond(pond_list)
        parametros: 
        pond_list (lista) -> lista de ponderaciones en el orden en el que aparecen en el data frame del analisis 
        '''
        for i in range(0,len(vul_model.frames_sum)):
            vul_model.frames_sum['pond'] = pond_list

    def sub_analisis(self):
        '''Corre el sub analisis para generar los rasters de cada subanalisis: model.sub_analisis()'''
        sum = np.zeros(vul_model.frames[0]['rasters'][0].shape,dtype=float)

        for i in range(0,len(vul_model.frames)): 
            for j in range(0,len(vul_model.frames[i])):
                sum = sum + (vul_model.frames[i]['rasters'][j] * vul_model.frames[i]['pond'][j] )
                vul_model.frames_sum['raster sum'][j] = sum

    def analisis(self):
        '''Corre el analisis principal para generar el raster final: model.analisis()'''
        vul_model.g_sum = np.zeros(vul_model.frames_sum['raster sum'][0].shape,dtype=float)
        for i in range(0,len(vul_model.frames_sum)): 
            vul_model.g_sum = vul_model.g_sum + (vul_model.frames_sum['raster sum'][i] * vul_model.frames_sum['pond'][i] )
            vul_model.frames_sum['raster sum'][i] = vul_model.g_sum
        vul_model.g_sum = vul_model.NormalizeData(vul_model.g_sum)

    def describe():
        ''' imprime una descripcion del modelo con el nombre de las capas que se usaran con cada sub analisis y sus ponderaciones ademas de la ponderacion final
        model.describe()'''

        for i in range(0,len(vul_model.carpetas)):
            print('sub carpeta de analisis: '+vul_model.carpetas[i])
            print('')
            print(vul_model.frames[i][['rast_name', 'pond']])
            print('**********************************************************************************')
        print('')
        print(' ponderacion de analisis final')
        print('')
        print(vul_model.frames_sum[['categoria','pond']])

    def plot_sub_analisis (self,word):
        '''Grafica individualemnte el sub analisis generado despues de correr el subanalisis model.plot_sub_analisis(word)
        parametros: 
        mord (str) -> nombre del subanalisis, nombre de la carpeta que contiene el sub analisis
        '''
    
        plt.figure(figsize = (30,20))
        plt.imshow(vul_model.frames_sum[vul_model.frames_sum['categoria']==word]['raster sum'][0])
        plt.colorbar()
        plt.show()

    def plot_analisis (self): 
        ''' Grafica el analisis despues de usar el comando de analisis model.plot_analisis()'''

        plt.figure(figsize = (30,20))
        plt.imshow(vul_model.g_sum )
        plt.colorbar()
        plt.show()

    def export_raster(self, name, res): 
        ''' Exporta el raster final como archivo tif export_raster(name, res) 
        parametros:
        name (str)  -> nombre del archivo, debe contener su extencion, normalmente es *.tif
        res (int)   -> resolucion del raster a utilizar, normalmente entre 5 y 30
        '''

        a=rst.open( vul_model.direccion+'/'+vul_model.carpetas[len(vul_model.carpetas)-1]+'/'+vul_model.archivos[len(vul_model.archivos)-1])
        bounds=[0,0]
        bounds[0] = a.bounds[3]
        bounds[1] = a.bounds[0] 

        path3=vul_model.direccion+'/'+name

        transform = from_origin(bounds[1],bounds[0], res, res)

        new_dataset = rst.open(path3, 
                                'w', 
                                driver='GTiff',
                                height = vul_model.g_sum.shape[0], 
                                width = vul_model.g_sum.shape[1],
                                count=1, 
                                dtype=str(vul_model.g_sum.dtype),
                                crs='+proj=utm +zone=11 +datum=WGS84 +units=m +no_defs' ,
                                transform=transform)

        new_dataset.write(vul_model.g_sum, 1)
        new_dataset.close()
        print('exportacion completa')        

    def print_subC(self,sub_carp): #imprimir todos los rasters
        ''' imprime todos los rasters de el sub analisis que se solicite print_subC(sub_carp) 
        parametros: 
        sub_carp (int) -> subcarpeta de analisis que desea graficar
        '''

        col=3
        row= (int(len(vul_model.frames[sub_carp])/3))+1

        fig, axs = plt.subplots(row, col,figsize=(15,15))

        nn = 0 

        for i in range(0,row):
            for j in range(0,col):

                if nn >len(vul_model.frames[sub_carp])-1: 
                    break
                else:
                    axs[i,j].imshow(vul_model.frames[sub_carp]['rasters'][nn])
                    axs[i,j].set_title(vul_model.frames[sub_carp]['rast_name'][nn])
                    nn=nn+1
