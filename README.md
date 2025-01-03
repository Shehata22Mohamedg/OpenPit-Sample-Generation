# Flask QAQC Sample Generator

This Flask application processes an uploaded Excel file containing QAQC sample data and generates interval samples, STD/GBLANK samples, and a comprehensive list of all samples based on user-defined depth increments. The results are saved as CSV files, which can be downloaded.

## Features

- Upload an Excel file with sample data.
- Generate samples based on depth increments and merge rules.
- Output CSV files for:
  - All generated samples.
  - STD/GBLANK samples.
  - Other interval samples.
- Download the generated CSV files from the web interface.

## Prerequisites

- Python 3.x
- Flask
- pandas
- openpyxl

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies using `pip`:

   ```bash
   pip install flask pandas openpyxl
