#!/usr/bin/python


import yaml
import requests
import datetime
import os.path
import json
import adfctermin
from vadbwriter import write_xml
import logging

log = logging.getLogger(__name__)

CAT_TYPEN = "Typen (nach Dauer und Tageslage)"
CAT_CHARACTER = "Besondere Charakteristik /Thema"
CAT_ZIELGRUPPE = "Besondere Zielgruppe"
CAT_GEEIGNET = "Geeignet für"
CAT_WEITERE = "Weitere Eigenschaften"



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
    filename = "/tmp/adfc_search_%s_%s.json" % (unit['name'],
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


def fetch_tour(cfg, uuid, now, yesterday):
    filename = "/tmp/adfc_event_%s_%s.json" % (uuid,
                                         now.strftime('%Y-%m-%d'))
    yesterday_filename = "/tmp/adfc_event_%s_%s.json" % (uuid,
                                         yesterday.strftime('%Y-%m-%d'))

    if os.path.isfile(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data
    else:

        response = requests.get(cfg['get_event_url']+uuid)
        if os.path.isfile(yesterday_filename):
            with open(yesterday_filename) as json_file:
                data = json.load(json_file)
            last_changed=data['ADFCHH_lastChanged']
            del data['ADFCHH_lastChanged']
            if json.dumps(data)==json.dumps(json.loads(response.text)):
                data['ADFCHH_lastChanged']=last_changed
            else:
                data=json.loads(response.text)
                data['ADFCHH_lastChanged']=now.isoformat()
        else:
            data=json.loads(response.text)
            data['ADFCHH_lastChanged']=now.isoformat()
        outfile = open(filename, 'w')
        outfile.write(json.dumps(data))
        outfile.close()
        return data

def main():
    cfg = read_cfg_file()
    start_date = datetime.datetime.today()
    end_date = datetime.datetime.today(
    )+datetime.timedelta(cfg['zeitraum_tage'])
    touren = []
    for unit in cfg['units']:
        data = fetch_touren(unit, cfg, start_date, end_date)
        touren = touren+data
    terminlist = []
    log.info('Hallo')
    yesterday=start_date- datetime.timedelta(days=1)
    for tour in touren:
        link = 'https://touren-termine.adfc.de/radveranstaltung/'+tour['cSlug']
        extra = fetch_tour(cfg, tour['eventItemId'], start_date, yesterday)
        tour['extra'] = extra
        error = False
        if tour['cStatus'] == 'Published':
            status = adfctermin.Status.Published
        elif tour['cStatus'] == 'Cancelled':
            status = adfctermin.Status.Cannceld
        else:
            log.error('Unbekanter Status %s bei Termin %s' %
                      (tour['cStatus'], link))
            error = True
        minPrice = 999999
        maxPrice = 0
        for price_ele in extra['eventItemPrices']:
            if price_ele['price'] > maxPrice:
                maxPrice = price_ele['price']
            if price_ele['price'] < minPrice:
                minPrice = price_ele['price']
        if maxPrice == 0:
            minPrice = 0
        if extra['eventItem']['cTourLengthKm'] != '0':
            km = "%d km " % extra['eventItem']['cTourLengthKm']
        else:
            km = tour['tourLenght']
        startpunkt = None
        for loc in extra['tourLocations']:
            if loc['type'] == 'Startpunkt':
                startpunkt = loc
        kategorie = None
        radTypen = []
        zielgruppen = []
        thema = []
        eigenschaften = []
        for tags in tour['extra']['itemTags']:
            if tags['category'] == CAT_TYPEN:
                if kategorie is None:
                    if tags['tag'] in adfctermin.KATEGORIE_DICT.keys():
                        kategorie = adfctermin.KATEGORIE_DICT[tags['tag']]
                    else:
                        log.error('Unbekannter Tag %s bei Termin-Type %s' %
                                  (tags['tag'], link))
                        error = True
                else:
                    log.error('Mehr als ein Kategorie Typ bei Termin %s' % link)
                    error = True
            elif tags['category'] == CAT_GEEIGNET:
                if tags['tag'] in adfctermin.RADTYPEN_DICT.keys():
                    radTypen.append(adfctermin.RADTYPEN_DICT[tags['tag']])
                else:
                    log.error('Unbekannter Raddtype: %s bei Termin %s' %
                              (tags['tag'], link))
                    error = True
            elif tags['category'] == CAT_ZIELGRUPPE:
                if tags['tag'] in adfctermin.ZIELGRUPPEN_DICT.keys():
                    zielgruppen.append(adfctermin.ZIELGRUPPEN_DICT[tags['tag']])
                else:
                    log.error('Unbekannter Zielgruppe: %s bei Termin %s' %
                              (tags['tag'], link))
                    error = True

            elif tags['category'] == CAT_CHARACTER:
                if tags['tag'] in adfctermin.THEMA_DICT.keys():
                    thema.append(adfctermin.THEMA_DICT[tags['tag']])
                else:
                    log.error('Unbekannter Thema: %s bei Termin %s' %
                              (tags['tag'], link))
                    error = True

            elif tags['category'] == CAT_WEITERE:
                if tags['tag'] in adfctermin.EIGENSCHAFTEN_DICT.keys():
                    eigenschaften.append(adfctermin.EIGENSCHAFTEN_DICT[tags['tag']])
                else:
                    log.error('Unbekannter Eigenschaft: %s bei Termin %s' %
                              (tags['tag'], link))
                    error = True

            else:
                log.error('Unbekantes Tag %s bei Termin %s' %
                          (tags['category'], link))
                error = True
        if not error:
            if (tour['extra']['eventItem']['cRegistrationType']=='None'):
                bookingLink=''
            elif (tour['extra']['eventItem']['cRegistrationType']=='Internal'):
                bookingLink=link
            elif (tour['extra']['eventItem']['cRegistrationType']=='External'):
                bookingLink=tour['extra']['eventItem']['cExternalRegistrationUrl']
            publishDate=datetime.datetime.fromisoformat(tour['extra']['eventItem']['cPublishDate'])
            termin = adfctermin.ADFCTermin(
                id=tour['eventItemId'],
                start=datetime.datetime.fromisoformat(tour['beginning']),
                ende=datetime.datetime.fromisoformat(tour['end']),
                status=status,
                title=tour['title'],
                shortDesc=extra['eventItem']['cShortDescription'],
                descr=extra['eventItem']['description'],
                bookingLink=bookingLink,
                laenge=km,
                minPreis=minPrice,
                maxPreis=maxPrice,
                adfcUrl=link,
                imageUrl=extra['images'][0]['downloadLink'],
                imageCopyright=extra['images'][0]['copyright'],
                startLat=startpunkt['location']['lat'],
                startLon=startpunkt['location']['long'],
                startName=startpunkt['name'],
                startStreet=startpunkt['street'],
                startCity=startpunkt['city'],
                startZipCode=startpunkt['zipCode'],
                kategorie=kategorie,
                radTypen=radTypen,
                zielgruppen=zielgruppen,
                thema=thema,
                eigenschaften=eigenschaften,
                publishDate=publishDate,
                changedDate=datetime.datetime.fromisoformat(tour['extra']['ADFCHH_lastChanged'])
            )
            terminlist.append(termin)
    write_xml(terminlist, cfg, '/srv/metroterm/out/vadb-metropolregion.xml', 'standard-import.xsd')

main()
