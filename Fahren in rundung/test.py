import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. Create Sample Data ---
# Replace this with loading your actual Excel file
data = {
    'zeit (min)': [0, 30, 30.07, 35.89, 36.24, 41.48, 42.61, 44.24, 45.66, 46.00, 46.29, 46.36, 76.36, 76.72, 77.07, 78.48, 80.12, 81.25, 86.52, 86.87, 92.63, 92.70],
    'geschwindigkeit (km/h)': [0, 3, 3, 18, 18, 18, 18, 18, 3, 3, 0, 0, 3, 3, 18, 18, 18, 18, 18, 3, 3, 0],
    'weg (km)': [0, 1.74, 292.82, 336.22, 1907.65, 2247.3, 2736.9, 3161.75, 3205.15, 3219.59, 3221.33, 3221.33, 3219.59, 3205.15, 3161.75, 2736.9, 2247.3, 1907.65, 325.41, 282.01, -5.98, -7.72],
    'sektion': [1, 1, 1, 1, 2, 2, 3, 4, 5, 5, 6, 6, 6, 6, 6, 5, 5, 4, 3, 2, 2, 1]
}
df = pd.DataFrame(data)

# --- 2. Calculate Section Start and End Times ---
# This is crucial for drawing the background sections
sections = []
for section_num in sorted(df['sektion'].unique()):
    section_data = df[df['sektion'] == section_num]
    start_time = section_data['zeit (min)'].min()
    end_time = section_data['zeit (min)'].max()
    sections.append({'section': section_num, 'start': start_time, 'end': end_time})

# --- 3. Create the Plot ---
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add Speed Trace (Primary Y-axis)
fig.add_trace(
    go.Scatter(x=df['zeit (min)'], y=df['geschwindigkeit (km/h)'], name='Geschwindigkeit (km/h)',
               mode='lines+markers', line=dict(color='blue')),
    secondary_y=False,
)

# Add Distance Trace (Secondary Y-axis)
fig.add_trace(
    go.Scatter(x=df['zeit (min)'], y=df['weg (km)'], name='Weg (km)',
               mode='lines+markers', line=dict(color='red')),
    secondary_y=True,
)

# Add Background Rectangles for Sections
colors = ['rgba(173, 216, 230, 0.3)', 'rgba(144, 238, 144, 0.3)', 'rgba(255, 255, 0, 0.3)',
          'rgba(255, 165, 0, 0.3)', 'rgba(255, 99, 71, 0.3)', 'rgba(238, 130, 238, 0.3)',
          'rgba(175, 238, 238, 0.3)', 'rgba(255, 228, 196, 0.3)', 'rgba(216, 191, 216, 0.3)',
          'rgba(192, 192, 192, 0.3)'] # A list of colors for each section

for i, section in enumerate(sections):
    color = colors[i % len(colors)] # Cycle through colors if more sections than colors
    fig.add_vrect(x0=section['start'], x1=section['end'],
                  fillcolor=color, opacity=0.5, layer="below", line_width=0,
                  annotation_text=f"s {section['section']}", annotation_position="top left")

  
    plot_bgcolor='light', # Hintergrundfarbe des Plotbereichs 
    paper_bgcolor='white', # Hintergrundfarbe 
    legend=dict(
        x=1.02,        # 
        y=1,           # Y-Position relativ zum Plotbereich (1.0 ist ganz oben)
        xanchor='left',# Der "Ankerpunkt" der Legende ist links von der X-Position
        yanchor='top', # Der "Ankerpunkt" der Legende ist oben von der Y-Position
        bgcolor='rgba(255,255,255,0.8)', # Hintergrundfarbe der Legendenbox
        bordercolor='Black', # Rahmenfarbe der Legendenbox
        borderwidth=1 # Rahmenbreite der Legendenbox
    )


fig.update_yaxes(title_text='Geschwindigkeit (km/h)', secondary_y=False)
fig.update_yaxes(title_text='Weg (km)', secondary_y=True)


fig.show()