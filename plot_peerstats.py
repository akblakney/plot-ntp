import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from utils import plot_offset,  plot_hlines, convert_ms, remove_outliers, \
  add_sel, read_rawstats

COLORS = ['r','g','b','c','m','y','k','darkgoldenrod','teal','forestgreen','royalblue' ]
PI_ADDRESS = '192.168.1.10'

def set_ax_disp(ax, df, micro_scale):
  if micro_scale:
    ax.set_ylabel('offset (us)')
    plot_hlines(ax, df['seconds'], [-50,-20,-10,10,20,50])
  else:
    ax.set_ylabel('offset (ms)')
    plot_hlines(ax, df['seconds'], [-10,-5,-1,1,5,10])
    

# returns a ready to use dataframe from peerstats file
def read_peerstats(filename, micro_scale, threshold=None, start=0):
  df = pd.read_csv(filename, sep=' ', header=None, \
    names=['MJD', 'seconds', 'address','status','offset','delay','dispersion', \
    'RMS jitter'])
  df = convert_ms(df)
  if micro_scale:
    df = convert_ms(df)
  df = remove_outliers(df, threshold, start)
  df = add_sel(df)
  return df

def read_peerstats_from_raw(filename, threashold=None,start=0):
  #df = pd.read_csv(filename, sep=' ', header=None,\
  #  names=[''])
  return read_rawstats(filename)

def plot_by_select(df, micro_scale,line):
  # define different peer selection statuses
  rej = df[df.select == 0]
  san = df[df.select == 1]
  cor = df[df.select == 2]
  can = df[df.select == 3]
  out = df[df.select == 4]
  syn_ex = df[df.select == 5]
  syn_ok = df[df.select == 6]
  gps  = df[df.select == 7]
  pi = df[df.address == PI_ADDRESS]

  # plot by selection status
  fig, ax = plt.subplots()
  plot_offset(rej,'b',ax,'rejected',micro_scale,line)
  plot_offset(san,'g',ax,'sanity',micro_scale,line)
  plot_offset(cor,'r',ax,'correctness',micro_scale,line)
  plot_offset(can,'c',ax,'candidate',micro_scale,line)
  plot_offset(out,'m',ax,'outlier',micro_scale,line)
  plot_offset(syn_ex,'y',ax,'synchronized ex',micro_scale,line)
  plot_offset(syn_ok,'k',ax,'synchronized ok',micro_scale,line)
  plot_offset(gps,'g',ax,'PPS',micro_scale,line)
  plot_offset(pi, 'g',ax,'Pi',micro_scale,line)
  return ax

def plot_by_server(df, servers,micro_scale,line):

  # if none then add all
  if servers is None:
    servers = df['address'].unique()
    print(servers)
  fig, ax = plt.subplots()
  for i in range(len(servers)):
    plot_offset(df[df.address == servers[i]], COLORS[i], ax, servers[i],micro_scale,line)
  return ax
  
def set_options():
  filename = '/var/log/ntpsec/peerstats'
  th = None
  start = 0
  by_server = False
  servers = None
  micro_scale = False
  line = False
  use_rawstats = False
  no_scale = False

  # to specify threshold of offset in ms to tolerate
  if '-t' in sys.argv:
    ind = sys.argv.index('-t')
    th = int(sys.argv[ind + 1])

  # to specify number of seconds to begin at
  if '-s' in sys.argv:
    ind = sys.argv.index('-s')
    start = int(sys.argv[ind + 1])

  # to specify particular ip's to plot
  if '-ip' in sys.argv:
    by_server = True
    ind = sys.argv.index('-ip')
    if sys.argv[ind+1] == '.':
      servers = None
    else:
      servers = sys.argv[ind+1]
      servers = servers.split(',')

  # to use microseconds scale
  if '-u' in sys.argv:
    micro_scale = True

  # to specify a file (otherwise default peerstats is used)
  if '-f' in sys.argv:
    ind = sys.argv.index('-f')
    filename = sys.argv[ind+1]

  # to plot lines connecting the scatter points
  if '-l' in sys.argv:
    line = True

  if '-r' in sys.argv:
    use_rawstats = True

  if '-ns' in sys.argv:
    no_scale = True 

  return filename, th, start, by_server, \
    servers, micro_scale, line, use_rawstats, no_scale


def main():
  filename, th, start, by_server, servers, micro_scale, line, use_rawstats, \
    no_scale  = set_options()
  if use_rawstats:
    df = read_peerstats_from_raw(filename)
  else:
    df = read_peerstats(filename, micro_scale, th, start)
  if by_server:
    ax = plot_by_server(df, servers, micro_scale,line)
  else:
    ax = plot_by_select(df, micro_scale,line)


  # set ax stuff
  set_ax_disp(ax, df, micro_scale)

  # setup cringe legend stuff
  handles, labels = plt.gca().get_legend_handles_labels()
  by_label = dict(zip(labels,handles))
  plt.legend(by_label.values(),by_label.keys())
  #ax = plt.gca()
  if micro_scale:
    ax.set_ylim([-100,100])
  elif no_scale:
    pass
  else:
    ax.set_ylim([-20,20])
  plt.show()

if __name__ == '__main__':
  main()
