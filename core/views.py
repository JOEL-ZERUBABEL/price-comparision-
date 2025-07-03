from django.shortcuts import render
import asyncio
from .scrape import amazon_scrape,scrape_snapdeal

def homepage(request):
    return render(request,'home.html')


def results_view(request):
    query=request.GET.get('query','')
    if not query:
        return render(request,"results.html",{"product":[],"query": ""})
    amazon_data=asyncio.run(amazon_scrape(query))
    print("Amazon Data:",amazon_data)
    snapdeal_data=scrape_snapdeal(query)
    print("Snapdeal Data:",snapdeal_data)

    all_products=amazon_data+snapdeal_data
    return render(request,"results.html",{"product":all_products,"query":query})

