def classFactory(iface):
    from .inp_spatial_analyzer import InpSpatialAnalyzer
    return InpSpatialAnalyzer(iface)