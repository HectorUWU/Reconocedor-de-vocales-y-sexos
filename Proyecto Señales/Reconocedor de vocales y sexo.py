import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
from scipy.fftpack import fft
import numpy as np
from os import scandir
import os
from sklearn import svm

def DFT_slow(x):
    """Compute the discrete Fourier Transform of the 1D array x"""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    n = np.arange(N)
    k = n.reshape((N, 1))
    M = np.exp(-2j * np.pi * k * n / N)
    return np.dot(M, x)

def FFT(x):
    """A recursive implementation of the 1D Cooley-Tukey FFT"""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    
    if N % 2 > 0:
        raise ValueError("size of x must be a power of 2")
    elif N <= 32:  # this cutoff should be optimized
        return DFT_slow(x)
    else:
        X_even = FFT(x[::2])
        X_odd = FFT(x[1::2])
        factor = np.exp(-2j * np.pi * np.arange(N) / N)
        return np.concatenate([X_even + factor[:N / 2] * X_odd,
                               X_even + factor[N / 2:] * X_odd])

def read_multiples_wav():
    '''Lee archivos wav, en una carpeta, aplica fft y regresa un arreglo con los premedios de cada vocal EN DESUSO '''
    vocals = ['A','E','I']
    dic = []
    for vocal in vocals:
        files = lsi(str(os.getcwd())+'/'+vocal)
        vec,i = 0,0
        for file in files:
            rate, data = wav.read((str(os.getcwd())+'/'+vocal+'/'+file))
            data = np.setdiff1d(data,0)
            data = np.array(data[:32])
            fft_out = FFT(data)
            mx=np.amax(fft_out)
            vec += mx
            i+=1
        prom = vec/i
        dic.append(prom)
    return dic

def make_x_y(labels):
    '''Lee los archivos wav en una carpeta aplica fft y guarda la componenete de mayor frecuencia, 
    regresa el arreglo con dicha componente y la etiqueta de cada cada archivo'''
    x,y = [],[]
    i=0
    for label in labels:
        files = lsi(str(os.getcwd())+'/'+label)
        for file in files:
            rate, data = wav.read(str(os.getcwd())+'/'+label+'/'+file)
            data = np.setdiff1d(data,0)
            data = np.array(data[:32])
            fft_out = FFT(data)
            fft_mag=np.absolute(fft_out)
            mf=np.where(fft_mag==np.amax(fft_mag)) 
            comp=fft_out[mf]
            x.append(comp)
            y.append(label)
        i+=1
    return x,y

def make_prediction(proms,fname):
    '''Hace una prediccion de una vocal tomando los promedios y el nombre del archivo a abrir
    EN DESUSO'''
    rate, data = wav.read(fname)
    data = np.setdiff1d(data,0)
    data = np.array(data[:32])
    fft_out = FFT(data)
    mf=np.amax(fft_out) 
    vec=np.absolute(proms-mf)
    print(vec)
    i = np.where(vec==np.amin(vec))
    if(i[0]==0):
        print('A')
    elif(i[0]==1):
        print('E')
    elif(i[0]==2):
        print('I')
    elif(i[0]==3):
        print('O')
    elif(i[0]==4):
        print('U')
    else:
        print('Disculpa no te entendi')
    
        
def make_model(x,y):
    '''Crea un modelo de ML basado en el algoritmo de clasificacion del Suport Vector Machine
    regresa el modelo entrenado'''
    clf = svm.SVC(gamma='auto')
    clf.fit(x, y)  
    return clf 

def make_prediction_svm(model,fname):
    '''Hace una prediccion recibiendo el modelo entrenado y el nombre del archivo a leer
    por modelos de sckit learn se tiene que hacer dos predicciones pero solo retorna el valor a predecir'''
    rate, data = wav.read(fname)
    data = np.setdiff1d(data,0)
    data = np.array(data[:32])
    fft_out = FFT(data)
    fft_mag=np.absolute(fft_out)
    mf=np.where(fft_mag==np.amax(fft_mag)) 
    comp=fft_out[mf]
    r= float(np.real(comp))
    i = float(np.imag(comp))
    vec1,vec=[],[]
    vec1.append(r)
    vec1.append(i)
    vec.append(vec1)
    rate, data = wav.read('i.wav')
    data = np.setdiff1d(data,0)
    data = np.array(data[:32])
    fft_out = FFT(data)
    fft_mag=np.absolute(fft_out)
    mf=np.where(fft_mag==np.amax(fft_mag)) 
    comp=fft_out[mf]
    vec1=[]
    r= float(np.real(comp))
    i = float(np.imag(comp))
    vec1.append(r)
    vec1.append(i)
    vec.append(vec1)
    vec = np.asarray(vec)
    return(model.predict(vec)[0])
    

def make_X(x,y):
    '''crea la matriz X reciviendo las componenetes reales e imaginarias por separado'''
    New_X=[]
    for i in range(len(y)):
        new_X=np.append(x[i], y[i])
        New_X.append(new_X)
    New_X = np.asarray(New_X)
    return New_X
            
def lsi(path):
    '''Lee todos los archivos dentro de path'''
    return([obj.name for obj in scandir(path) if obj.is_file()])
    
if __name__ == "__main__":
    x,y=make_x_y(['A','E','I','O','U'])
    r= np.real(x)#obtiene las componenetes reales
    i = np.imag(x)#obtiene las componenetes imaginarias
    X = make_X(r,i)
    modelV=make_model(X,y)#entrena el modelo para predecir vocales
    print(make_prediction_svm(modelV,'i.wav'))
    xs,ys=make_x_y(['H','M'])
    rs= np.real(xs)#obtiene las componenetes reales
    iS = np.imag(xs)#obtiene las componenetes imaginaria
    XS = make_X(rs,iS)
    modelSexo=make_model(XS,ys)#entrena el modelo para predecir sexos
    print(make_prediction_svm(modelSexo,'i.wav'))