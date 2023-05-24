# Store Activity Monitoring API

Demo and explaination video( 5 minutes): https://www.loom.com/share/30d1e06462fd4b6fb0993cb23fc9dd18

The Store Activity Monitoring System is designed to assist restaurant owners in tracking the online presence of their establishments during business hours. The system provides a report that indicates the frequency of any inactive periods experienced by the restaurants in the past. This application is built using FASTAPI and SQLAlchemy, offering efficient and reliable performance.

## Purpose
The primary purpose of this project is to address situations where a restaurant might unexpectedly go inactive for a few hours. Store owners want to have a report that shows how often these inactive periods have occurred in the past. By analyzing this data, owners can gain insights into the operational efficiency of their online presence and take appropriate measures to improve it.

## Features

### Endpoints

1) `/register_store`: This endpoint is used for registering a store with its business timings. The following information is required:
   - `store_id`: Unique identifier for the store.
   - `local_timezone`: Local timezone of the store (default: America/Chicago).
   - `dayOfWeek`: The day of the week (0 for Monday, 6 for Sunday).
   - `start_time_local`: Start time of business operations in the local timezone.
   - `end_time_local`: End time of business operations in the local timezone.

   Note: If data is missing for a particular day, it is assumed that the store is open 24/7.
   
   Example-
   
   ![image](https://github.com/Naveenlingala/Store_Monitoring_API/assets/60232407/b3e98b0a-de83-4f8e-a47c-5bc2875e9186)

2) `/poll`: A poll request is sent from the restaurant every hour to indicate its activity status. The following information is required:
   - `id`: Unique identifier for the store.
   - `utc_timestamp`: UTC timestamp of the poll request.
   - `status`: Status of the store (active or inactive).
    
   Example -
   
   ![image](https://github.com/Naveenlingala/Store_Monitoring_API/assets/60232407/6095fd20-d4f0-42ca-a119-a98118c82380)

3) `/trigger_report`: This endpoint triggers the generation of a CSV report for all registered stores. It responds with a report ID that can be used to download the CSV file.

    Example-
    
    ![image](https://github.com/Naveenlingala/Store_Monitoring_API/assets/60232407/fd3ac97f-a87b-4ed8-a433-704ac36c334f)

### CSV Report Format

4) `/get_report`: This endpoint receives a report ID and responds with the downloadable CSV file containing the requested report.

    CSV Example: ![image](https://github.com/Naveenlingala/Store_Monitoring_API/assets/60232407/39be8314-17e7-4a05-855d-3ef14562520a)
    The generated CSV report follows the format:
    ```
    store_id, uptime_last_hour (in minutes), uptime_last_day (in hours), uptime_last_week (in days and hours), downtime_last_hour (in minutes), downtime_last_day (in hours), downtime_last_week (in days and hours)
    ```

## Schema Design

To optimize time and memory usage, an efficient schema has been designed for storing and retrieving data. The schema employs a clever trick to overcome potential storage and query performance challenges. Instead of storing every poll request and querying from all stored data, the system only stores the latest poll request for each store. At each trigger_report or poll request, the relevant values for the current day and week are updated. If the current day or week has been completed, the previous and current values are exchanged.

This approach ensures that only the necessary data is stored and retrieved, resulting in improved efficiency and faster query performance.

Schema View:![image](https://github.com/Naveenlingala/Store_Monitoring_API/assets/60232407/81fc9ccb-9b14-4650-9b3c-4aea0b4a6528)

## Conclusion

The Store Activity Monitoring API provides an effective solution for restaurant owners to monitor and analyze the online presence of their establishments during business hours. By registering stores, receiving regular poll requests, and generating insightful reports, owners can identify any inactive periods and take appropriate actions to improve the online availability of their restaurants.

