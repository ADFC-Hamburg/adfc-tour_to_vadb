from xml.sax.saxutils import XMLGenerator
from adfctermin import ADFCTermin
from pyproj import Geod
from lxml import etree
from  shutil import copyfile
def validate(xml_path: str, xsd_path: str) -> bool:

    xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)
    result = xmlschema.validate(xml_doc)

    return result

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

def distance(lat0, lon0, lat1, lon1):
    geod = Geod(ellps='WGS84')
    azimuth1, azimuth2, distance = geod.inv(lon0, lat0, lon1, lat1)
    return distance

def write_tour(xml, termin:ADFCTermin, cfg):
    tour={}

    xml.startElement('Event', {'id': termin.getId()})
    #xml.startElement('cancelled', {})
    #if termin.isCannceld():
    #    xml.characters('true')
    #else:
    #    xml.characters('false')
    #xml.endElement('cancelled')
    xml.startElement('languages', {})
    xml.startElement('Language', {'id': '1'})
    xml.endElement('Language')
    xml.endElement('languages')
    write_de(xml, 'title', termin.getTitle())
    description = "<p>%s<br>Kategorie:%s<br>Geeignet für: %s<br>Länge: %s<br>Besondere Zielgruppen: %s</p>" % (
            termin.getShortDescr(),
            termin.getKategoryAsString(),
            ", ".join(termin.getRadTypenAsStringList()),
            termin.getTourLaenge(),
            ", ".join(termin.getZielgruppenAsStringList()),
        )
    write_de(xml, 'shortDescription', description)
    write_de(xml, 'link', termin.getAdfcUrl())
    #write_de(xml, 'linkText', 'Mehr Infos im ADFC Tourenportal')

    xml.startElement('categories', {})
    xml.startElement('Category', {"id": "36"})
    xml.endElement('Category')
    xml.endElement('categories')
    xml.startElement('pricing', {})
    minPrice=termin.getMinPreis()
    maxPrice=termin.getMaxPreis()
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
    xml.endElement('pricing')
    xml.startElement('eventDates', {})
    xml.startElement('SpecificEventDate', {})
    xml.startElement('date', {})
    xml.characters(termin.getStartLocalTime().strftime('%Y-%m-%d'))
    xml.endElement('date')
    xml.startElement('startTime', {})
    xml.characters(termin.getStartLocalTime().strftime('%H:%M:%S'))
    xml.endElement('startTime')
    xml.startElement('duration', {})
    xml.characters("%d" % termin.getDurationInMinutes())
    xml.endElement('duration',)
    xml.endElement('SpecificEventDate')
    xml.endElement('eventDates')
    xml.startElement('media', {})
    xml.startElement('EventImage', {})
    xml.startElement('pooledMedium', {})
    xml.startElement('PooledEventMedium', {
                     'url': termin.getImageUrl()
                     })
    write_de(xml, 'title', '')
    write_de(xml, 'description', '')
    write_de(xml, 'copyright', termin.getImageCopyright())
    xml.endElement('PooledEventMedium')
    xml.endElement('pooledMedium')
    xml.startElement('imageType', {})
    xml.startElement('ImageType', {'id': '1'})
    xml.endElement('ImageType')
    xml.endElement('imageType')
    xml.endElement('EventImage')
    xml.endElement('media')
    maxDistance = 100
    nearestPoint = None  # Default Location
    lat = termin.getStartLat()
    lon = termin.getStartLon()
    for loc in cfg['locs']:
        locDistance = distance(
            loc['latitude'], loc['longitude'], lat, lon)
        if locDistance < maxDistance:
            maxDistance = locDistance
            nearestPoint = loc
    poi_id = "6137"
    if nearestPoint is not None:
        poi_id = str(nearestPoint['poi'])
    xml.startElement('location', {})
    xml.startElement('AddressPoi', {'id': poi_id})
    xml.endElement('AddressPoi')
    xml.endElement('location')
    #xml.startElement('contributor', {})
    #xml.startElement('AddressPoi', {'id': '6137'})
    #xml.endElement('AddressPoi')
    #xml.endElement('contributor')
    xml.endElement('Event')


def write_xml(terminlist, cfg, filename):
    tmpfilename="/tmp/vadb-metropolregion.xml"
    outfile = open(tmpfilename, 'w')
    xml = XMLGenerator(outfile, encoding='utf-8')
    xml.startDocument()
    xml.startElement('events', {})
    for termin in terminlist:
        write_tour(xml, termin, cfg)
    xml.endElement('events')
    xml.endDocument()
    outfile.close()
    if validate(tmpfilename, "standard-import.xsd"):
        copyfile(tmpfilename, filename)
    else:
         raise Exception("XSD does not validate")
