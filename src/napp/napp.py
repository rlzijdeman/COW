from rdflib import Graph, Namespace, RDF, URIRef, Literal
from csv import reader
import os

URI_PATTERN = "http://data.socialhistory.org/vocab/napp/{}/{}"

SDH = Namespace("http://data.socialhistory.org/resource/")
QB = Namespace("http://purl.org/linked-data/cube#")


g = Graph()
g.bind('sdh', SDH)
g.bind('qb', QB)


# AGE: format to 3 positions
mappings = {
    'AGE': lambda x: x.zfill(3)
}

nocode = ['OCCSTRNG', 'HISPAN']


def convert(filename):

    with open(filename, 'r') as csvfile:
        dataset_name = os.path.basename(filename).rstrip('.csv')
        dataset_uri = SDH['dataset/{}'.format(dataset_name)]
        g.add((dataset_uri, RDF.type, QB['Dataset']))

        nappreader = reader(csvfile, delimiter=',', quotechar='\"', strict=True)

        headers = nappreader.next()

        for row in nappreader:
            index = 0

            obs = SDH['observation/{}/{}'.format(dataset_name, ''.join(row).replace(' ','_').replace('{','_').replace('}','_'))]
            g.add((obs, QB['dataset'], dataset_uri))

            for col in row:
                if len(col) < 1:
                    index += 1
                    continue
                elif headers[index] in mappings:
                    value = mappings[headers[index]](col)
                else:
                    value = col

                if headers[index] in nocode:
                    g.add((obs, SDH['dimension/'+headers[index]], Literal(value)))
                else:
                    g.add((obs, SDH['dimension/'+headers[index]], URIRef(URI_PATTERN.format(headers[index], value))))

                index += 1

    with open('out.ttl','w') as outfile:
        g.serialize(outfile, format='turtle')
