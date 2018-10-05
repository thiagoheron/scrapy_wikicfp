
# coding: utf-8

# In[12]:


# Import's
import scrapy
import numpy as np
import pandas as pd


# In[13]:


class QuotesSpider(scrapy.Spider):
    name = "categorySC"

    start_urls = [
        'http://www.wikicfp.com/cfp/call?conference=computer%20science',
    ]
        

        
        
        
    def parse(self, response):
        
        links_all_pages = []
        first_page = 'http://www.wikicfp.com/cfp/call?conference=computer%20science'
        
        
        # If difference of the first page, exists reponse.meta[link events]
        if response.request.url != first_page:
            for link in response.meta['links_all_pages']:
                links_all_pages.append(link)
                
                
        
        # Get all links of each page of category science computer
        contsec = response.css(".contsec")[0]
        for i in range(8, len(contsec.css("tr"))):
            tr_correct = contsec.css("tr")[i]
            if tr_correct.css("td a"):
                tr_a = tr_correct.css("td a")
                link = "http://www.wikicfp.com" + tr_a.css("a::attr(href)").extract()[0]
                head, sep, tail = link.partition('&copyownerid=')
                links_all_pages.append(head)
                #links_all_pages.append('http://www.wikicfp.com'+ tr_a.css("a::attr(href)").extract()[0])
            
        
        print("\nLink Page:\n")
        # Check links all pages
        for link in links_all_pages:
            print("Link: {l}".format(l=link))
        
        
         
        
           
        
        
        # Discover if is the first page or other. The first page has next page in index 1, and others index 2
        size_menu = len(contsec.css("tr")[(len((contsec.css("tr")))-1)].css("a::attr(href)"))
        if size_menu == 3:
            next_page = 'http://www.wikicfp.com' + contsec.css("tr")[(len((contsec.css("tr")))-1)].css("a::attr(href)")[1].extract()
        else:
            next_page = 'http://www.wikicfp.com' + contsec.css("tr")[(len((contsec.css("tr")))-1)].css("a::attr(href)")[2].extract()
            
    
        # If the last page is different to next_page... end.
        if response.request.url != next_page:
            request = scrapy.Request(url=next_page, callback=self.parse, meta={'links_all_pages':links_all_pages})
            yield request
       
        else:
            for link in links_all_pages:
                # Here make a request for each link of 21 pages science computer
                request = scrapy.Request(url=link, callback=self.parse_related_links)
                yield request
        
            
       
       
    def parse_related_links(self, response):
        
        links_page_related = [] 
        div_related_resources = response.css(".contsec")[1].css(".cfp tr td a")
        
        # Get the links of related links area
        for i in range(0, len(response.css(".contsec")[1].css(".cfp tr td a").extract())):
                link = "http://www.wikicfp.com" + div_related_resources.css("a::attr(href)")[i].extract()
                head, sep, tail = link.partition('&copyownerid=')
                links_page_related.append(head)
                #links_page_related.append(div_related_resources.css("a::attr(href)")[i].extract())
                #links_page_related[i] = "http://www.wikicfp.com" + links_page_related[i]
                
              
        
        print("Link Base: {l}".format(l=response.request.url))
        for link in links_page_related:
            print("------Link Related: {l}".format(l=link))
            
            
        # Add the current link request
        links_page_related.append(response.request.url)

        
        for link in links_page_related:
                request = scrapy.Request(url=link, callback=self.parse_page)
                yield request
            
        

        
        
        
        
    def parse_page(self, response): 
        datas = response.css(".contsec")[0]
        table = datas.css("table .gglu")[0]
        values = []
        
        # Title
        title = response.css("title::text").extract_first()
        
        # Keys of Table
        keys = table.css("tr th::text").extract() 
        
        # Valeus of Table
        for i in range(0, len(keys)):
            item = table.css("tr td")[i]
            if not item.css("span"):
                values.append(table.css("tr td::text")[i].extract())
            else:
                t = table.css("tr td")[i]
                values.append(item.css("span::text")[(len(item.css("span"))-1)].extract())
        
        # Categories
        tagCategories = response.css("tr td h5")
        categories = []
        for i in range(0, len(tagCategories.css("a::text"))):
            categories.append(tagCategories.css("a::text")[i].extract())
        
        # Event ID
        contsec = response.css("form")
        eventid = contsec[1].css("input")
        id_event = eventid.css("input").xpath("@value")[1].extract()
        
        # Link of Event
        try:
            link_event = response.css(".contsec tr")[5].css("a::attr(href)").extract()[0]
        except IndexError:
            link_event = 'null'
        
        # Related Resources
        link_resource = []
        name_resource = []
        related_resources = response.css(".contsec")[1].css(".cfp tr td a")
        for i in range(0, len(response.css(".contsec")[1].css(".cfp tr td a").extract())):
                link_resource.append(related_resources.css("a::attr(href)")[i].extract())
                link_resource[i] = "http://www.wikicfp.com" + link_resource[i]
                name_resource.append(related_resources.css("a::text")[i].extract())
                
        
        # Description
        ''' 
        try:
            div_cfp = response.css(".cfp")[0]
            description = div_cfp.css("::text").extract()
        except IndexError:
            description = 'null'
        '''
        
        
        
        
        # Create a dict from links of related resourcers 'title':'link'
        dfResources = pd.Series(link_resource, index=name_resource)
        dfResources = dfResources.to_dict()
        
        # Create a dict from Series and add new keys:values
        for i in range(0, len(keys)):
            keys[i] = keys[i].lower()
            dfTable = pd.Series(values, index=keys) 
            dfTable = dfTable.to_dict()
        dfTable['categories'] = categories
        dfTable['title'] = title
        dfTable['link_event'] = link_event
        dfTable.update({'related_resources': dfResources})
        #dfTable['description'] = description
         
    
            
        yield{
            id_event: dfTable
        }
        
        
        
        
        

