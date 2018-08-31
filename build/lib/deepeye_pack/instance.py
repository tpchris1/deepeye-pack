import os
from features import Type

class ViewPosition(object):
    def __init__(self,table_pos,view_pos):
        self.table_pos=table_pos
        self.view_pos=view_pos

class Instance(object):
    def __init__(self,table_name):
        self.table_name=table_name
        self.column_num=self.tuple_num=0 # the number of the column and row of the original data
        self.table_num=self.view_num=0
        self.tables=[]
        self.views=[]

    def addTable(self,table):
        self.tables.append(table)
        self.table_num+=1

    def addTables(self,tables):
        for table in tables:
            self.addTable(table)

    def getM(self):
        max_M=[0,0,0,0]
        for table in self.tables:
            for view in table.views:
                if view.M>max_M[view.chart]:
                    max_M[view.chart]=view.M
        for table in self.tables:
            for view in table.views:
                if max_M[view.chart]==0:
                    view.M=1
                else:
                    view.M=1.0*view.M/max_M[view.chart]
    
    def getW(self):
        '''weight=[0 for i in range(self.column_num)]
        for table in self.tables:
            for view in table.views:
                weight[view.fx.origin]+=1
                weight[view.fy.origin]+=1
                if view.z_id!=-1:
                    weight[view.z_id]+=1
        for i in range(self.column_num):
            weight[i]=1.0*weight[i]/self.view_num
        for table in self.tables:
            for view in table.views:
                view.W=weight[view.fx.origin]+weight[view.fy.origin]
                if view.z_id!=-1:
                    view.W+=weight[view.z_id]'''
        for table in self.tables:
            for view in table.views:
                if view.z_id==-1:
                    view.W=1.0/3*2
                else:
                    view.W=1.0
    
    def getScore_learning_to_rank(self):
        path=os.path.dirname(__file__)
        path2 = os.getcwd() + '\\data\\'
        # path2 = path + '\\data\\'
        if not os.path.exists(path2):
            os.mkdir(path2)
        # print os.path.exists(path2)
        f=open(path2+self.table_name+'.ltr','w')
        # f=open(path2+'\\data\\'+self.table_name+'.ltr','w')
        for i in range(self.table_num):
            self.views.extend([ViewPosition(i,view_pos) for view_pos in range(self.tables[i].view_num)])
        for i in range(self.table_num):
            for j in range(self.tables[i].view_num):
                view=self.tables[i].views[j]
                #print view
                f.write(view.output_score()+'\n')
        f.close()
        cmd='java -jar "'+path+'/jars/RankLib.jar" -load "'+path+'/jars/rank.model" -rank "'+ path2 + self.table_name+'.ltr" -score "'+ path2 + self.table_name+'.score"'
        # cmd='java -jar "'+path+'/jars/RankLib.jar" -load "'+path+'/jars/rank.model" -rank "'+ path +'/data/'+ self.table_name+'.ltr" -score "'+path+'/data/'+self.table_name+'.score"'
        os.popen(cmd)
        f=open(path2+self.table_name+'.score')
        i=0
        line=f.readline()
        while line:
            self.tables[self.views[i].table_pos].views[self.views[i].view_pos].score = float(line.split()[-1])
            line=f.readline()
            i += 1
        f.close()

        self.views.sort(key=lambda view:self.tables[view.table_pos].views[view.view_pos].score,reverse=True)

    def getScore(self):
        for i in range(self.table_num):
            self.views.extend([ViewPosition(i,view_pos) for view_pos in range(self.tables[i].view_num)])
        G=[[-1 for i in range(self.view_num)] for j in range(self.view_num)]
        out_edge_num=[0 for i in range(self.view_num)]
        score=[0 for i in range(self.view_num)]
        for i in range(self.view_num):
            for j in range(self.view_num):
                if i!=j:
                    view_i=self.tables[self.views[i].table_pos].views[self.views[i].view_pos]
                    view_j=self.tables[self.views[j].table_pos].views[self.views[j].view_pos]
                    if view_i.M >= view_j.M and view_i.Q >= view_j.Q and view_i.W >= view_j.W:
                        if view_i.M==view_j.M and view_i.Q==view_j.Q and view_i.W==view_j.W:
                            continue
                        G[i][j] = (view_i.M - view_j.M + view_i.Q - view_j.Q + view_i.W - view_j.W) / 3.0
                        out_edge_num[i] += 1
        for remove_time in range(self.view_num-1):
            for i in range(self.view_num):
                if out_edge_num[i]==0:
                    for j in range(self.view_num):
                        if G[j][i]>=0:
                            score[j]+=G[j][i]+score[i]
                            G[j][i]=-1
                            out_edge_num[i]=-1
                            out_edge_num[j]-=1
                    break
        for i in range(self.view_num):
            self.tables[self.views[i].table_pos].views[self.views[i].view_pos].score=score[i]
        self.views.sort(key=lambda view:self.tables[view.table_pos].views[view.view_pos].score,reverse=True)