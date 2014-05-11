import urllib2, urllib, cookielib
from BeautifulSoup import BeautifulSoup
import json, io
import mechanize


def get_parameters(soupitem):
    """Get the aspx parameters from the page

    """
    parameters = {}
    for input in soupitem.findAll('input'):
        if input.has_key('id') and input['id'] != '__EVENTTARGET':
            if input.has_key('value'):
                try:
                    parameters[input['id']] = input['value']
                except AttributeError:
                    print ''
            else:
                parameters[input['id']] = ''
    return parameters

def update_parameters(parameters, region):
    """ Update the aspx parameters

    This site requires a region to get the list of cities within
    """
    # Update the region
    # TODO: update parameters for origin cities, destinations and schedules
    parameters['__EVENTTARGET'] = 'ctl00$cphM$forwardRouteUC$lstRegion$repeater$'+region+'$link'
    parameters['ctl00$toolkitScriptManager'] = 'ctl00$cphM$updateOrigin'

    return parameters

def get_stops(filestream): 
    home_url = "http://www.boltbus.com/default.aspx"
    cities_url = "http://www.boltbus.com/wherewetravel.aspx"
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler())
    req = urllib2.Request(home_url)
    homepage = opener.open(req)
    soupHome = BeautifulSoup(homepage.read())

    # POST the region to the site and update stops
    stops = []
    parameters = get_parameters(soupHome)
    for region in ['ctl00', 'ctl01']:

        parameters = update_parameters(parameters, region)

        data = urllib.urlencode(parameters)
        opener.open(req, data)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler())
        req = urllib2.Request(home_url)
        homepage = opener.open(req, data)

        req = urllib2.Request(cities_url)
        f = opener.open(req)
        soup = BeautifulSoup(f.read())

        # Get the lat, long and stop_name from the Maplocations
        mapregions = soup.findAll('script',{'type':'text/javascript'})
        for region in mapregions:
            region = region.__str__('utf8')
            if "MapLocations" in region:
                indexfirst = region.find('{')
                indexlast = region.rfind('}')
                regionmap = region[indexfirst:indexlast+1]
                
        data = json.loads(regionmap)
        maplocations = data['MapLocations']

        stops_loc = {}
        stops_addr = {}
        for loc in maplocations:
            stops_loc = {'stop_name':loc['Name'].replace('&amp;','&'),'lat':loc['Location']['Latitude'],'long':loc['Location']['Longitude']}
            stops.append(stops_loc)

        for city in soup.findAll('div',{'class':'accordionContent'}):
            stopnames = [adr.text for adr in city.findAll('b')]

            addresses = []
            addresses_clean = []
            for loc in city.findAll('b'):
                stoplocations = loc.findNextSiblings(text = lambda(text): text != '<br />' and text != '\n' and text != '</h>')
                if len(stoplocations) == 3:
                    addr = stoplocations[0]
                    addr = addr.replace("\r\n", "")
                    addr = addr.replace("         ", "")
                    addr.strip()
                    addresses.append(addr)
                elif len(stoplocations)%3==0: 
                    for i in range(0,len(stoplocations),3):
                        stoplocations[i] = stoplocations[i].replace("\r\n", "")
                        stoplocations[i] = stoplocations[i].replace("         ", "")
                        stoplocations[i].strip()
                        addresses.append(stoplocations[i])

                # Remove redundant addresses
                for i in addresses:
                    if i not in addresses_clean:
                        addresses_clean.append(i)

                # Put stop_locations in a dict to be later added 
                for i,s in enumerate(stopnames): 
                    stops_addr[s] = addresses_clean[i]

        # Update stops
        for i, stop in enumerate(stops):
            stop_tmp = stop
            for key in stops_addr.iterkeys():
                if (stop['stop_name'] == key):
                    stop_tmp.update({'stop_location':stops_addr[key]})
                    stops[i] = stop_tmp

    # Output to file instance
    json.dump(stops, filestream)