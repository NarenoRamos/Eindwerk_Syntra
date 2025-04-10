import os
import pandas as pd
import psycopg2
import numpy as np

def df_from_query(SQL_query):

    host=os.getenv('DB_HOST')
    dbname=os.getenv('POSTGRES_DB')
    user=os.getenv('POSTGRES_USER')
    password=os.getenv('POSTGRES_PASSWORD')
    port=os.getenv('DB_PORT')

    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port) 
    cur = conn.cursor()

    cur.execute(SQL_query)

    colnames = [desc[0] for desc in cur.description]

    data = cur.fetchall()

    cur.close()
    conn.close()

    df = pd.DataFrame(data, columns=colnames)    

    return df

def get_df_ring():
    df_ring = df_from_query(
        """ 
        SELECT ring_id, route 
        FROM ring
        """
    )

    df_edges = df_from_query(
        """ 
        SELECT 
        edge_id, 
        speed AS max_speed, 
        path 
        FROM edges
        """
    )

    df_ring = df_ring.explode("route")

    end_df = df_ring.merge(df_edges, how='left', left_on='route', right_on='edge_id')
    end_df = end_df.reset_index(drop=True)
    end_df = end_df.drop(columns=['edge_id'])
    end_df = end_df.rename(columns={'route_x': 'route_id', 'route_y': 'coordinates'})

    return end_df

def get_df_speed(vehicle_class):
    df = df_from_query(
    f"""
    SELECT  
        mp.matching_edge_id,
        AVG(md.snelheid_rek_{vehicle_class}) AS actual_speed
    FROM measurement_data AS md  
    LEFT JOIN measurement_points AS mp  
    ON mp.measurement_id = md.unieke_id  
    WHERE md.tijd_waarneming = (SELECT MAX(tijd_waarneming) FROM measurement_data) 
    AND md.snelheid_har_{vehicle_class} != 252
    GROUP BY matching_edge_id
    ;"""
    )

    return df

def get_df_speed_ontime(vehicle_class, date, hour):

    df = df_from_query(
        f"""
        SELECT  
            mp.matching_edge_id,  
            AVG(md.snelheid_rek_{vehicle_class}) AS actual_speed  
        FROM measurement_data AS md  
        LEFT JOIN measurement_points AS mp  
            ON mp.measurement_id = md.unieke_id  
        WHERE md.tijd_waarneming >= '{date} {hour}:00:00'  
        AND md.tijd_waarneming < '{date} {hour + 1}:00:00'
        AND md.snelheid_har_{vehicle_class} != 252
        GROUP BY mp.matching_edge_id;
        """
        )

    return df

def ring_with_speeds(vehicle_class, date, hour):
    df_ring = get_df_ring()
    if date == "":
        df_speeds = get_df_speed(vehicle_class)
    else:
        df_speeds = get_df_speed_ontime(vehicle_class, date, hour)

    df = df_ring.merge(df_speeds, how='left', left_on='route', right_on='matching_edge_id')
    
    del df['matching_edge_id']

    df['max_speed'] = df['max_speed'].astype(float)
    df['actual_speed'] = df['actual_speed'].astype(float)

    df['actual_speed'] = [
        df['actual_speed'].iloc[x] if pd.notna(df['actual_speed'].iloc[x]) 
        else (df['actual_speed'].iloc[x - 1] + df['actual_speed'].iloc[x + 1]) / 2 
        for x in range(len(df))
    ]

    df['speed_percentage'] = (df['actual_speed'] / df['max_speed'].replace(0, np.nan)) * 100

    bins = [0, 50, 80, 150] 
    labels = ['red', 'yellow', 'green']  

    df['speed_category'] = pd.cut(df['speed_percentage'], bins=bins, labels=labels, right=True)

    df['actual_speed'] = df['actual_speed'].apply(lambda x: str(int(round(x))))

    return df