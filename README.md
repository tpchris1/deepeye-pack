# deepeye_pack

## Description
1. This is a Python package for DeepEye API,can easily visualize data without too much effort. And provide with really simple usage
2. the DeepEye system: https://github.com/TsinghuaDatabaseGroup/DeepEye/tree/master/APIs_Deepeye

## Installation
1. Python 2.7
2. MySQL 5.7
3. Packages
    1. mysqldb binary packages for windows: link1:https://www.lfd.uci.edu/~gohlke/pythonlibs/ <br>link2:https://sourceforge.net/projects/mysql-python/
        - Download 'MySQL-python' and choose the right version for it 
        - Install the .whl by wheel install
        - there is a back up version in this repository under 'mysqldb' folder 
    2. numpy(latest version)
    3. pandas(latest version)

## Usage
1. Initial code
    ```py     
    import deepeye_pack as dp
    import MySQLdb # for from_mysql() function 
    
    dp = deepeye_pack.deepeye('demo')

    # this is where the table info should be input
    # as in table_info(table_name,column_names,column_types)
    dp.table_info('electricity',['city','date','electricity(kWh)'],['varchar','date','float'])
    ```
2. Import
    1. from_mysql()
        ```py
        # specify mysql parameter
        conn=MySQLdb.connect(host='localhost',port=3306,    user='root',passwd='ppww',db='deepeye',charset='utf8') 
        # import 
        dp.from_mysql(conn,'SELECT * FROM `electricity`')
        ```
    2. from_csv()
        ```py
        path = "elec.csv" # the path where the file located
        dp.from_csv(path)
        ```
3. Visualization
    ```py
    # choose one from three
    dp.learning_to_rank()
    dp.partial_order()
    dp.diversified_ranking()
    ```
4. Output
    ```py
    # can use several different methods at the same time
    dp.to_print_out()
    dp.to_single_json()
    dp.to_multiple_jsons()
    dp.to_multiple_htmls()
    dp.to_single_html()
    ```
