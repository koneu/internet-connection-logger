import speedtest  
import os
import os.path
import pandas as pd
import numpy as np
import plotly.express as px
import threading
from datetime import datetime
import plotly.graph_objects as go
from ping3 import ping

# config
update_ud_every_seconds = 60 * 10
update_ping_every_seconds = 10

update_ping_hostname = ["google.com", "github.com", "amazon.com"]

current_data_nuOfRelevantPoints = 5

# make sure all files taht we need exist
speedtest_data_file_name = "data/speedtest.csv"
speedtest_html_file_name = "data/speedtest.html"
ping_data_file_name = "data/ping.csv"
ping_html_file_name = "data/ping.html"
pingmean_html_file_name = "data/ping_mean.html"
download_html_file_name = "data/download.html"
upload_html_file_name = "data/upload.html"

if not os.path.exists(speedtest_data_file_name):
    with open(speedtest_data_file_name, 'w'): pass

if not os.path.exists(ping_data_file_name):
    with open(ping_data_file_name, 'w'): pass


# add header in files if content got deleted
# note if the content got changed the programm will probably crash
# better would be to always check the first line
if os.stat(speedtest_data_file_name).st_size == 0:
    with open(speedtest_data_file_name,'a') as fd:
        fd.write("timestamp,download,upload,ping\n")

if os.stat(ping_data_file_name).st_size == 0:
    with open(ping_data_file_name,'a') as fd:
        entry = "timestamp"
        for host in update_ping_hostname:
            entry = entry + "," + host
        entry = entry + "\n"
        fd.write(entry)

# buisness logic
def add_ud_measurement():
    try:
        st = speedtest.Speedtest(timeout = 99)
        st.download()
        st.upload()

        entry = str(st.results.dict()["timestamp"]) + "," + \
            str(st.results.dict()["download"]/1000000) + "," + \
            str(st.results.dict()["upload"]/1000000) + "," + \
            str(st.results.dict()["ping"]) + "\n"

        with open(speedtest_data_file_name,'a') as fd:
            fd.write(entry)
    except:
        t = datetime.now()
        entry = str(t) + "," + \
            str(0) + "," + \
            str(0) + "," + \
            str(9999) + "\n"
            
        with open(speedtest_data_file_name,'a') as fd:
            fd.write(entry)

def add_ping_measurement():
    t = datetime.now()    
    entry = str(t)


    for host in update_ping_hostname:
        r = 9999
        try:
            r = ping(host)  
        except:
            pass
        entry = entry + "," + str(r)
    entry = entry + "\n"

    with open(ping_data_file_name,'a') as fd:
        fd.write(entry)

def update_ud_html():
    df = pd.read_csv(speedtest_data_file_name, sep=r',', parse_dates=True)
    fig = px.line(df, x="timestamp", y=["download", "upload"], 
            # colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_dark',
            # paper_bgcolor='rgba(0, 0, 0, 0)',
            # plot_bgcolor='rgba(0, 0, 0, 0)',
            # margin={'b': 15},
        )
    fig.write_html(speedtest_html_file_name)

def update_ping_html():
    df = pd.read_csv(ping_data_file_name, sep=r',', parse_dates=True)
    fig = px.line(df, x="timestamp", y=update_ping_hostname, 
            # colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_dark',
            # paper_bgcolor='rgba(0, 0, 0, 0)',
            # plot_bgcolor='rgba(0, 0, 0, 0)',
            # margin={'b': 15},
        )
    fig.write_html(ping_html_file_name)

    
def update_current_data_html():
    df_data = pd.read_csv(speedtest_data_file_name, sep=r',', parse_dates=True)
    df_ping = pd.read_csv(ping_data_file_name, sep=r',', parse_dates=True)

    mean_ping = df_ping.tail(current_data_nuOfRelevantPoints)

    fig_pin = go.Figure()
    for host in update_ping_hostname:
        m = mean_ping[host].mean()
        fig_pin.add_trace(go.Barpolar(
            r=mean_ping[host],
            theta = np.full(current_data_nuOfRelevantPoints,host),
            name = host + "[" + str(mean_ping[host].mean().round(3)) + "]",
        ))  
        
    fig_pin.update_traces(text=update_ping_hostname)
    fig_pin.update_layout(
        template = 'plotly_dark',
        polar_angularaxis_rotation=45,
        polar_radialaxis_ticksuffix='s'
    )

    fig_pin.write_html(pingmean_html_file_name)
    

    mean_data = df_data.tail(current_data_nuOfRelevantPoints).mean()
    max_data = df_data.max()
    
    colors = ['green', 'red']
    fig_download = go.Figure(data=[go.Pie(labels=['download','missing'],
                             values=[mean_data["download"], max_data["download"] - mean_data["download"]])])
    fig_download.update_traces(textfont_size=20,textinfo='value',
                marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    fig_download.update_layout(
        template = 'plotly_dark',
        showlegend=False
    )
    fig_download.write_html(download_html_file_name)


    
    fig_upload = go.Figure(data=[go.Pie(labels=['upload','missing'],
                             values=[mean_data["upload"], max_data["upload"] - mean_data["upload"]])])
    fig_upload.update_traces(textfont_size=20,textinfo='value',
                marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    fig_upload.update_layout(
        template = 'plotly_dark',
        showlegend=False
    )
    fig_upload.write_html(upload_html_file_name)



    
def repeat_add_ud_measurement():
  threading.Timer(update_ud_every_seconds, repeat_add_ud_measurement).start()
  add_ud_measurement()
  update_ud_html()

def repeat_add_ping_measurement():
  threading.Timer(update_ping_every_seconds, repeat_add_ping_measurement).start()
  add_ping_measurement()
  update_ping_html()
  update_current_data_html()

  


if __name__ == '__main__':
    repeat_add_ud_measurement()
    repeat_add_ping_measurement()