# Liverpool Museum of Natural History (LMNH) Visitor Data Pipeline

<img src="https://images.liverpoolmuseums.org.uk/styles/focal_point_4_3/public/import-news-articles/World-Museum-large_0.jpg" style="width: 400px;" />

## Project Overview
The Liverpool Museum of Natural History (LMNH) is a leading cultural institution in Liverpool, attracting hundreds of thousands of visitors each year to award-winning exhibitions like "Fossils of the Ancient Nile" and "Inordinately Fond: Biodiversity in Beetles." With a mission to provide value to the community and enhance visitor experience, LMNH has launched a project to collect real-time feedback data using interactive kiosks placed at exhibition exits.

This project aims to build an end-to-end data pipeline that automates the collection, processing, storage, and visualization of visitor interaction data. By creating a live dashboard for museum staff, LMNH can track visitor satisfaction, monitor safety incidents, and make data-driven decisions on exhibition planning and visitor support.

## Project Goals
1. **Automate Data Collection**: Connect to a live data stream of visitor interactions from kiosks deployed at key exhibitions.
2. **Data Cleaning and Validation**: Process and clean raw interaction data to remove invalid records, ensuring that the stored data is accurate and relevant.
3. **Data Storage**: Design and implement a scalable cloud database to store both historical and real-time data.
4. **Data Analysis and Visualization**: Develop a Tableau dashboard that updates in real-time to present key insights on visitor satisfaction and support staff in decision-making.

## Stakeholders
- **Angela Millay (Exhibitions Manager)**: Seeks real-time insights into visitor engagement and satisfaction to optimize exhibition planning.
- **Rita Pelkman (Head of Security & Visitor Safety)**: Aims to use the data to identify areas needing visitor support and improve safety measures across the museum.

## Key Components
1. **ETL Pipeline**:
   - **Data Extraction**: Connect to an AWS S3 bucket for historical kiosk data (.csv and .json files) and a live Kafka data stream for real-time interaction data, **hosted on an EC2**.
   - **Data Transformation**: Clean and validate data to handle potential issues, including invalid interactions and data outside museum hours.
   - **Data Loading**: Store processed data in a remote cloud database (AWS RDS) designed to handle flexible updates and high availability.
   
2. **Data Validation Rules**:
   - Filter out interactions before 8:45 am and after 6:15 pm.
   - Discard interactions from non-project exhibits or with invalid button values.
   - Handle various data integrity issues arising from mechanical or human errors.

3. **Dashboard**:
   - Build a Tableau dashboard to visualize visitor feedback and safety data in real-time.
   - Track satisfaction levels across exhibitions and monitor assistance/emergency requests to enhance visitor experience and safety.

## Setup Instructions

### 1. Clone the Repository

```zsh
git clone <repository-url>
cd LMNH-Data-Pipeline
```

### 2. Create a Virtual Environment

Create a virtual environment to manage dependencies:

```zsh
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```zsh
pip3 install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the root directory with the following content:

```markdown
AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
AWS_REGION=<your-aws-region>
DATABASE_NAME=<your-database-name>
DATABASE_USERNAME=<your-database-username>
DATABASE_PASSWORD=<your-database-password>
DATABASE_IP=<your-database-ip>
DATABASE_PORT=<your-database-port>
```

Create a `.env.kafka` file in the root directory with the following content:

```markdown
BOOTSTRAP_SERVERS=<your-bootstrap-servers>
SECURITY_PROTOCOL=<your-security-protocol>
SASL_MECHANISM=<your-sasl-mechanism>
USERNAME=<your-username>
PASSWORD=<your-password>
```

### 5. Setup Terraform Variables

Create a `terraform.tfvars` file in the `terraform` directory with the following content:

```markdown
DATABASE_USERNAME=<your-database-username>
DATABASE_PASSWORD=<your-database-password>
KEY_NAME=<your-key-name>
```