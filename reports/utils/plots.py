import json
import pandas as pd
from .utils import party_colors, parties_order
import plotly.graph_objects as go
from collections import Counter
import re
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
from wordcloud import WordCloud

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


### helper

def hex_to_rgba(hex_color, opacity=0.6):
    """Convert hex color to rgba with given opacity"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r},{g},{b},{opacity})'



#### 1. User consumption stats
def create_user_consumption_stats(matched_videos, user_data):
    """Create user consumption statistics"""
    try: return f"""
            <ul class="stats-list">
                <li>Seit dem Ampel-Aus hast du insgesamt <span class="stats-value">{len(user_data):,}</span> Videos auf TikTok angesehen</li>
                <li>Davon waren <span class="stats-value">{len(matched_videos):,}</span> Videos politisch.</li>
                <li>Das sind <span class="stats-value">{(len(matched_videos)/len(user_data)*100):.1f}%</span> der Videos, die du gesehen hast.</li>
            </ul>
        """
    
    except Exception as e:
        print(f"Error processing user data: {str(e)}")
        return "<p>Entschuldigung, deine Nutzungsdaten konnten nicht analysiert werden.</p>"


### 2. Party distribution in user feed
def create_party_distribution_user_feed(matched_videos):
    """Create party distribution visualization using treemap"""


    # Filter out non-party accounts and count videos by party
    party_counts = matched_videos[matched_videos['partei'] != 'Kein offizieller Parteiaccount']['partei'].value_counts()

    # Only create treemap if we have data
    if len(party_counts) == 0:
        print("No party data found!")
        return '<div>No political party videos found in your feed.</div>'

    # Create treemap figure
    fig_party = go.Figure(go.Treemap(
        labels=party_counts.index,
        parents=[''] * len(party_counts),
        values=party_counts.values,
        textinfo='label+value',
        textfont=dict(
            size=28,
            family='Source Sans Pro, Arial, sans-serif'
        ),
        textposition='middle center',
        hoverinfo='skip',
        text=[f"{party}<br>{count} Videos" for party, count in zip(party_counts.index, party_counts.values)],
        texttemplate="%{text}",
        marker=dict(
            colors=[
                f'rgba({int(party_colors[party].lstrip("#")[0:2], 16)}, '
                f'{int(party_colors[party].lstrip("#")[2:4], 16)}, '
                f'{int(party_colors[party].lstrip("#")[4:6], 16)}, 0.6)'
                for party in party_counts.index
            ]
        )
    ))
    
    # Update layout
    fig_party.update_layout(
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        autosize=True,
        height=600,
        margin=dict(t=0, l=25, r=25, b=25),
        hovermode=False  # Disable hover mode
    )
    
    return {
        'html': {
            'party': (
                '<div style="width: 100%; max-width: 100%; margin: 0 auto;">' +
                fig_party.to_html(
                    full_html=False, 
                    include_plotlyjs='/static/reports/js/plotly-3.0.0.min.js',
                    config=STATIC_PLOT_CONFIG  # Use standard config that allows hovering
                ) +
                '</div>'
            )
        },
        'figures': {
            'party': fig_party
        }
    }

### 3. Party distribution on feed temporal
def create_temporal_party_distribution_user_feed(matched_videos):
    """Create weekly watched videos visualization with stacked area chart"""
    
    # Convert timestamp to datetime and filter non-party accounts
    matched_videos['date'] = pd.to_datetime(matched_videos['create_time'])
    matched_videos = matched_videos[matched_videos['partei'] != 'Kein offizieller Parteiaccount']

    # Set date as index and resample by week
    matched_videos.set_index('date', inplace=True)
    
    # Group by week and party
    daily_party_counts = matched_videos.groupby([pd.Grouper(freq='D'), 'partei']).size().reset_index(name='count')
    daily_party_counts['date'] = daily_party_counts['date'].dt.normalize()  # Normalize dates to midnight

    # Get min and max dates to create full date range
    min_date = matched_videos.index.min()
    max_date = matched_videos.index.max()
    print("\nDate range:")
    print(f"Min date: {min_date}")
    print(f"Max date: {max_date}")
    
    # Create complete date range by week
    full_date_range = pd.date_range(
        start=min_date.normalize(),
        end=max_date.normalize(),
        freq='D'
    )
    
    # Create a DataFrame with all weeks and parties
    all_parties = matched_videos['partei'].unique()
    index = pd.MultiIndex.from_product(
        [full_date_range, all_parties],
        names=['date', 'partei']
    )
    
    # Reindex with all dates and fill missing values with 0
    daily_party_counts = daily_party_counts.set_index(['date', 'partei'])
    daily_party_counts = daily_party_counts.reindex(index, fill_value=0).reset_index()
    
    # Create figure
    fig = go.Figure()
    
    # Add traces in reverse order (bottom to top)
    for party in reversed(parties_order):
        if party not in daily_party_counts['partei'].unique():
            continue
            
        party_data = daily_party_counts[daily_party_counts['partei'] == party]
        
        # Convert hex color to rgba with transparency
        hex_color = party_colors[party].lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        rgba_color = f'rgba({r},{g},{b},0.6)'
        
        fig.add_trace(go.Scatter(
            x=party_data['date'],
            y=party_data['count'],
            name=party,
            mode='lines',
            line=dict(width=0),
            stackgroup='one',
            fillcolor=rgba_color,
            hovertemplate="%{y}<br>" +
                         "<extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Datum",
        yaxis_title="Anzahl gesehener Videos pro Tag",
        hovermode='x unified',
        dragmode=False,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(
                size=25
            )
        ),
        autosize=True,
        height=800,
        font=dict(
            size=25,
            color='#444'
        ),
        margin=dict(r=100, t=50, l=50, b=30),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(
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
        # Format tick labels to show dates
        ticktext=[d.strftime('%d.%m') for d in daily_party_counts['date'].unique()],
        tickvals=daily_party_counts['date'].unique()
    )
    
    fig.update_yaxes(
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
        'html': (
            '<div class="weekly-watched-container">'
            '<div style="width: 100%; max-width: 100%; margin: 0 auto; padding: 0;">' +
            fig.to_html(
                full_html=False, 
                include_plotlyjs='/static/reports/js/plotly-3.0.0.min.js',
                config=PLOT_CONFIG  # Use standard config that allows hovering
            ) +
            '</div>'
            '</div>'
        ),
        'figure': fig
    }

### 4. Top videos table
def create_top_videos_table(matched_videos):

    # Get top 5 videos with hashtags
    matched_videos = matched_videos.sort_values('view_count', ascending=False)
    top_5_videos = matched_videos.head(5)[['username', 'view_count', 'video_id', 'partei', 'hashtags']]
    
    def format_hashtags(hashtags):
        if not hashtags:  # Check if list is empty
            return ""
        # Filter out common tags
        filtered_tags = [tag for tag in hashtags if tag.lower() not in {'fyp', 'foryou', 'viral', 'trending', 'fy', 'fürdich', 'capcut'}]
        return " ".join([f"<span class='hashtag'>#{tag}</span>" for tag in filtered_tags[:5]])
    
    top_videos_html = """
        <table class="top-videos-table">
            <thead>
                <tr>
                    <th>Account</th>
                    <th>Views</th>
                    <th>Hashtags</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in top_5_videos.iterrows():
        video_link = f"https://www.tiktok.com/share/video/{row['video_id']}"
        hashtags = format_hashtags(row['hashtags'])
        
        top_videos_html += f"""
            <tr>
                <td class="account-cell">
                    <span class="account-name">@{row['username']}</span>
                </td>
                <td class="views-cell">{row['view_count']:,.0f}</td>
                <td class="hashtags-cell">{hashtags}</td>
                <td class="link-cell">
                    <a href="{video_link}" target="_blank" class="video-link">Video ansehen</a>
                </td>
            </tr>
        """
    
    top_videos_html += """
            </tbody>
        </table>
    """
    
    return top_videos_html


### 5. User feed wordcloud
def create_user_feed_wordcloud(matched_videos):
    """Create wordcloud for user's watched political videos"""

    # Extract hashtags
    def get_hashtags(matched_videos):
        # Initialize empty list to store all hashtags
        all_hashtags = []
        
        # Iterate through each video's hashtags
        for hashtag_list in matched_videos['hashtags']:
            if hashtag_list:  # Check if list exists and is not empty
                # Filter out common/unwanted tags
                filtered_tags = [
                    tag.lower() for tag in hashtag_list 
                    if tag.lower() not in {
                        'fyp', 'foryou', 'viral', 'trending', 
                        'fy', 'fürdich', 'capcut'
                    }
                ]
                all_hashtags.extend(filtered_tags)
        
        # Return Counter object with hashtag frequencies
        return Counter(all_hashtags)
    
    # Get frequencies for user's feed
    user_freq = get_hashtags(matched_videos)
    
    if not user_freq:
        return {'html': '<div>Keine Hashtags gefunden.</div>', 'figure': None}
        
        
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
def create_hashtag_cloud_germany(df_posts):
    """Create wordcloud for all political videos in TikTok Germany"""

    # Extract hashtags
    def get_hashtags(hashtag_col):
        # Initialize empty list to store all hashtags
        all_hashtags = []
        
        # Iterate through each video's hashtags
        for hashtag_list in hashtag_col:
            if hashtag_list:  # Check if list exists and is not empty
                # Filter out common/unwanted tags
                filtered_tags = [
                    tag.lower() for tag in hashtag_list 
                    if tag.lower() not in {
                        'fyp', 'foryou', 'viral', 'trending', 
                        'fy', 'fürdich', 'capcut'
                    }
                ]
                all_hashtags.extend(filtered_tags)
        
        # Return Counter object with hashtag frequencies
        return Counter(all_hashtags)
    
    # Get frequencies for all posts
    all_freq = get_hashtags(df_posts['hashtags'])
    
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