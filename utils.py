import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from io import StringIO

DNS = {
  '129.6.15.28' : 'time-a-g.nist.gov',
  '129.6.15.29' : 'time-b-g.nist.gov',
  '129.6.15.30' : 'time-c-g.nist.gov',
  '129.6.15.27' : 'time-d-g.nist.gov',
  '129.6.15.26' : 'time-e-g.nist.gov',
  '216.239.35.0' : 'time1.google.com',
  '216.239.35.4' : 'time2.google.com',
  '129.134.29.123' : 'time2.facebook.com',
  '128.59.0.245' : 'gnomon.cc.columbia.edu',
  '128.252.19.1' : 'ntp.wustl.edu',
  '139.78.97.128' : 'ntp.okstate.edu',
  '192.168.1.8' : 'pi.goob'

}

def hex_to_sel(row):
  h = str(row['status'])
  b = bin(int(h,16))[2:]
  # pad b first
  while len(b) < 16:
    b = '0' + b
  sel = int(b[5:8],2)
  return sel

# adds the peer selection field, by deciphering the hex ...
def add_sel(df):
  df['select'] = df.apply(lambda row: hex_to_sel(row), axis=1)
  return df

def pprint_df(df):
  with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(df)

# for eliminating a cringe server from the df
def remove_server(df, server):
  return df[df.address != server]


# this does a scatter plot of offset vs seconds
def plot_offset(df, color, ax,label, micro_scale,line=False):
  if df['seconds'].size < 1:
    return
  if label in DNS:
    label = DNS[label]
  if not line:
    df.plot.scatter(x='seconds',y='offset',color=color,ax=ax,label=label,marker='o',linestyle='solid')
  else:
    df.plot(x='seconds',y='offset',color=color,ax=ax,label=label,marker='o',linestyle='solid')
    
def plot_hlines(ax, seconds, values):
  _min = min(seconds)
  _max = max(seconds)
#  ax.hlines(-10,xmin=_min, xmax=_max,linestyles='--' ) 
#  ax.hlines(10,xmin=_min, xmax=_max,linestyles='--') 
  ax.hlines(0,xmin=_min, xmax=_max,linestyles='--',color='r') 
  for v in values:
    ax.hlines(v,xmin=_min, xmax=_max,linestyles='--')   
  
def remove_outliers(df, threshold,tt):
  if threshold is not None:
    df = df[abs(df.offset) < threshold]
  df = df[df.seconds > tt]
  return df

def convert_ms(df):
  df['offset'] *= 1000
  df['delay'] *= 1000
  return df

# for reading rawstats which has lines that need to be skipped
def skip(line):
  #return ':' in line or '192.168.1.240' in line
  return ':' in line

# return dataframe with rawstats info
# include MJD,s, IPaddr, {orig, recv, trns,dest}
# also sets up the offsets, delay, and delay1, delay2
def read_rawstats(filename):
  # if it is compressed data
#  if filename[-3:] == '.gz':
#    with open(filename, 'rb') as fd:
#      gzip_file = gzip.GzipFile(fileobj=fd)
#      lines = 
#  with open(filename) as file:
#    for line in file:
#      print(line)
  lines = ''.join([line for line in open(filename) if not skip(line)])
  cringe = 'cringe'
  df = pd.read_csv(StringIO(lines), sep=' ',header=None,usecols=[0,1,2,4,5,6,7],\
    names=['MJD','seconds', 'address','orig','recv','tx','dest'])

  # remove outgoing
  #df = df[df.address != '192.168.1.8']
  
  # put in ms
  df['d1'] = 1000*(df['recv'] - df['orig'])
  df['d2'] = 1000*(df['dest'] - df['tx'])
  df['delay'] = df['d1'] + df['d2']
  df['offset'] = .5*(df['d1']-df['d2'])
  #df['offset'] = .5*(df['d1']+df['d2']) 
  return df

