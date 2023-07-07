from django.http import HttpResponse
from rest_framework.decorators import api_view
from fidstore.batiskaf.data.get_categories import start_parse
from fidstore.drevodesign.main import start_parse_drevodesign
@api_view(['GET', ])
def parse_batiskaf(request):
    start_parse()
    return HttpResponse(open('fidstore/batiskaf/data/batiskaf.xml',encoding='utf-8').read(), content_type='text/xml')

@api_view(['GET', ])
def get_batiskaf_list(request):
    return HttpResponse(open("fidstore/batiskaf/data/batiskaf.xml",encoding='utf-8').read(), content_type='text/xml')

@api_view(['GET', ])
def parse_drevodesign(request):
    start_parse_drevodesign()
    return HttpResponse(open("fidstore/drevodesign/drevodesign.xml",encoding='utf-8').read(), content_type='text/xml')

@api_view(['GET', ])
def get_drevodesign_list(request):
    return HttpResponse(open("fidstore/drevodesign/drevodesign.xml",encoding='utf-8').read(), content_type='application/xml')