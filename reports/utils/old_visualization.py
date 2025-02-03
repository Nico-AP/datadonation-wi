import plotly.graph_objects as go
import pandas as pd
from .utils import party_colors, parties_order
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
from plotly.subplots import make_subplots
import io
import base64

# Common plot settings
PLOT_CONFIG = {
    'responsive': True,
    'displayModeBar': False,
    'staticPlot': False,  # Need this false to allow hovering
    'scrollZoom': False,
    'doubleClick': False,
    'showAxisDragHandles': False,
    'showAxisRangeEntryBoxes': False,
    'modeBarButtonsToRemove': [
        'zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
        'autoScale2d', 'resetScale2d', 'hoverClosestCartesian',
        'hoverCompareCartesian', 'toggleSpikelines'
    ]
}

# For plots where we want no interaction at all
STATIC_PLOT_CONFIG = {
    'responsive': True,
    'displayModeBar': False,
    'staticPlot': True  # This disables all interactions
}

PLOT_FONT = dict(
    size=25,
    color='#444',
    family='Source Sans Pro, Arial, sans-serif'
)

PLOT_LAYOUT = dict(
    autosize=True,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=PLOT_FONT,
    margin=dict(
        r=50,  # These margins will be automatically adjusted on mobile
        t=50,
        l=50,
        b=50,
        autoexpand=True  # This helps with responsiveness
    ),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)

# helper functions
def load_user_data(user_data_path):
    """Helper function to load and clean user data JSON"""
    try:
        with open(user_data_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find the last closing brace of the main JSON object
            last_brace = content.rstrip().rfind('}')
            if last_brace > 0:
                # Take only the content up to and including the last brace
                cleaned_content = content[:last_brace + 1]
                return json.loads(cleaned_content)
            else:
                raise json.JSONDecodeError("No valid JSON object found", content, 0)
    except Exception as e:
        print(f"Error loading user data: {str(e)}")
        return None

def hex_to_rgba(hex_color, opacity=0.6):
    """Convert hex color to rgba with given opacity"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r},{g},{b},{opacity})'

def create_plot_html(fig, config=None):
    """Helper function to standardize plot HTML generation"""
    return fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config=config or STATIC_PLOT_CONFIG
    )

def update_plot_style(fig):
    """Apply standard styling to plot"""
    fig.update_layout(**PLOT_LAYOUT)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')



### 5. User feed wordcloud
def create_user_feed_wordcloud(df_posts, user_data_path):
    """Create wordcloud for user's watched political videos"""
    # Get user's watched video hashtags
    with open(user_data_path, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    
    browsing_history = user_data['Activity']['Video Browsing History']['VideoList']
    browsing_df = pd.DataFrame(browsing_history)
    
    def extract_video_id(url):
        try:
            return int(url.strip('/').split('/')[-1])
        except:
            return None
    
    # Get watched video IDs and match with posts
    watched_video_ids = set(browsing_df['Link'].apply(extract_video_id))
    matched_videos = df_posts[df_posts['id'].isin(watched_video_ids)]
    
    # Extract hashtags
    def get_hashtags(descriptions):
        hashtags = []
        for desc in descriptions:
            if isinstance(desc, str):
                tags = re.findall(r'#(\w+)', desc.lower())
                hashtags.extend(tags)
        return Counter(hashtags)
    
    # Get frequencies for user's feed
    user_freq = get_hashtags(matched_videos['video_description'])
    
    # Create wordcloud
    user_cloud = WordCloud(
        width=800,
        height=800,
        background_color='white',
        colormap='Reds',  # Red theme for user's feed
        max_words=100,
        prefer_horizontal=0.7,
        min_font_size=10,
        max_font_size=100
    ).generate_from_frequencies(user_freq)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot wordcloud
    ax.imshow(user_cloud, interpolation='bilinear')
    ax.axis('off')
    
    # Convert to HTML
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=600)
    buf.seek(0)
    plt.close(fig)
    
    # Create HTML with the image
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Update HTML wrapper to use full width
    html = f'''
    <div style="width:100%; margin:0 auto;">
        <img src="data:image/png;base64,{img_str}" style="width:100%; height:auto;">
    </div>
    '''
    
    return {
        'html': html,
        'figure': fig
    }

### 6. All accounts wordcloud
def create_all_accounts_wordcloud(df_posts):
    """Create wordcloud for all political videos in TikTok Germany"""
    
    # Extract hashtags for all posts
    def get_hashtags(descriptions):
        hashtags = []
        for desc in descriptions:
            if isinstance(desc, str):
                tags = re.findall(r'#(\w+)', desc.lower())
                hashtags.extend(tags)
        return Counter(hashtags)
    
    # Get frequencies for all posts
    all_freq = get_hashtags(df_posts['video_description'])
    
    # Create wordcloud
    all_cloud = WordCloud(
        width=800,
        height=800,
        background_color='white',
        colormap='Blues',  # Blue theme for overall TikTok
        max_words=100,
        prefer_horizontal=0.7,
        min_font_size=10,
        max_font_size=100
    ).generate_from_frequencies(all_freq)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot wordcloud
    ax.imshow(all_cloud, interpolation='bilinear')
    ax.axis('off')
    
    # Convert to HTML
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=600)
    buf.seek(0)
    plt.close(fig)
    
    # Create HTML with the image
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Update HTML wrapper to use full width
    html = f'''
    <div style="width:100%; margin:0 auto;">
        <img src="data:image/png;base64,{img_str}" style="width:100%; height:auto;">
    </div>
    '''
    
    return {
        'html': html,
        'figure': fig
    }
### 7. Party distribution all accounts temporal
def create_temporal_party_distribution_all_accounts(df):
    """Create temporal analysis visualization showing videos per day"""
    # Convert timestamp to datetime
    df['date'] = pd.to_datetime(df['create_time'], unit='s')
    
    # Resample to days (D)
    df_temporal = df.set_index('date')
    
    # Create party-specific temporal analysis
    party_dfs = []
    for party in df['partei'].unique():
        if pd.isna(party) or party == 'Kein offizieller Parteiaccount':
            continue
            
        party_data = df_temporal[df_temporal['partei'] == party]
        daily_counts = party_data.resample('D')['id'].count().reset_index()
        daily_counts['partei'] = party
        party_dfs.append(daily_counts)
    
    df_party_temporal = pd.concat(party_dfs)
    
    # Create figure
    fig_party = go.Figure()
    
    # Inside create_temporal_analysis function
    for party in reversed(parties_order):
        if party not in df_party_temporal['partei'].unique():
            continue
            
        party_data = df_party_temporal[df_party_temporal['partei'] == party]
        
        # Convert hex color to rgba with transparency
        hex_color = party_colors[party].lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        rgba_color = f'rgba({r},{g},{b},0.6)'  # 0.6 for 60% opacity
        
        fig_party.add_trace(go.Scatter(
            x=party_data['date'],
            y=party_data['id'],
            name=party,
            mode='lines',
            line=dict(width=0),
            stackgroup='one',
            fillcolor=rgba_color,
            # Update hover template to only show number
            hovertemplate="%{y} Videos<extra></extra>",
            hoverlabel=dict(
                bgcolor='white',
                font_size=16,
                font_family="Source Sans Pro, Arial, sans-serif"
            ),
            # Add color to legend text
            legendgroup=party,
            showlegend=True
        ))
    
    # After all traces are added, update the layout
    fig_party.update_layout(
        xaxis_title="Datum",
        yaxis_title="Anzahl Videos",
        dragmode=False,
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,  # Position above the plot
            xanchor="center",
            x=0.5,  # Center horizontally
            font=dict(
                size=25
            )
        ),
        autosize=True,
        height=800,  # Increased height
        font=dict(
            size=25,
            color='#444'
        ),
        margin=dict(r=100, t=50, l=50, b=30),  # Adjusted margins
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',  # Show all values for a given x position
        hoverdistance=100,  # Increase hover radius
        hoverlabel=dict(
            namelength=0  # Hide trace names in hover
        ),
        # Add a title for the hover label that shows the date
        title=dict(
            text="<br>",  # Empty title to create space for hover label
            font=dict(size=1),  # Make title invisible
            pad=dict(b=0)  # Remove padding
        ),
        # Update hover template for date display
        xaxis=dict(
            hoverformat="%d.%m.%Y"  # Format for the date in hover
        )
    )
    
    # Update x-axis to show daily ticks
    fig_party.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='lightgray',
        tickangle=45,
        tickfont=dict(
            size=25,
            color='#444'
        ),
        title_font=dict(
            size=25
        ),
        # Use daily format for tick labels
        tickformat='%d.%m'
    )
    
    fig_party.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='lightgray',
        tickfont=dict(
            size=25,
            color='#444'
        ),
        title_font=dict(
            size=25
        )
    )
    
    return {
        'html': {
            'party': (
                '<div style="width: 100%; max-width: 100%; margin: 0 auto;">' +
                fig_party.to_html(
                    full_html=False, 
                    include_plotlyjs='cdn',
                    config=PLOT_CONFIG  # Use standard config that allows hovering
                ) +
                '</div>'
            )
        },
        'figure': {
            'party': fig_party
        }
    }

### 8. Party distribution all accounts treemap
def create_party_distribution_all_accounts(df_posts):
    """Create treemap chart showing video count distribution by party"""
    # Filter out non-party accounts and prepare data
    df_filtered = df_posts[df_posts['partei'].notna() & (df_posts['partei'] != 'Kein offizieller Parteiaccount')].copy()
    
    # Calculate video counts per party
    party_metrics = []
    for party in df_filtered['partei'].unique():
        party_data = df_filtered[df_filtered['partei'] == party]
        party_metrics.append({
            'party': party,
            'Videos': len(party_data)
        })
    
    # Sort by video count
    party_metrics = sorted(party_metrics, key=lambda x: x['Videos'], reverse=True)
    
    # Convert hex colors to rgba with opacity
    def hex_to_rgba(hex_color, opacity=0.6):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r},{g},{b},{opacity})'
    
    # Create treemap
    fig = go.Figure(go.Treemap(
        labels=[m['party'] for m in party_metrics],
        parents=[''] * len(party_metrics),  # Empty string as parent means root level
        values=[m['Videos'] for m in party_metrics],
        textinfo='label+value',
        marker=dict(
            colors=[hex_to_rgba(party_colors[party], 0.6) for party in [m['party'] for m in party_metrics]],
            line=dict(width=2, color='white')  # Add white borders between sections
        ),
        hovertemplate='<b>%{label}</b><br>Videos: %{value}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        font=dict(size=25)
    )
    
    # Find party with most videos
    max_party = max(party_metrics, key=lambda x: x['Videos'])
    top_party = {
        'party': max_party['party'],
        'value': max_party['Videos'],
        'color': party_colors[max_party['party']],  # Solid color for text
        'color_transparent': hex_to_rgba(party_colors[max_party['party']])  # Transparent for backgrounds
    }
    
    return {
        'html': create_plot_html(fig),
        'figure': fig,
        'top_party': top_party
    }

### 9. Views bar plots
def create_views_bars_all_accounts(df_posts):
    """Create bar charts showing total views and views per video side by side"""
    # Filter out non-party accounts and prepare data
    df_filtered = df_posts[df_posts['partei'].notna() & (df_posts['partei'] != 'Kein offizieller Parteiaccount')].copy()
    
    # Create figure with subplots side by side
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Views insgesamt', 'Views pro Video'],
        horizontal_spacing=0.15,  # Reduced from default
        column_widths=[0.5, 0.5]  # Ensure equal width
    )
    
    # Calculate total views
    total_views = []
    for party in df_filtered['partei'].unique():
        party_data = df_filtered[df_filtered['partei'] == party]
        total_views.append({
            'party': party,
            'total': party_data['view_count'].sum(),
            'per_video': party_data['view_count'].mean()
        })
    
    # Sort data
    total_sorted = sorted(total_views, key=lambda x: x['total'], reverse=False)
    per_video_sorted = sorted(total_views, key=lambda x: x['per_video'], reverse=False)
    
    # Convert hex colors to rgba with opacity
    def make_transparent(hex_color, opacity=0.6):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r},{g},{b},{opacity})'
    
    # Add total views bar
    fig.add_trace(
        go.Bar(
            y=[m['party'] for m in total_sorted],
            x=[m['total'] for m in total_sorted],
            orientation='h',
            marker_color=[make_transparent(party_colors[p]) for p in [m['party'] for m in total_sorted]],
            hovertemplate="<b>%{y}</b><br>Views insgesamt: %{x:,.0f}<extra></extra>",
            width=0.5,
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add per-video views bar
    fig.add_trace(
        go.Bar(
            y=[m['party'] for m in per_video_sorted],
            x=[m['per_video'] for m in per_video_sorted],
            orientation='h',
            marker_color=[make_transparent(party_colors[p]) for p in [m['party'] for m in per_video_sorted]],
            hovertemplate="<b>%{y}</b><br>Views pro Video: %{x:,.0f}<extra></extra>",
            width=0.5,
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Use standard settings
    fig.update_layout(**PLOT_LAYOUT)
    
    # Update axes
    for i in [1, 2]:
        fig.update_xaxes(
            title_text="Anzahl",
            title_font=dict(size=25),  # Title font size
            tickfont=dict(size=25),    # Tick label font size
            showticklabels=True,
            row=1, col=i,
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        fig.update_yaxes(
            tickangle=0,
            tickfont=dict(size=25),  # Tick label font size
            row=1, col=i,
            showgrid=False
        )
    
    # Find party with most total views and most views per video
    max_total = max(total_sorted, key=lambda x: x['total'])
    max_per_video = max(per_video_sorted, key=lambda x: x['per_video'])
    
    top_party = {
        'total': {
            'party': max_total['party'],
            'value': int(max_total['total']),
            'color': party_colors[max_total['party']],  # Solid color for text
            'color_transparent': hex_to_rgba(party_colors[max_total['party']])  # Transparent for backgrounds
        },
        'per_video': {
            'party': max_per_video['party'],
            'value': int(max_per_video['per_video']),
            'color': party_colors[max_per_video['party']],  # Solid color for text
            'color_transparent': hex_to_rgba(party_colors[max_per_video['party']])  # Transparent for backgrounds
        }
    }
    
    update_plot_style(fig)
    
    return {
        'html': create_plot_html(fig),
        'figure': fig,
        'top_party': top_party
    }

### 10. Likes bar plots
def create_likes_bars_all_accounts(df_posts):
    """Create bar charts showing total likes and likes per video side by side"""
    # Filter out non-party accounts and prepare data
    df_filtered = df_posts[df_posts['partei'].notna() & (df_posts['partei'] != 'Kein offizieller Parteiaccount')].copy()
    
    # Create figure with subplots side by side
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Likes insgesamt', 'Likes pro Video'],
        horizontal_spacing=0.15
    )
    
    # Calculate total likes
    total_likes = []
    for party in df_filtered['partei'].unique():
        party_data = df_filtered[df_filtered['partei'] == party]
        total_likes.append({
            'party': party,
            'total': party_data['like_count'].sum(),
            'per_video': party_data['like_count'].mean()
        })
    
    # Sort data
    total_sorted = sorted(total_likes, key=lambda x: x['total'], reverse=False)
    per_video_sorted = sorted(total_likes, key=lambda x: x['per_video'], reverse=False)
    
    # Convert hex colors to rgba with opacity
    def make_transparent(hex_color, opacity=0.6):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r},{g},{b},{opacity})'
    
    # Add total likes bar
    fig.add_trace(
        go.Bar(
            y=[m['party'] for m in total_sorted],
            x=[m['total'] for m in total_sorted],
            orientation='h',
            marker_color=[make_transparent(party_colors[p]) for p in [m['party'] for m in total_sorted]],
            hovertemplate="<b>%{y}</b><br>Likes insgesamt: %{x:,.0f}<extra></extra>",
            width=0.5,
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add per-video likes bar
    fig.add_trace(
        go.Bar(
            y=[m['party'] for m in per_video_sorted],
            x=[m['per_video'] for m in per_video_sorted],
            orientation='h',
            marker_color=[make_transparent(party_colors[p]) for p in [m['party'] for m in per_video_sorted]],
            hovertemplate="<b>%{y}</b><br>Likes pro Video: %{x:,.0f}<extra></extra>",
            width=0.5,
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Use standard settings
    fig.update_layout(**PLOT_LAYOUT)
    
    # Update axes
    for i in [1, 2]:
        fig.update_xaxes(
            title_text="Anzahl",
            title_font=dict(size=25),  # Title font size
            tickfont=dict(size=25),    # Tick label font size
            showticklabels=True,
            row=1, col=i,
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        fig.update_yaxes(
            tickangle=0,
            tickfont=dict(size=25),  # Tick label font size
            row=1, col=i,
            showgrid=False
        )
    
    # Find party with most total likes and most likes per video
    max_total = max(total_sorted, key=lambda x: x['total'])
    max_per_video = max(per_video_sorted, key=lambda x: x['per_video'])
    
    top_party = {
        'total': {
            'party': max_total['party'],
            'value': int(max_total['total']),
            'color': party_colors[max_total['party']],  # Solid color for text
            'color_transparent': hex_to_rgba(party_colors[max_total['party']])  # Transparent for backgrounds
        },
        'per_video': {
            'party': max_per_video['party'],
            'value': int(max_per_video['per_video']),
            'color': party_colors[max_per_video['party']],  # Solid color for text
            'color_transparent': hex_to_rgba(party_colors[max_per_video['party']])  # Transparent for backgrounds
        }
    }
    
    update_plot_style(fig)
    
    return {
        'html': create_plot_html(fig),
        'figure': fig,
        'top_party': top_party
    }
