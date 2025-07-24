# coding=utf-8

"""
Plot a map with locations of fusion companies as OpenStreetMap into html-file.
"""

__author__      = 'Alf Köhn-Seemann'
__email__       = 'koehn@igvp.uni-stuttgart.de'
__copyright__   = 'University of Stuttgart'
__license__     = 'MIT'

# import standard modules
import bs4
import markdown
import numpy as np
import pandas as pd
import requests         # de facto standard for HTTP requests in python

# Folium is a python library to create interactive maps using Leaflet 
# JavaScript library. Allows to visualize geospatial data on a map and share
# that map as a website
import folium

# Nominatim is open-source geocoding service provided by OpenStreetMap project
from geopy.geocoders import Nominatim


def get_fusion_companies_info(url):
    #{{{
    """
    Load informations about fusion companies from github markdown page.

    Parameters
    ----------
    url: str
        url of github-markdown file containing table with fusion companies. 
        Note: use raw file content (not the into-html-formatted version)

    Returns
    -------
    fusion_table: pandas dataframe
        contains 'address', 'name', and 'concept'
    """

    # test if url is correct/available
    response = requests.get(url)
    if response.status_code == 200:
        print("Successfully requested data from url")
    elif response.status_code == 404:
        raise Exception(f"Error with url")

    # load content from markdown-formatted github table
    markdown_raw    = requests.get(url).text
    html_extracted  = markdown.markdown(text=markdown_raw, extensions=['tables'])
    # use html parser to extract tables
    soup = bs4.BeautifulSoup(html_extracted, 'html.parser')
    tables = soup.find_all('table')
    # headers will be used to identify correct table
    headers = soup.find_all('h2')

    dataframes = []
    for table, header in zip(tables, headers):
        # only take the active companies/projects
        if 'active' in header.get_text().lower():
            df = pd.read_html(str(table))[0]
            df['address'] = df['Location']
            df['name']    = df['Company']
            df['concept'] = df['Concept']
            dataframes.append(df[['name', 'address', 'concept']])

    fusion_table = pd.concat(dataframes)

    return fusion_table
    #}}}


def get_lat_lng(address_arr):
    #{{{
    """
    Get latitude and longitude of a given address.

    Parameters
    ----------
    address_arr: numpy array of strings

    Returns
    -------
    lats, lngs: two 1D numpy arrays
    """

    # initialize Naminatim API
    # setting timeout is important, otherwise timeout error likely to occur
    geolocator = Nominatim(user_agent='my_geopy_app', timeout=5)

    lats = np.empty(0)
    lngs = np.empty(0)
    for addr in address_arr:
        locator = geolocator.geocode(addr)
        print("original address: {0} | address found by openstreetmap's Nominatim: {1}".format(addr, locator))
        if locator is not None:
            lats    = np.append( lats, locator.latitude )
            lngs    = np.append( lngs, locator.longitude )
        else:
            print( "ERROR: following address return None when passed to openstreetmaps Nominatim: ",addr )
            return -1
        #print(lats)

    return lats, lngs
    #}}}


def plot_fusion_map(names=None, 
                    lats=None, lngs=None, 
                    concepts=None, 
                    fname_map="map.html"
                    ):
    #{{{
    """
    Plot a map into html-file with fusion companies as markers.

    Parameters
    ----------
    names: 1D numpy array
    lats: 1D numpy array
    lngs: 1D numpy array
    concepts: 1D numpy array
    fname_map: str

    Returns
    -------
    lats, lngs: two 1D numpy arrays
    """

    
    # create map, possible keywords:
    # location: center of map (latitude, longitude)
    # zoom_start: zoom-level (resolution)
    #my_map = folium.Map(location=(50,0), zoom_start=2)
    my_map = folium.Map()

    # define colors for different fusion concepts
    col_stell   = 'green'
    col_tokam   = 'blue'
    col_icf     = 'red'
    col_other   = 'black'
    
    marker_opac = .6

    # add markers for fusion companies to map
    ii = 0
    # python zip function allows to iterate through multiple lists simultaneously
    for lat, lng in zip(lats, lngs):
        if 'stellarator' in concepts[ii].lower():
            folium.Marker(
                    location=[lat, lng],
                    tooltip=names[ii],
                    icon=folium.Icon(color=col_stell),
                    opacity=marker_opac,
                    ).add_to(my_map)
        elif 'tokamak' in concepts[ii].lower():
            folium.Marker(
                    location=[lat, lng],
                    tooltip=names[ii],
                    icon=folium.Icon(color=col_tokam),
                    opacity=marker_opac,
                    ).add_to(my_map)
        elif 'icf' in concepts[ii].lower():
            folium.Marker(
                    location=[lat, lng],
                    tooltip=names[ii],
                    icon=folium.Icon(color=col_icf),
                    opacity=marker_opac,
                    ).add_to(my_map)
        else:
            folium.Marker(
                    location=[lat, lng],
                    tooltip=names[ii],
                    icon=folium.Icon(color=col_other),
                    opacity=marker_opac,
                    ).add_to(my_map)
        ii += 1

    # make a legend by explicitly defining the corresponding HTML code
    # source: https://www.geeksforgeeks.org/data-visualization/create-a-legend-on-a-folium-map-a-comprehensive-guide/
    legend_html = '''
    <div style="position: fixed; 
         bottom: 50px; left: 50px; width: 110px; height: 90px; 
         border:2px solid grey; z-index:9999; font-size:14px;
         background-color:white; opacity: 0.6;">
         &nbsp; <i class="fa fa-circle" style="color:blue"></i> Tokamak<br>
         &nbsp; <i class="fa fa-circle" style="color:green"></i> Stellarator<br>
         &nbsp; <i class="fa fa-circle" style="color:red"></i> ICF<br>
         &nbsp; <i class="fa fa-circle" style="color:black"></i> other<br>
    </div>
    '''
    # add legend to the map
    my_map.get_root().html.add_child(folium.Element(legend_html))

    # save name to html file (which can then be opened separately in a web-browser)
    my_map.save(fname_map)
    print( "written map into ", fname_map)
    #}}}


def main():
    #{{{

    # url of github-markdown file containing table with fusion companies
    # note, use the raw file content (not the into-html-formatted-version)
    url = "https://raw.githubusercontent.com/alfkoehn/fusion_plots/refs/heads/master/fusion_companies/fusion_companies.md"

    # extract information of fusion companies from github page
    df  = get_fusion_companies_info(url)

    # convert everything into numpy tables
    names   = df['name'].to_numpy()
    address = df['address'].to_numpy()
    concepts = df['concept'].to_numpy()

    # get latitude and longitude from addresses of companies
    lats, lngs = get_lat_lng(address)

    # plot world map with fusion companies as markers
    fname_map = "fusion_companies_map.html"
    plot_fusion_map(names=names, 
                    lats=lats, lngs=lngs, 
                    concepts=concepts, 
                    fname_map=fname_map
                )
    #}}}


if __name__ == '__main__':
    main()


