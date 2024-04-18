#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import pandas as pd
import os
from google.cloud import storage
from google.cloud import bigquery
import datetime
import json
import settings


def fetch_api_data(url: str) -> dict:
  """Fetches data from the specified API URL and returns the JSON response.

  Args:
      url: The URL of the API endpoint.

  Returns:
      The JSON data parsed from the API response, or raises an exception on error.

  Raises:
      requests.exceptions.HTTPError: If the API request fails.
  """

  response = requests.get(url)
  response.raise_for_status()  # Raise exception for non-200 status codes

  return response.json()



def get_weather_data(locations: dict, api_key: str) -> dict:
  """ Fetches current and forecasted weather data for multiple locations.

  Args:
      locations (dict): A dictionary containing location information.
          Each key represents a location name, and the value is another dictionary
          with 'lat' and 'lon' keys for latitude and longitude.
      api_key (str): Your OpenWeatherMap API key.

  Returns:
      tuple: A tuple containing two dictionaries, one for current weather data
          keyed by location name, and another for forecasted weather data
          keyed by location name.

  Raises:
      requests.exceptions.RequestException: If an error occurs during API requests.
  """

  base_url = "https://api.openweathermap.org/data/2.5/"
  weather_data = {"current": {}, "forecast": {}}

  for location_name, location in locations.items():
    try:
      # Construct URLs with common base and location data
      current_url = f"{base_url}weather?lat={location['lat']}&lon={location['lon']}&appid={api_key}&units=metric"
      forecast_url = f"{base_url}forecast?lat={location['lat']}&lon={location['lon']}&appid={api_key}&units=metric"

      # Fetch and store data using a single function call
      weather_data["current"][location_name] = fetch_api_data(current_url)
      weather_data["forecast"][location_name] = fetch_api_data(forecast_url)
    except requests.exceptions.RequestException as e:
      print(f"Error fetching data for location {location_name}: {e}")

  return weather_data



def transform_current_weather_data(data_dict: dict) -> pd.DataFrame:
  """Transforms weather API data into a Pandas DataFrame suitable for BigQuery.

  Args:
      data_dict (dict): A dictionary containing weather data.
      is_current_weather (bool, optional): If True, assumes data represents
          current weather and selects the first element. Defaults to False.

  Returns:
      pd.DataFrame: A Pandas DataFrame containing the transformed weather data.
  """

  # Preprocess the 'weather' column (in some cases the API returns a list instead of a dictionary)
  if isinstance(data_dict['weather'], list):  # Check if 'weather' is a list and select the first element
    data_dict['weather'] = data_dict['weather'][0]

  # Flatten data structure
  flattened_data = {}
  for key, value in data_dict.items():
    if isinstance(value, dict):
      for sub_key, sub_value in value.items():
        flattened_data[f"{key}_{sub_key}"] = sub_value
    else:
      flattened_data[key] = value

  # Convert DataFrame and handle datetime if necessary
  data_df = pd.DataFrame([flattened_data])
  if 'dt' in data_df.columns:
    data_df['dt_txt'] = pd.to_datetime(data_df['dt'], unit='s')
    data_df['dt_txt'] = data_df['dt_txt'].dt.strftime('%Y-%m-%d %H:%M:%S')

  return data_df



def convert_weather_api_dict_to_dataframe(data_dict: dict) -> pd.DataFrame:
  """
  Converts a nested dictionary containing weather data from the Weather API to a Pandas DataFrame.

  Args:
      data_dict (dict): The dictionary containing the weather data.

  Returns:
      pd.DataFrame: A DataFrame representing the weather data.
  """

  extracted_data = {}
  for key, value in data_dict.items():
    if isinstance(value, dict):
      for sub_key, sub_value in value.items():
        extracted_data[f"{key}_{sub_key}"] = sub_value
    else:
      extracted_data[key] = value

  return pd.DataFrame([extracted_data])


def transform_forecasted_weather_data(data_dict: dict) -> pd.DataFrame:
  """
  Transforms the forecasted weather data from the Weather API into a Pandas DataFrame.

  Args:
      data_dict (dict): The dictionary containing the forecasted weather data.

  Returns:
      pd.DataFrame: A DataFrame containing the transformed forecasted weather data.
  """

  city_dict = data_dict['city']
  city_df = convert_weather_api_dict_to_dataframe(city_dict)

  forecasts_dict = data_dict['list']
  forecast_df = pd.DataFrame()
  for forecast_item in forecasts_dict:
    forecast_item['weather'] = forecast_item['weather'][0]
    forecast_item_df = convert_weather_api_dict_to_dataframe(forecast_item)
    forecast_df = pd.concat([forecast_df, forecast_item_df], ignore_index=True)

  return pd.concat([forecast_df, city_df], axis=1)


def upload_json_to_gcs(json_data: dict, bucket_name: str, folder_path: str) -> None:
  """Uploads a JSON object to Google Cloud Storage.

  Args:
      json_data (dict): The JSON data to upload.
      bucket_name (str): The name of the bucket to upload the data to.
      folder_path (str): The folder path within the bucket to store the data (optional).
  """
  
  # Read Google Application Credentials
  if settings.is_local_environment:
  	os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.cloud_storage_service_account


  client = storage.Client()

  # Create a new bucket if it doesn't exist
  try:
      bucket = client.get_bucket(bucket_name)
  except:       bucket = client.create_bucket(bucket_name)

  # Generate a timestamp for the filename
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

  # Define the file name with timestamp
  filename = f"{timestamp}.json"

  # Combine folder path and filename
  object_path = os.path.join(folder_path, filename)  # Using os.path.join for cleaner path handling

  # Convert JSON to bytes and upload
  blob = bucket.blob(object_path)
  blob.upload_from_string(json.dumps(json_data).encode("utf-8"), content_type="application/json")

  print(f"Uploaded {filename} to {bucket_name}/{object_path}")



def upload_df_to_bigquery(dataframe: pd.DataFrame, project_id: str, dataset_id: str, table_name: str):
    """Uploads a pandas DataFrame to a BigQuery table.
    
    Args:
        dataframe (pd.DataFrame): The pandas DataFrame to upload.
        project_id (str): Your GCP project ID.
        dataset_id (str): The ID of the BigQuery dataset where the table will be created.
        table_name (str): The name of the BigQuery table to create.
    
    Returns:
        None
    """
    # Read Google Application Credentials
    if settings.is_local_environment:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.bigquery_service_account
  
    # Construct a BigQuery client object.
    client = bigquery.Client()
    dataset_id = f"{project_id}.{dataset_id}"
    
    # Construct a full Dataset object to send to the API.
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "europe-west8" # Replace with your preferred location
    try:
       dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
       print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
    except:
        print("Dataset already exists")
    
    table_id = f"{dataset_id}.{table_name}"
    
    # Modify job_config for partitioning and truncating
    job_config = bigquery.LoadJobConfig(   
          autodetect=True,
          write_disposition= 'WRITE_APPEND', #'WRITE_TRUNCATE',
          create_disposition='CREATE_IF_NEEDED'#,
          #range_partitioning = bigquery.RangePartitioning(
          #    field="id", # [Important!] Partition by location id to store only the latest forecast for each location  
          #    range_=bigquery.PartitionRange(interval=1),
        #)
    )
          
    print("Created a BigQuery job_config variable")
    
    # Make an API request to store the data into BigQuery
    try:
        job = client.load_table_from_dataframe(dataframe, table_id, job_config=job_config)
        job.result()  # Wait for the job to complete.
        print("Saved data into BigQuery")
    except Exception as e:
        print(dataframe.dtypes)
        print(table_id)
        print(job_config)
        print(e)
        raise e


def main(request: dict) -> str:
    """
    This function retrieves weather data for specified locations, transforms it 
    into DataFrames for current and forecast weather. It then, uploads the raw JSON data 
    to Google Cloud Storage and the transformed data to BigQuery
    
    Args:
        request (json): A dictionary containing the body of the POST request that triggered the Cloud Function
    
    Returns:
        A string message "200, Success" indicating successful execution of the function
    """
    
    try:
        request_body = request.get_json()
    except:
        request_body = json.loads(request)
        
    # Replace with your actual API key (don't commit this with the key!)
    api_key = settings.api_key
    
    # Load location data with coordinates
    locations_dict = {
        'Thessaloniki, GR': {'lat': '40.6403', 'lon': '22.9439'},
        'Paris, FR': {'lat': '48.85341', 'lon': '2.3488'},
        'London, GB': {'lat': '51.50853', 'lon': '-0.12574'},
        'Dubai, AE': {'lat': '25.276987', 'lon': '55.296249'},
        'Los Angeles, US': {'lat': '34.0522', 'lon': '-118.2437'},
    }

    # Retrieve weather data for all locations
    weather_data = get_weather_data(locations_dict, api_key)

    # Initialize empty DataFrames for transformed data
    current_weather = pd.DataFrame()
    forecast_weather = pd.DataFrame()

    # Transform and concatenate current weather data
    for location, data in weather_data['current'].items():
        transformed_data = transform_current_weather_data(data)
        current_weather = pd.concat([current_weather, transformed_data], ignore_index=True)

    # Transform and concatenate forecasted weather data
    for location, data in weather_data['forecast'].items():
        transformed_data = transform_forecasted_weather_data(data)
        forecast_weather = pd.concat([forecast_weather, transformed_data], ignore_index=True)

    # Define bucket name for storing data
    bucket_name = "raw_weather_api_data"

    # Upload current weather data to GCS
    for location, data in weather_data['current'].items():
        folder_path = f"current_weather/{location}"
        upload_json_to_gcs(data, bucket_name, folder_path)

    # Upload forecasted weather data to GCS
    for location, data in weather_data['forecast'].items():
        folder_path = f"forecasted_weather/{location}"
        upload_json_to_gcs(data, bucket_name, folder_path)
       
    # Upload transformed data to BigQuery
    upload_df_to_bigquery(dataframe=current_weather, project_id=settings.project_id, dataset_id=settings.dataset_id, table_name = 'current_weather')
    upload_df_to_bigquery(dataframe=forecast_weather, project_id=settings.project_id, dataset_id=settings.dataset_id, table_name = 'forecasted_weather')


    return '200, Success'


if __name__ == "__main__":
    
    data = {}
    payload = json.dumps(data)
    print(main(payload))
