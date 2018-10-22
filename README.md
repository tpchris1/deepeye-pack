# deepeye_pack

## Update - 2018/10/22 v0.0.2
1. read_csv_handld_changedate revise to pandas method
2. both the import methods require **Mandatory** table_info to specify the table 
3. mysql_handle now change to pandas dataframe verison
4. from_mysql also changes to para-method, pass port/user/db... instead of query and MySQLdb conn


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
    3. pandas(latest version) above ver 0.23.0

## Usage
1. Initial
    1. example code:
    ```py
    import deepeye_pack
    
    #create a deepeye_pack class that wraps everything
    dp = deepeye_pack.deepeye('demo') # the name here doesnt actually matter

    # then user needs to input table info
    # as in table_info(table_name,column_names,column_types)
    dp.table_info('electricity',['city','date','electricity(kWh)'],['varchar','date','float'])
    ```
    2. the column_types that supported by deepeye_pack are specified as below:
        1. numerical: `int`, `float`, `double`
        2. temporal: `date`, `datetime`, `year`
        3. categorical: `char`, `varchar`
2. Import
    1. from_mysql()
        ```py
        # call the from_mysql() function
        dp.from_mysql(host='localhost',port=3306,user='root',passwd='ppww',db='deepeye', query='SELECT * FROM `table_name`')

        ```
    2. from_csv()
        ```py
        path = "file.csv" # the path where the file located
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
