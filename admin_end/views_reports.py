from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.views.generic import View
from django.db.models import Q
from HyFAS.utils import render_to_pdf


def DTRReport(request):
    template = get_template('reports/dtr-reports.html')


    context = {}
    html = template.render(context)
    pdf = render_to_pdf('reports/dtr-reports.html', context)
    return HttpResponse(pdf, content_type="application/pdf")
    # return render(request, 'reports/dtr-reports.html')