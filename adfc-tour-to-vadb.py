#!/usr/bin/python

from xml.sax.saxutils import XMLGenerator
import yaml
import requests
import datetime
import os.path
import json
from dateutil import tz
import pyproj

CAT_TYPEN = "Typen (nach Dauer und Tageslage)"
CAT_CHARACTER = "Besondere Charakteristik /Thema"
CAT_ZIELGRUPPE = "Besondere Zielgruppe"
CAT_GEEIGNET = "Geeignet für"
CAT_WEITERE = "Weitere Eigenschaften"


def distance(lat0, lon0, lat1, lon1):
    geod = pyproj.Geod(ellps='WGS84')
    azimuth1, azimuth2, distance = geod.inv(lon0, lat0, lon1, lat1)
    return distance


def write_de(xml, tag: str, out_str: str):
    xml.startElement(tag, {})
    xml.startElement('I18n', {})
    xml.startElement('de', {})
    # cdata = '<![CDATA[{}]]>'.format(out_str)
    # xml.ignorableWhitespace(cdata)
    xml.characters(out_str)
    xml.endElement('de')
    xml.endElement('I18n')
    xml.endElement(tag)


def write_tour(xml, tour, cfg):
    utc_beg_time = datetime.datetime.fromisoformat(tour['beginning'])
    utc_end_time = datetime.datetime.fromisoformat(tour['end'])
    duration_in_min = "%d" % ((utc_end_time-utc_beg_time).total_seconds()/60)
    berlin_zone = tz.gettz('Europe/Berlin')
    beg_time = utc_beg_time.astimezone(berlin_zone)

    xml.startElement('Event', {'id': tour['eventItemId']})
    xml.startElement('cancelled', {})
    if tour['cStatus'] == 'Cancelled':
        xml.characters('true')
    else:
        xml.characters('false')
    xml.endElement('cancelled')
    xml.startElement('languages', {})
    xml.startElement('Language', {'id': '1'})
    xml.endElement('Language')
    xml.endElement('languages')
    write_de(xml, 'title', tour['title'])
    kategorie = None
    geeignet = []
    zielgruppe = []
    for tags in tour['extra']['itemTags']:
        if tags['category'] == CAT_TYPEN:
            kategorie = tags['tag']
        elif tags['category'] == CAT_GEEIGNET:
            geeignet.append(tags['tag'])
        elif tags['category'] == CAT_ZIELGRUPPE:
            zielgruppe.append(tags['tag'])
        elif tags['category'] == CAT_CHARACTER:
            pass
        elif tags['category'] == CAT_WEITERE:
            pass
        else:
            print('NEUE CAT: %s' %tags['category'])
    description = '<p>'+tour['extra']['eventItem']['cShortDescription']
    if not kategorie is None:
        description = description+"<br>Kategorie: %s" % kategorie
    if len(geeignet) > 0:
        description = description + \
            "<br>Geeignet für: %s" % (",".join(geeignet))
    if tour['extra']['eventItem']['cTourLengthKm'] != '0':
        km = "%d km " % tour['extra']['eventItem']['cTourLengthKm']
    else:
        km = tour['tourLenght']
    description = description+'<br>Länge: %s' % km
    if len(zielgruppe) >0:
        description == description + \
          "<br>Besondere Zielgruppe: %s" % (",".join(zielgruppe))
    description = description+'</p>'
    # FIXME
    # kurz = "<p>" + tour.getKurzbeschreibung() + "<br>Kategorie: " + tour.getKategorie() + "<br>Geeignet für: " + \
    #       tour.getRadTyp() + "<br>" + "<br>".join(tour.getZusatzInfo()) + "<br>Schwierigkeitsgrad: " + \
    #       ["unbekannt", "sehr einfach", "einfach", "mittel", "schwer", "sehr schwer"][tour.getSchwierigkeit()] + "</p>"
    # kurz = kurz.replace("<br><br>", "<br>").replace("]]>","")
    write_de(xml, 'shortDescription', description)
    link = 'https://touren-termine.adfc.de/radveranstaltung/'+tour['cSlug']
    write_de(xml, 'link', link)
    write_de(xml, 'linkText', 'Mehr Infos im ADFC Tourenportal')

    xml.startElement('categories', {})
    xml.startElement('Category', {"id": "36"})
    xml.endElement('Category')
    xml.endElement('categories')
    xml.startElement('pricinig', {})
    minPrice = 999999
    maxPrice = 0
    for price_ele in tour['extra']['eventItemPrices']:
        if price_ele['price'] > maxPrice:
            maxPrice = price_ele['price']
        if price_ele['price'] < minPrice:
            minPrice = price_ele['price']
    if maxPrice == 0:
        xml.startElement('freeOfCharge', {})
        xml.characters('true')
        xml.endElement('freeOfCharge')
    else:
        xml.startElement('fromPrice', {})
        xml.characters(f"{minPrice:.2f}")
        xml.endElement('fromPrice')
        xml.startElement('toPrice', {})
        xml.characters(f"{maxPrice:.2f}")
        xml.endElement('toPrice')
    xml.endElement('pricinig')
    xml.startElement('eventDates', {})
    xml.startElement('SpecificEventData', {})
    xml.startElement('date', {})
    xml.characters(beg_time.strftime('%Y-%m-%d'))
    xml.endElement('date')
    xml.startElement('startTime', {})
    xml.characters(beg_time.strftime('%H:%M:%S'))
    xml.endElement('startTime')
    xml.startElement('duration', {})
    xml.characters(duration_in_min)
    xml.endElement('duration',)
    xml.endElement('SpecificEventData')
    xml.endElement('eventDates')
    xml.startElement('media', {})
    xml.startElement('EventImage', {})
    xml.startElement('pooledMedium', {})
    xml.startElement('PooledEventMedium', {
                     'url': tour['extra']['images'][0]['downloadLink']})
    write_de(xml, 'copyright', tour['extra']['images'][0]['copyright'])
    xml.endElement('PooledEventMedium')
    xml.endElement('pooledMedium')
    xml.startElement('imageType', {})
    xml.startElement('ImageType', {'id': '1'})
    xml.endElement('ImageType')
    xml.endElement('imageType')
    xml.endElement('EventImage')
    xml.endElement('media')
    startpunkt = None
    for loc in tour['extra']['tourLocations']:
        if loc['type'] == 'Startpunkt':
            startpunkt = loc['location']
    maxDistance = 500
    nearestPoint = '6137'  # Default Location
    for loc in cfg['locs']:
        locDistance = distance(
            loc['latitude'], loc['longitude'], startpunkt['lat'], startpunkt['long'])
        if locDistance < maxDistance:
            maxDistance = locDistance
            nearestPoint = str(loc['poi'])
    # FIXME
    xml.startElement('location', {})
    xml.startElement('AddressPoi', {'id': nearestPoint})
    xml.endElement('AddressPoi')
    xml.endElement('location')
    # <location>
    #    <AddressPoi id="${addressPoi}"/>
    # </location>
    xml.startElement('contributor', {})
    xml.startElement('AddressPoi', {'id': '6137'})
    xml.endElement('AddressPoi')
    xml.endElement('contributor')
    xml.endElement('Event')


def write_xml(touren, cfg):
    outfile = open('/tmp/my.xml', 'w')
    xml = XMLGenerator(outfile, encoding='utf-8')
    xml.startDocument()
    xml.startElement('events', {})
    for tour in touren:
        write_tour(xml, tour, cfg)
    xml.endElement('events')
    xml.endDocument()
    outfile.close()


def read_cfg_file():
    with open('config.yml', 'r') as file:
        cfg = yaml.safe_load(file)
    return cfg


def fetch_touren(unit, cfg, start_date, end_date):
    # url="%s&unitKey=%d" % (cfg['search_url'],unit_key)
    # print(url)
    params = cfg['static_search_params']
    params['unitKey'] = unit['key']
    params['beginning'] = start_date.strftime('%Y-%m-%d')
    params['end'] = end_date.strftime('%Y-%m-%d')
    filename = "/tmp/adfc_%s_%s.json" % (unit['name'],
                                         start_date.strftime('%Y-%m-%d'))
    if os.path.isfile(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data['items']
    else:
        response = requests.get(cfg['search_url'], params=params)
        outfile = open(filename, 'w')
        outfile.write(response.text)
        outfile.close()
        return response.json()['items']


def fetch_tour(cfg, uuid, now):
    filename = "/tmp/adfc_%s_%s.json" % (uuid,
                                         now.strftime('%Y-%m-%d'))
    if os.path.isfile(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data
    else:
        response = requests.get(cfg['get_event_url']+uuid)
        outfile = open(filename, 'w')
        outfile.write(response.text)
        outfile.close()
        return response.json()


def main():
    cfg = read_cfg_file()
    start_date = datetime.datetime.today()
    end_date = datetime.datetime.today(
    )+datetime.timedelta(cfg['zeitraum_tage'])
    touren = []
    for unit in cfg['units']:
        print(unit['name'])
        data = fetch_touren(unit, cfg, start_date, end_date)
        print(len(data))
        touren = touren+data
    for tour in touren:
        tour['extra'] = fetch_tour(cfg, tour['eventItemId'], start_date)
    write_xml(touren, cfg)


main()
