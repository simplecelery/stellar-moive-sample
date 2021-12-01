import threading
import time
import bs4
import requests
import StellarPlayer
import re
import urllib.parse
from .plugin import Plugin


class myplugin(StellarPlayer.IStellarPlayerPlugin, Plugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        StellarPlayer.IStellarPlayerPlugin.__init__(self, player)        
        Plugin.__init__(self)
        self.detail = None
        self.play_list = []
        
        print(self.data)
        print(self.categories)
        
    @property
    def movies(self):
        # to dict
        return [ dict(zip(['name', 'cover', 'summary', 'category', 'src'], i)) for i in self.paged_data] 
       
    def stop(self):
        return super().stop()

    def start(self):
        return super().start()

    def makeLayout(self):
        if self.detail is None:
            return self.makeLayoutList() 
        else:
            return self.makeLayoutDetail() 

    def makeLayoutList(self):
        category_items = []
        categories = map(lambda x: f'[{x}]' if x == self.current_category else x, ['全部'] + list(self.categories))
        for cat in categories:
            category_items.append({'type':'link','name':cat, 'fontSize':15, '@click':'onCategoryClick', 'width':60})

        grid_layout = {'group':
                            [
                                {'type':'image','name':'cover','width':120,'height':150,'@click':'onMovieClick'},
                                {'type':'label','name':'name','hAlign':'center'},
                            ],
                            'dir':'vertical'
                        }
        controls = [
            {'group':category_items, 'name': 'categories', 'height':30},
            {'type':'space','height':10},
            {'group':
                [
                    {'type':'edit','name':'search_edit','label':'搜索', ':value': 'q'},
                    {'type':'button','name':'搜电影','@click':'onSearch'}
                ]
                ,'height':30
            },
            {'type':'space','height':10},
            {'type':'grid','name':'list','itemlayout':grid_layout,'value':self.movies,'marginSize':5,'itemheight':180,'itemwidth':120},
            {'group':
                [
                    {'type':'space'},
                    {'group':
                        [
                            {'type':'label','name':'cur_page',':value':'cur_page'},
                            {'type':'link','name':'首页','fontSize':13,'@click':'onClickFirstPage'},
                            {'type':'link','name':'上一页','fontSize':13,'@click':'onClickFormerPage'},
                            {'type':'link','name':'下一页','fontSize':13,'@click':'onClickNextPage'},
                            {'type':'link','name':'末页','fontSize':13,'@click':'onClickLastPage'},
                            {'type':'label','name':'max_page',':value':'max_page'},
                        ]
                        ,'width':0.7
                    },
                    {'type':'space'}
                ]
                ,'height':30
            },
            {'type':'space','height':5}
        ]
        return controls

    def makeLayoutDetail(self):
        detail = self.detail
        self.play_list = [{'name': name, 'url': url} for name, url in detail['src']]
        play_list_layout = {'type':'link','name':'name','@click':'onPlayClick'}
        controls = [
            {'type':'space','height':10},
            {'type':'link','name':'返回','@click':'onBackClick', 'fontSize':20, 'height': 20},
            {'type':'space','height':10},
            {'group':[
                    {'type':'image','name':'mediapicture', 'value':detail['cover'],'width':0.5},
                    {'type':'space','width':10},
                    {'group':[
                            {'type':'label','name':'medianame','textColor':'#ff7f00','fontSize':20,'value':detail['name'],'height':40},
                            {'type':'space','height':10},
                            {'type':'label','name':'info','textColor':'#005555','value':detail['summary'],'height':200,'vAlign':'top'},
                            {'type':'space','height':10},
                            {
                                'group': {'type':'grid','name':'play_list','itemlayout':play_list_layout,'value':self.play_list,'separator':True,'itemheight':30,'itemwidth':120},
                            }
                        ],
                        'dir':'vertical'
                    },
                    {'type':'space','width':10}
                ],
                'width':1.0
            },
            {'type':'space','height':10}
        ]
        return controls
        
    def show(self):
        self.doModal('main',800,750,'影片插件示例',self.makeLayout())

    def onSearch(self,*args):
        self.updateLayout('main', self.makeLayout())

    def onCategoryClick(self, pageId, control,*args):
        self.current_category = control.strip('[]')
        self.updateLayout('main', self.makeLayout())

    def onMovieClick(self, pageId, control, index, *args):
        self.detail = self.movies[index]
        self.updateLayout('main', self.makeLayout())

    def onBackClick(self, *args):
        self.detail = None
        self.updateLayout('main', self.makeLayout())

    def onPlayClick(self, page, listControl, index, itemControl):
        item = self.play_list[index]        
        try:
            self.player.play(item['url'], caption=f"{self.detail['name']} - {item['name']}")
        except:
            self.player.play(item['url'])

    def onClickFirstPage(self, *args):
        self.page = 1
        self.updateLayout('main', self.makeLayout())

    def onClickFormerPage(self, *args):
        if self.page > 1: self.page -= 1
        self.updateLayout('main', self.makeLayout())

    def onClickNextPage(self, *args):
        if self.page < self.page_count: self.page += 1
        self.updateLayout('main', self.makeLayout())

    def onClickLastPage(self, *args):
        self.page = self.page_count            
        self.updateLayout('main', self.makeLayout())
    
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = myplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
