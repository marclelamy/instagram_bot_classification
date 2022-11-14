from plotly.subplots import make_subplots
from IPython.display import Image




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

    try: # if charts are not histograms
        fig.update_traces(bingroup=None)
    except Exception as e: 
        print(e)

    fig.update_layout(title=f'{title}<br><sub>{subtitle}')

    return fig





def save_plotly(fig, file_name, show=None):
    '''Saves as interactive html and png plotly chart.
    
    Parameters
    ----------
    fig: plotly chart 
    file_name: 
    show: if fig displays plotly chart, if image a png of it otherwise nothing
    '''

    html_path = 'charts/html/' + file_name.lower().replace(' ', '_') + '.html'
    png_path = 'charts/png/' + file_name.lower().replace(' ', '_') + '.png'
    fig.write_html(html_path)
    fig.write_image(png_path, width=1200, height=500, scale=5)

    if show == 'fig':
        return fig
    elif show == 'image':
        return Image(png_path) 
