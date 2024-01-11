from enum import Enum


class ReportFormat(Enum):
    # TODO: Add and implement vtk and vtp from the converter notebook into this class.
    """ Format of a report """
    csv = 'csv'
    h5 = 'h5'
    hdf = 'h5'
    hdf5 = 'h5'
    tsv = 'tsv'
    xlsx = 'xlsx'


class VizFormat(Enum):
    """ Format of a viz """
    jpg = 'jpg'
    pdf = 'pdf'
    png = 'png'
    svg = 'svg'
