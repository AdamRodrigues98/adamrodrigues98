select tab.table_schema as database_name,
       tab.table_name
from information_schema.tables tab
left join information_schema.table_constraints tco
          on tab.table_schema = tco.table_schema
          and tab.table_name = tco.table_name
          and tco.constraint_type = 'PRIMARY KEY'
where tco.constraint_type is null
      and tab.table_schema not in('mysql', 'information_schema', 
                                  'performance_schema', 'sys')
      and tab.table_type = 'BASE TABLE'
--      and tab.table_schema = 'sakila' -- put schema name here
order by tab.table_schema,
         tab.table_name;
            