from xml.sax.saxutils import XMLGenerator
from adfctermin import ADFCTermin
from lxml import etree
from shutil import copyfile
from base64 import encodebytes
from struct import pack
from os.path import isfile

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

def write_str(xml, tag: str, out_str: str):
    xml.startElement(tag, {})
    xml.characters(out_str)
    xml.endElement(tag)

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
    if termin.getBookingLink() != '':
        write_de(xml,'bookingLink', termin.getBookingLink())
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
    write_str(xml,'creationTime',termin.getPublishDate().strftime("%Y-%m-%d %H:%M:%s"))
    write_str(xml,'lastChangeTime',termin.getChangedDate().strftime("%Y-%m-%d %H:%M:%s"))
    pack_float=pack('ff', termin.getStartLat(),termin.getStartLon())
    poi_id = "ADFC_HH_v1_%s" % encodebytes(pack_float).decode().strip()
    xml.startElement('location', {})
    xml.startElement('AddressPoi', {'id': poi_id})
    xml.startElement('languages', {})
    xml.startElement('Language', {'id':"1"})
    xml.endElement('Language')
    xml.endElement('languages')
    xml.startElement('types',{})
    xml.startElement('AddressPoiType', {'id':"3"})
    xml.endElement('AddressPoiType')
    xml.endElement('types')
    title=''
    if termin.getStartName() != '':
        title=termin.getStartName()
    else:
        title="%s, %s %s" % (termin.getStartStreet(), termin.getStartZipCode(), termin.getStartCity())
    write_de(xml,'title', title)
    xml.startElement('contact1',{})
    xml.startElement('address',{})
    write_str(xml,'street',termin.getStartStreet())
    #write_str(xml,'streetNo',termin.getStartStreetNo())
    write_str(xml,'zipcode',termin.getStartZipCode())
    write_str(xml,'city',termin.getStartCity())
    xml.endElement('address')
    xml.endElement('contact1')
    xml.startElement('geoInfo',{})
    xml.startElement('GeoInfo',{})
    xml.startElement('coordinates',{})
    write_str(xml,'latitude',"%f" % termin.getStartLat())
    write_str(xml,'longitude',"%f" % termin.getStartLon())
    xml.endElement('coordinates')
    xml.endElement('GeoInfo')
    xml.endElement('geoInfo')
    xml.endElement('AddressPoi')
    xml.endElement('location')
    #xml.startElement('contributor', {})
    #xml.startElement('AddressPoi', {'id': '6137'})
    #xml.endElement('AddressPoi')
    #xml.endElement('contributor')
    xml.endElement('Event')


def write_xml(terminlist, cfg, filename, xsd_filename):
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

    if not(isfile(xsd_filename)) or validate(tmpfilename, xsd_filename):
        copyfile(tmpfilename, filename)
    else:
         raise Exception("XSD does not validate")
