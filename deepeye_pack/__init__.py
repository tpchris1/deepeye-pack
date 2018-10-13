#coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb
import numpy as np
import pandas as pd
import datetime
from pprint import *
from pyecharts import Bar,Line,Scatter,Pie,Grid,Page

from instance import Instance
from table import Table
from table_l import Table as Table_LTR #table of Learning-to-rank model 
from view import Chart
from features import Type
from myGraph import myGraph # graph for building diversified ranking

methods_of_import =['none','mysql','csv']
methods_of_ranking =['none','learn_to_rank','partial_order','diversified_ranking']

class default(object):
    def __init__(self):
        return

class deepeye(object):
##### initial function
    def __init__(self,*name):
        if not name : self.name = 'deepeye'
        else : self.name = name
        self.is_table_info = False
        self.import_method = methods_of_import[0]
        self.rank_method = methods_of_ranking[0]
        # print name
    
    def table_info(self,name,column_info,*column_info2):
        """input table_info(must have)"""
        self.table_name=name
        self.column_names=[]
        self.column_types=[]
        if isinstance(column_info,list) and isinstance(column_info2[0],list):
            self.column_names = column_info
            self.column_types = column_info2[0]
        elif isinstance(column_info,dict):
            self.column_names = column_info.keys()
            self.column_types = column_info.values()
        elif isinstance(column_info,list) and isinstance(column_info[0],tuple):
            self.column_names = [i[0] for i in column_info]
            self.column_types = [i[1] for i in column_info]
        else:
            raise TypeError("unsupported argument types (%s, %s)" % (type(column_info), type(column_info2)))
        self.is_table_info = True
        return
    
    def error_throw(self,stage):
        """throw error before enter function"""
        if self.is_table_info == False:
            print "please enter table info by table_info()"
            sys.exit(0)
        
        if stage=='rank':
            if self.import_method =='none':
                im_methods_string = ''
                for i in range(len(methods_of_import)):
                    if i == 0:continue
                    elif i != len(methods_of_import)-1: im_methods_string += ('from_' + methods_of_import[i] + '() or ')
                    else: im_methods_string += ('from_' + methods_of_import[i] + '()')
                print "please import by " + im_methods_string
                sys.exit(0)
        elif stage=='output':
            if self.import_method =='none':
                im_methods_string = ''
                for i in range(len(methods_of_import)):
                    if i == 0:continue
                    elif i != len(methods_of_import)-1: im_methods_string += ('from_' + methods_of_import[i] + '() or ')
                    else: im_methods_string += ('from_' + methods_of_import[i] + '()')
                print "please import by " + im_methods_string
                sys.exit(0)
            else: 
                if self.rank_method == 'none':
                    rank_method_string = ''
                    for i in range(len(methods_of_ranking)):
                        if i == 0:continue
                        elif i != len(methods_of_ranking)-1: rank_method_string += (methods_of_ranking[i] + '() or ')
                        else: rank_method_string += (methods_of_ranking[i] + '()')
                    print "please rank first by " + rank_method_string
                    sys.exit(0)
        return


##### data import function
    def from_csv(self,path):
        """import from csv"""
        # if self.import_method != methods_of_import[0]:
        #     raise StandardError("already imported through %s" % self.import_method)
        self.error_throw('from')
        self.csv_path = path

        try:
            fh = open(self.csv_path, "r")
        except IOError:
            print "Error: no such file or directory"

        self.csv_dataframe = pd.DataFrame(pd.read_csv(self.csv_path,header=0))
        self.import_method = methods_of_import[2]
        return

    def csv_handle(self,instance):
        table_origin = self.csv_dataframe
        in_column_num = len(self.column_names) 
        in_column_name = self.column_names
        in_column_type = self.column_types

        instance.column_num = instance.tables[0].column_num = in_column_num
        for i in range(instance.column_num):
            instance.tables[0].names.append(in_column_name[i])
            instance.tables[0].types.append(Type.getType(in_column_type[i].lower()))
        instance.tables[0].origins=[i for i in range(instance.tables[0].column_num)]
        
        instance.tuple_num = instance.tables[0].tuple_num = table_origin.shape[0]
        for i in range(instance.tables[0].column_num):
            if instance.tables[0].types[i] == 3: #if there is date type column in csv,convert into datetime format
                col_name = table_origin.columns[i]
                col_type = self.column_types[i]
                self.csv_handle_changedate(col_name,col_type)
        
        #change table column name with table_info column_names
        for i in range(len(table_origin.columns)): table_origin.rename(columns={ table_origin.columns[i] : in_column_name[i] }, inplace=True) 
        instance.tables[0].D = table_origin.values.tolist()
        return instance

    def csv_handle_changedate(self,col_name,col_type):
        """deal with date type data, wrap to datetime format"""
        table = self.csv_dataframe
        if col_type == 'date':
            table[col_name] = pd.to_datetime(table[col_name]).dt.date
        elif col_type == 'datetime':
            table[col_name] = pd.to_datetime(table[col_name]).dt.to_pydatetime()
        elif col_type == 'year':
            table[col_name] = pd.to_datetime(table[col_name].apply(lambda x: str(x)+'/1/1')).dt.date
        return
            
                
    '''
    def csv_handle_changedate(self,col_name,col_type):
        """version 0.1 changedate through personal handle"""
        table = self.csv_dataframe
        if col_type == 'date':
            col = []
            for i in table[col_name]:
                if isinstance(i,str):
                    if i.find('/') >= 0: splitflag = '/'
                    elif i.find('-') >=0: splitflag = '-'
                    else: print "wrong date type of"+col_name+"in"+self.table_name; sys.exit(0); 

                temp = i.split(splitflag)
                res = datetime.date(int(temp[0]),int(temp[1]),int(temp[2]))
                # print res
                col.append(res)
            col2 = pd.DataFrame({col_name:col})
            table.update(col2)
            return
        elif col_type == 'datetime':
            return
        elif col_type == 'year':
            col = []
            for i in table[col_name]:
                res = datetime.date(int(i),1,1)
                col.append(res)
            # print col # DEBUG
            col2 = pd.DataFrame({col_name:col})
            table.update(col2)
            return
        '''
    
    def show_csv_info(self):
        """print out csv info"""
        self.csv_dataframe
        return

    '''
    def from_mysql(self,conn,mysql_select_query,*mysql_table_name):
        
        return
    '''
    
    
    def from_mysql(self,conn,mysql_select_query,*mysql_table_name):
        """import from mysql"""
        # self.error_throw('from')
        # if self.import_method != methods_of_import[0]:
        #     raise StandardError("already imported through %s" % self.import_method)

        self.mysql_conn = conn
        self.mysql_query_showTable = mysql_select_query

        if mysql_table_name: 
            self.mysql_table_name = mysql_table_name
            self.mysql_query_showInfo = 'describe' + ' ' + mysql_table_name
        elif 'table_name' in self.__dict__:
            self.mysql_table_name = self.table_name
            self.mysql_query_showInfo = 'describe' + ' ' + self.table_name
        else:
            self.mysql_table_name = self.mysql_query_showTable.split('`')[1]
            self.mysql_query_showInfo = 'describe' + ' ' + self.mysql_table_name
            print 'extract table name,column names and column types from mysql query since no table_info is given' + self.mysql_table_name
        self.import_method = methods_of_import[1]
        return

    def mysql_handle(self,instance):
        """mysql data handle function"""
        cur=self.mysql_conn.cursor()

        instance.column_num = instance.tables[0].column_num = cur.execute(self.mysql_query_showInfo)
        mysql_table_description = map(list,cur.fetchall())

        c_name_list=[]
        t_name_list=[]
        for i in mysql_table_description: 
            c_name = i[0].encode('ascii','ignore')
            t_name = i[1].encode('ascii','ignore')
            c_name_list.append(c_name)
            t_name_list.append(t_name)
            instance.tables[0].names.append(c_name)
            instance.tables[0].types.append(Type.getType(t_name.lower()))
        if self.is_table_info == False:
            self.column_names = c_name_list
            self.column_types = t_name_list

        instance.tables[0].origins=[i for i in range(instance.tables[0].column_num)]
        instance.tuple_num=instance.tables[0].tuple_num=cur.execute(self.mysql_query_showTable)
        instance.tables[0].D=map(list,cur.fetchall())
        # print self.column_types
        for idx,val in enumerate(self.column_types):
            if val[0:4] == 'year':
                # print idx,val
                # print instance.tables[0].D[0]
                for row in instance.tables[0].D:
                    row[idx] = datetime.date(row[idx],1,1)
        # print instance.tables[0].D[0] # DEBUG
        cur.close()
        self.mysql_conn.close()
        return instance

    def show_mysql_info(self):
        """print out mysql info"""
        print self.mysql_conn
        print self.mysql_table_name
        print self.mysql_query_showInfo
        print self.mysql_query_showTable
        return
    


##### ranking function
    def rank_generate_all_views(self,instance):
        if len(instance.tables[0].D)==0:
            print 'no data in table'
            sys.exit(0)
        instance.addTables(instance.tables[0].dealWithTable()) # the first deal with is to transform the table into several small ones
        begin_id=1
        while begin_id<instance.table_num:
            instance.tables[begin_id].dealWithTable()
            begin_id+=1
        if instance.view_num==0:
            print 'no chart generated'
            sys.exit(0)
        return instance

    def learning_to_rank(self):
        """use Learn_to_rank method to rank the charts"""
        self.error_throw('rank')

        instance=Instance(self.table_name)            
        instance.addTable(Table_LTR(instance,False,'',''))
        if self.import_method == 'mysql': instance = self.mysql_handle(instance)
        elif self.import_method == 'csv': instance = self.csv_handle(instance)

        instance=self.rank_generate_all_views(instance)
        instance.getScore_learning_to_rank()

        self.instance = instance
        self.rank_method = methods_of_ranking[1]
        return
    
    def partial_order(self):
        """use partial order method to rank the charts"""
        self.error_throw('rank')
        instance=Instance(self.table_name)
        instance.addTable(Table(instance,False,'','')) # 'False'->transformed '',''->no describe yet
        if self.import_method == 'mysql': instance = self.mysql_handle(instance)
        elif self.import_method == 'csv': instance = self.csv_handle(instance)
        
        instance=self.rank_generate_all_views(instance)
        instance.getM()
        instance.getW()
        instance.getScore()

        self.instance = instance
        self.rank_method = methods_of_ranking[2]
        return
    
    def diversified_ranking(self):
        """use diversified ranking method to rank the charts"""
        self.error_throw('rank')
        instance=Instance(self.table_name)
        instance.addTable(Table(instance,False,'','')) # 'False'->transformed '',''->no describe yet
        if self.import_method == 'mysql': instance = self.mysql_handle(instance)
        elif self.import_method == 'csv': instance = self.csv_handle(instance)

        instance=self.rank_generate_all_views(instance)
        instance.getM()
        instance.getW()
        instance.getScore()

        self.instance = instance
        self.rank_method = methods_of_ranking[3]
        return


##### output function
    def to_list(self):
        """export as list type"""
        self.error_throw('output')

        instance = self.instance
        export_list=[]
        if self.rank_method == methods_of_ranking[3]:
            G=myGraph(instance.view_num)
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                G.addNode(view)
            G.getSim()
            result=G.getTopK(instance.view_num)
            order=1
            for item in result:
                export_list.append(G.nodes[item].output(order))
                order+=1
        else:
            order1=order2=1
            old_view=''
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                if old_view:
                    order2 = 1
                    order1 += 1
                export_list.append(view.output(order1))
                old_view = view
        return export_list
    def to_print_out(self):
        """print out to cmd"""
        self.error_throw('output')

        instance = self.instance
        if self.rank_method == methods_of_ranking[3]:
            G=myGraph(instance.view_num)
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                G.addNode(view)
            G.getSim()
            result=G.getTopK(instance.view_num)
            order=1
            for item in result:
                print G.nodes[item].output(order)
                order+=1
        else:
            order1=order2=1
            old_view=''
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                if old_view:
                    order2 = 1
                    order1 += 1
                print view.output(order1)
                old_view = view
        return
    
    def to_single_json(self):
        """create a single json file"""
        self.error_throw('output')
        
        path2 = os.getcwd() + '\\json\\'
        if not os.path.exists(path2):
            os.mkdir(path2)
        f=open(path2+self.table_name+'.json','w')

        instance = self.instance

        if self.rank_method == methods_of_ranking[3]:
            G=myGraph(instance.view_num)
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                G.addNode(view)
            G.getSim()
            result=G.getTopK(instance.view_num)
            order=1
            for item in result:
                f.write(G.nodes[item].output(order)+'\n')
                order+=1
            f.close()
        else:
            order1=order2=1
            old_view=''
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                if old_view:
                    order2 = 1
                    order1 += 1
                f.write(view.output(order1)+'\n')
                old_view = view
            f.close()
        return

    
    def to_multiple_jsons(self):
        """create multiple json files"""
        self.error_throw('output')

        path2 = os.getcwd() + '\\json\\'
        if not os.path.exists(path2):
            os.mkdir(path2)

        instance = self.instance
        if self.rank_method == methods_of_ranking[3]:
            G=myGraph(instance.view_num)
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                G.addNode(view)
            G.getSim()
            result=G.getTopK(instance.view_num)
            order=1
            for item in result:
                f=open(path2+self.table_name+str(order)+'.json','w')
                f.write(G.nodes[item].output(order))
                order+=1
            f.close()
        else:
            order1=order2=1
            old_view=''
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                if old_view:
                    order2 = 1
                    order1 += 1
                f=open(path2+self.table_name+str(order1)+'.json','w')
                f.write(view.output(order1))
                f.close()
                old_view = view
        return

    
    def html_handle(self,data):
        """convert function to html by pyecharts"""
        zoommax = sys.maxint
        zoommin = -sys.maxint-1
        filename = self.table_name + str(data['order']) + '.html'
        margin = str(data['title_top']) + '%'

        if data['chart'] == 'bar':
            chart = Bar(data['chartname'],data['describe'],title_pos="center",title_top=margin)
        elif data['chart'] == 'pie': 
            chart = Pie(data['chartname'],data['describe'],title_pos="center",title_top=margin)
        elif data['chart'] == 'line': 
            chart = Line(data['chartname'],data['describe'],title_pos="center",title_top=margin)
        elif data['chart'] == 'scatter': 
            chart = Scatter(data['chartname'],data['describe'],title_pos="center",title_top=margin)
        else :
            print "not valid chart"

        if not data["classify"] :
            attr = data["x_data"][0]
            val = data["y_data"][0]
            if data['chart'] == 'bar':       chart.add("",attr,val,xaxis_name=data["x_name"],yaxis_name=data["y_name"],yaxis_name_pos="end",is_datazoom_show=True,datazoom_range=[zoommin,zoommax],is_datazoom_extra_show=True,datazoom_extra_type="slider",datazoom_extra_range=[zoommin,zoommax])
            elif data['chart'] == 'line':    chart.add("",attr,val,xaxis_name=data["x_name"],yaxis_name=data["y_name"],yaxis_name_pos="end",is_datazoom_show=True,datazoom_range=[zoommin,zoommax],is_datazoom_extra_show=True,datazoom_extra_type="slider",datazoom_extra_range=[zoommin,zoommax])
            elif data['chart'] == 'pie':     chart.add("",attr,val,is_label_show=True)
            elif data['chart'] == 'scatter': chart.add("",attr,val,xaxis_name=data["x_name"],yaxis_name=data["y_name"],yaxis_name_pos="end",is_datazoom_show=True,datazoom_range=[zoommin,zoommax],is_datazoom_extra_show=True,datazoom_extra_type="slider",datazoom_extra_range=[zoommin,zoommax])
        else :
            attr = data["x_data"][0]
            for i in range(len(data["classify"])) :
                val = data["y_data"][i]
                name = (data["classify"][i][0] if type(data["classify"][i]) == type(('a','b')) else data["classify"][i])
                if data['chart'] == 'bar': chart.add(name,attr,val,xaxis_name=data["x_name"],yaxis_name=data["y_name"],yaxis_name_pos="end",is_stack=True,is_datazoom_show=True,datazoom_range=[zoommin,zoommax],is_datazoom_extra_show=False,datazoom_extra_type="slider",datazoom_extra_range=[zoommin,zoommax])
                elif data['chart'] == 'line': chart.add(name,attr,val,xaxis_name=data["x_name"],yaxis_name=data["y_name"],yaxis_name_pos="end",is_datazoom_show=True,datazoom_range=[zoommin,zoommax],is_datazoom_extra_show=True,datazoom_extra_type="slider",datazoom_extra_range=[zoommin,zoommax])
                elif data['chart'] == 'pie': chart.add(name,attr,val,is_label_show=True)
                elif data['chart'] == 'scatter': 
                    attr_scatter = data["x_data"][i]
                    chart.add(name,attr_scatter,val,xaxis_name=data["x_name"],yaxis_name=data["y_name"],yaxis_name_pos="end",is_datazoom_show=True,datazoom_range=[zoommin,zoommax],is_datazoom_extra_show=True,datazoom_extra_type="slider",datazoom_extra_range=[zoommin,zoommax])
        # chart.render(filename)
        return chart,filename
        
    def to_single_html(self): #size problem
        """convert to html by pyecharts and output to multiple html files"""
        self.error_throw('output')

        instance = self.instance

        path2 = os.getcwd() + '\\html\\'
        if not os.path.exists(path2):
            os.mkdir(path2)

        page = Page()
        
        if self.rank_method == methods_of_ranking[3]:
            G=myGraph(instance.view_num)
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                G.addNode(view)
            G.getSim()
            result=G.getTopK(instance.view_num)
            order=1
            for item in result:
                view = G.nodes[item]
                data={}
                data['order'] = order
                data['chartname'] = instance.table_name
                data['describe'] = view.table.describe
                data['x_name'] = view.fx.name
                data['y_name'] = view.fy.name
                data['chart'] = Chart.chart[view.chart]
                data['classify'] = [v[0] for v in view.table.classes]
                data['x_data'] = view.X
                data['y_data'] = view.Y
                data['title_top'] = 5
                order+=1
                # print data,'\n'

                [chart,filename] = self.html_handle(data)
                grid = Grid()
                grid.add(chart,grid_top='20%',grid_bottom='20%')
                page.add(grid)
        else:
            order1=order2=1
            old_view=''
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                if old_view:
                    order2 = 1
                    order1 += 1
                old_view = view
                
                data={}
                data['order'] = order1
                data['chartname'] = instance.table_name
                data['describe'] = view.table.describe
                data['x_name'] = view.fx.name
                data['y_name'] = view.fy.name
                data['chart'] = Chart.chart[view.chart]
                data['classify'] = [v[0] for v in view.table.classes]
                data['x_data'] = view.X
                data['y_data'] = view.Y
                data['title_top'] = 5

                [chart,filename] = self.html_handle(data)
                grid = Grid()
                grid.add(chart,grid_top='20%',grid_bottom='20%')
                page.add(grid)
                # print data
        page.render('./html/'+self.table_name+'_all'+'.html')
        return
    
    def to_multiple_htmls(self):
        """convert to html by pyecharts and output to multiple html files"""
        self.error_throw('output')

        path2 = os.getcwd() + '\\html\\'
        if not os.path.exists(path2):
            os.mkdir(path2)

        instance = self.instance
        
        if self.rank_method == methods_of_ranking[3]:
            G=myGraph(instance.view_num)
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                G.addNode(view)
            G.getSim()
            result=G.getTopK(instance.view_num)
            order=1
            for item in result:
                view = G.nodes[item]
                data={}
                data['order'] = order
                data['chartname'] = instance.table_name
                data['describe'] = view.table.describe
                data['x_name'] = view.fx.name
                data['y_name'] = view.fy.name
                data['chart'] = Chart.chart[view.chart]
                data['classify'] = [v[0] for v in view.table.classes]
                data['x_data'] = view.X
                data['y_data'] = view.Y
                data['title_top'] = 5
                order+=1
                # print data,'\n'

                [chart,filename] = self.html_handle(data)
                grid = Grid()
                grid.add(chart,grid_top='20%',grid_bottom='20%')
                grid.render('./html/'+filename)
        else:
            order1=order2=1
            old_view=''
            for i in range(instance.view_num):
                view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
                if old_view:
                    order2 = 1
                    order1 += 1
                old_view = view

                data={}
                data['order'] = order1
                data['chartname'] = instance.table_name
                data['describe'] = view.table.describe
                data['x_name'] = view.fx.name
                data['y_name'] = view.fy.name
                data['chart'] = Chart.chart[view.chart]
                data['classify'] = [v[0] for v in view.table.classes]
                data['x_data'] = view.X
                data['y_data'] = view.Y
                data['title_top'] = 5
    
                [chart,filename] = self.html_handle(data)
                grid = Grid()
                grid.add(chart,grid_top='20%',grid_bottom='20%')
                grid.render('./html/'+filename)
                # print data
        return
    