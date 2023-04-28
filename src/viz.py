import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
from IPython.display import Image
pd.options.display.float_format = '{:,.2f}'.format


viz_path = '/Users/marclamy/Desktop/code/viz/instabot/'


def join_plots(plot_lst: list, row_col=None, title='', subtitle=''): 
    '''Merges multiple plotly express plots into one. 
    
    Parameters
    ----------
    plot_lst: list containing all plotly express to plot
    row_col: tuple indicating how many rows by columns
    '''
    if row_col == None: 
        row_col = (1, len(plot_lst))

    fig = make_subplots(rows=row_col[0], cols=row_col[1]) 

    for index, figure in enumerate(plot_lst):
        for trace in range(len(figure["data"])):
            fig.append_trace(figure["data"][trace], row=row_col[0], col=index+1)

    # try: # if charts are not histograms
    #     fig.update_traces(bingroup=None)
    # except Exception as e: 
    #     print(e)

    fig.update_layout(title=f'{title}<br><sub>{subtitle}')

    return fig





def save_plotly_fig(fig, show='image'):
    '''Saves as interactive html and png plotly chart.
    
    Parameters
    ----------
    fig: plotly chart 
    file_name: 
    show: if fig displays plotly chart, if image a png of it otherwise nothing
    '''
    height = fig.layout['height'] if fig.layout['height'] != None else 500
    width = fig.layout['width'] if fig.layout['width'] != None else 1200

    try: fig_title = fig.to_dict()['layout']['title']['text'].split('<br>')[0]
    except KeyError as e: fig_title = 'NO TITLE PROVIDED'
    fig = fig.update_layout(title=fig_title.title())
    
    html_file = fig_title.lower().replace(' ', '_').replace('.', '') + '.html'
    png_file = fig_title.lower().replace(' ', '_').replace('.', '') + '.png'
    fig.write_html(viz_path + html_file)
    fig.write_image(viz_path + png_file, width=width, height=height, scale=5)

    html_link = 'https://htmlpreview.github.io/?' + 'https://github.com/marclelamy/viz/blob/main/instabot/' + html_file
    png_link = 'https://github.com/marclelamy/viz/blob/main/instabot/' + png_file
    print(f'Link for interactability (plotly chart): {html_link}')

    
    with open('/Users/marclamy/Desktop/code/viz/README.md', 'r+') as f:
        embed = f'[Link for interactibility]({html_link})'
        embed += f'\n![]({png_link})'
        content = '**' + fig_title + '**\n\n' + embed + '\n\n\n'
        if fig_title not in f.read():
            f.write(content)

    if show == 'fig':
        return fig
    elif show == 'image':
        return Image(viz_path + png_file) 



