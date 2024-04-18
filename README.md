# Weather API - ETL Data Pipeline on Google Cloud Platform

## Project Overview
This repository showcases my implementation of an end-to-end ETL pipeline, leveraging Google Cloud Platform (GCP) to manage and analyze weather data. This project emphasizes my capabilities in using cloud technologies and data engineering practices to handle real-world data workflows effectively.

## Project Architecture:
![image](https://github.com/michailchionidis/gcp-etl-pipeline/assets/104796421/f18a074d-e2d2-49e7-bd1f-a335b6f54229)

## Skills Demonstrated
- **API Interaction**: Automated data extraction from OpenWeather API.
- **Data Manipulation**: Utilized Python and Pandas to clean and transform data.
- **Cloud Services**: Deployed automated ETL workflows to extract, process, and store data on production using GCP services like Cloud Functions, Cloud Scheduler, BigQuery, and Cloud Storage.
- **Data Visualization**: Created an interactive dashboard using Looker Studio.

![image](https://github.com/michailchionidis/gcp-etl-pipeline/assets/104796421/0e3ec579-2ded-4067-8266-a08bb7de4ab5)


## Technologies Used
- Python 3.11, Pandas
- Google Cloud Platform (GCP)
- BigQuery, Google Cloud Storage, Cloud Functions, Cloud Scheduler
- Looker Studio

## Project Files
- `main.py`: Contains the full code for data extraction, transformation, and loading.
- `settings.py`: Used to configure API keys, GCP service account files, project ID, and dataset ID.
- `requirements.txt`: Lists all the dependencies necessary to run `main.py`.

## Setup and Installation
### Prerequisites
- An account with OpenWeather to access the WeatherAPI. [Find more here](https://dataprojectsio.notion.site/4-Account-Setup-Creating-an-OpenWeather-Account-3c996b5a1eb84f0bab282fdc103c9418)
- A free trial account on Google Cloud Platform to use cloud services. [Find more here](https://dataprojectsio.notion.site/7-Mini-Course-Google-Cloud-Platform-Fundamentals-dc6c8744b359483a84e02337ddf875fc)

### Configuration
1. **Clone the repository**
```git clone https://github.com/yourgithubusername/weather-data-etl-pipeline.git```

2. **Create a virtual environment**
```python3 -m venv venv```

3. **Activate your virtual environment**
```. venv/bin/activate```

4. **Install required Python libraries**
```pip install -r requirements.txt```

5. **Set up `settings.py`**
- Set your OpenWeather API Key.
- Configure service account files for Cloud Storage and BigQuery access. Instructions for setting up:
  - [Cloud Storage Service Account](https://dataprojectsio.notion.site/8-Mini-Course-Cloud-Storage-Fundamentals-504d51bd3fb940e2ba679a702a6a3809)
  - [BigQuery Service Account](https://dataprojectsio.notion.site/9-Mini-Course-BigQuery-Fundamentals-8f84175612fe4431a97bc5cfdec39947)
- Set your GCP project ID and dataset ID. Learn how to create a new GCP project [here](https://dataprojectsio.notion.site/7-Mini-Course-Google-Cloud-Platform-Fundamentals-dc6c8744b359483a84e02337ddf875fc).

### Running the Project
To execute the ETL pipeline, follow these steps:
1. **API Data Extraction**: Set up your API key and the service account files in `settings.py`.
2. **Data Transformation and Storage**: Run `main.py` to process the extracted data. You should have an active GCP account to store data in Cloud Storage and BigQuery
3. **Automation**: Deploy your script on Cloud Functions and create Cloud Scheduler job to fully automate and schedule the ETL process. [Find more information here](https://dataprojectsio.notion.site/12-Cloud-Deployment-Deploy-your-Python-script-as-a-Cloud-Function-for-automated-execution-72810f5f28334ef292bd6c5605136d79)

## Contributions
Contributions to this project are welcome! Please fork this repository and submit a pull request with your proposed changes.

## Acknowledgments
This project is provided by [DataProjects.io](https://dataprojects.io), a platform that helps data professionals build a portfolio of real-world, end-to-end projects on the cloud.

[You can find the complete project along with detailed instructions here!](https://dataprojectsio.notion.site/1-Real-World-Portfolio-Project-Build-an-End-to-End-ETL-Data-Pipeline-on-Google-Cloud-Platform-49e9b2abeec24dc4b98e9c68bfc7d503)

## License
This project is licensed under the Mozilla Public License 2.0 - see the [LICENSE](LICENSE) file for details.

