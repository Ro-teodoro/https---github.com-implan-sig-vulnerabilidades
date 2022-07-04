
#importamos librerias
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import rasterio as rst
from rasterio.transform import from_origin


class vul_model:




    def NormalizeData(data):
    
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    #constructor: 
    def __init__(self, direccion):

        vul_model.direccion = direccion

        p=os.listdir(direccion)
        vul_model.carpetas = []

        for i in p: #agregamos las carpetas a lista
            if os.path.isdir(direccion+i): 
                vul_model.carpetas.append(i)
        
        print('Se agregaron las carpetas de analisis: ' ,vul_model.carpetas )

        vul_model.rr =[]

        vul_model.r_names =[]

        for k in range(0,len(vul_model.carpetas)): #importamos todos lo datos
            print('  ')
            print('cargando capas de: '+ vul_model.carpetas[k])
            print('  ')
            r = []
            r_n = []
            path2 = path + vul_model.carpetas[k]
            vul_model.archivos = os.listdir( path2)
            for i in range(0,len(vul_model.archivos)):

                print('cargando: '+path + path2+ '/' +vul_model.archivos[i])
                r_n.append(vul_model.archivos[i])
                r.append( rst.open(path2+ '/' +vul_model.archivos[i]).read(1))

            vul_model.r_names.append(r_n)
            vul_model.rr.append(r)

        print(' ')    
        print('ha terminado la carga')    

        print('  ')
        print('filtrando rasters...')
        shapes0=[]
        shapes1=[]

        for k in range(0,len(vul_model.rr)):
            for i in vul_model.rr[k]:
                shapes0.append(i.shape[0])
                shapes1.append(i.shape[1])

        min1=min(shapes0)
        min2=min(shapes1)

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
        vul_model.frames[carp]['rasters'][capa] = vul_model.NormalizeData(vul_model.frames[carp]['rasters'][capa][0])

    def norm_sum(self):
        for i in range(0, len(vul_model.frames_sum)):
            vul_model.frames_sum['raster sum'][i] = vul_model.NormalizeData( vul_model.frames_sum['raster sum'][i])

    def add_pond(self, frame, pond_list):
        vul_model.frames[frame]['pond']= pond_list
        print('   ')
        print('ponderacion agregada... ')

    def add_gen_pond(seld,pond_list):
        for i in range(0,len(vul_model.frames_sum)):
            vul_model.frames_sum['pond'] = pond_list

    def sub_analisis(self):

        sum = np.zeros(vul_model.frames[0]['rasters'][0].shape,dtype=float)

        for i in range(0,len(vul_model.frames)): 
            for j in range(0,len(vul_model.frames[i])):
                sum = sum + (vul_model.frames[i]['rasters'][j] * vul_model.frames[i]['pond'][j] )
                vul_model.frames_sum['raster sum'][j] = sum

    def analisis(self):

        vul_model.g_sum = np.zeros(vul_model.frames_sum['raster sum'][0].shape,dtype=float)
        for i in range(0,len(vul_model.frames_sum)): 
            vul_model.g_sum = vul_model.g_sum + (vul_model.frames_sum['raster sum'][i] * vul_model.frames_sum['pond'][i] )
            vul_model.frames_sum['raster sum'][i] = vul_model.g_sum
        vul_model.g_sum = vul_model.NormalizeData(vul_model.g_sum)
   
    def describe():
        print(vul_model.carpetas)

    def plot_sub_analisis (self,word):
        plt.figure(figsize = (30,20))
        plt.imshow(tijuana.frames_sum[tijuana.frames_sum['categoria']==word]['raster sum'][0])
        plt.colorbar()
        plt.show()

    def plot_analisis (self):
        plt.figure(figsize = (30,20))
        plt.imshow(vul_model.g_sum )
        plt.colorbar()
        plt.show()


    def export_raster(self, name, res): #exportar raster

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

